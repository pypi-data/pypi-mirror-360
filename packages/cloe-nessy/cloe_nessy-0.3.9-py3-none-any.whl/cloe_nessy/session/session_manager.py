import json
import os
from enum import Enum
from typing import Any

from pyspark.sql import SparkSession


class SessionManager:
    """SessionManager is a singleton class that manages the SparkSession instance."""

    class Environment(Enum):
        """Enumeration of execution environments for Spark utilities.

        This Enum defines the different environments in which the Spark session
        can operate, including:
            - DATABRICKS_UI: Represents the Databricks user interface.
            - FABRIC_UI: Represents the Fabric user interface.
            - DATABRICKS_CONNECT: Represents the Databricks Connect environment.
            - OTHER_REMOTE_SPARK: Represents other remote Spark environments, such as used in tests.
            - STANDALONE_SPARK: Represents a standalone Spark cluster environment.
        """

        DATABRICKS_UI = "databricks_ui"
        FABRIC_UI = "fabric_ui"
        DATABRICKS_CONNECT = "databricks_connect"
        OTHER_REMOTE_SPARK = "other_remote_spark"
        STANDALONE_SPARK = "standalone_spark"

    _spark: SparkSession | None = None
    _utils = None
    _env: Environment | None = None

    @classmethod
    def get_spark_session(cls, config: dict[str, str] | None = None, profile_name: str = "DEFAULT") -> SparkSession:
        """Creates or retrieves an existing SparkSession.

        This method initializes a SparkSession based on the provided
        configuration and profile name. If a SparkSession already exists,
        it returns that instance; otherwise, it creates a new one.

        Args:
            config: An optional Spark configuration
                provided as key-value pairs.
            profile_name: The name of the Databricks profile to use.
                Defaults to "DEFAULT".

        Returns:
            An instance of SparkSession for data processing.
        """
        if cls._spark is not None:
            return cls._spark

        if cls._env is None:
            cls._detect_env()

        builder = cls.get_spark_builder()

        # Check if NESSY_SPARK_CONFIG environment variable is set and load it as config
        nessy_spark_config = os.getenv("NESSY_SPARK_CONFIG")
        if nessy_spark_config:
            try:
                # Parse the JSON configuration from the environment variable
                config = json.loads(nessy_spark_config)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in NESSY_SPARK_CONFIG: {e}") from e

        if config:
            for key, value in config.items():
                builder.config(key, value)  # type: ignore

        cls._spark = builder.getOrCreate()

        return cls._spark

    @classmethod
    def get_utils(
        cls,
    ) -> Any:  # return type should be Union[DBUtils, MsSparkUtils, RemoteDbUtils].
        """Get or create a DBUtils, RemoteDbUtils or MsSparkUtils instance, depending on the context.

        In Databricks this will return DBUtils, when using Databricks-Connect it returns RemoteDbUtils, and in Fabric it will return MsSparkUtils.

        Returns:
            utils: The DBUtils, RemoteDbUtils or MsSparkUtils instance.

        Raises:
            RuntimeError: If the instance cannot be created.
        """
        if cls._utils is not None:
            return cls._utils

        if cls._env is None:
            cls._detect_env()

        utils_function = {
            cls.Environment.DATABRICKS_UI: cls._get_dbutils,
            cls.Environment.DATABRICKS_CONNECT: cls._get_dbutils,
            cls.Environment.OTHER_REMOTE_SPARK: cls._get_dbutils,
            cls.Environment.STANDALONE_SPARK: cls._get_localsparkutils,
            cls.Environment.FABRIC_UI: cls._get_mssparkutils,
        }

        try:
            cls._utils = utils_function[cls._env]()  # type: ignore
        except Exception as e:
            raise RuntimeError(f"Cannot create utils instance. Error: {e}") from e

        return cls._utils

    @classmethod
    def _get_dbutils(cls):
        if cls._env == cls.Environment.DATABRICKS_CONNECT:
            from databricks.sdk import WorkspaceClient

            return WorkspaceClient().dbutils

        from pyspark.dbutils import DBUtils

        cls.get_spark_session()
        return DBUtils(cls._spark)

    @classmethod
    def _get_mssparkutils(cls):
        from notebookutils import mssparkutils  # type: ignore

        cls._utils = mssparkutils

    @classmethod
    def _get_localsparkutils(cls):
        return None

    @classmethod
    def _detect_env(cls) -> Environment | None:
        """Detects the current execution environment for Spark.

        This class method attempts to import the necessary modules to determine
        whether the code is running in a Databricks UI, Fabric UI, or using
        Databricks Connect. It sets the class variable `_env` accordingly.

        The detection process involves checking the type of `dbutils` to identify
        the environment. If the environment is already detected, it returns the
        cached value.

        Returns:
            Environment: An enum value indicating the detected environment

        Raises:
            RuntimeError: If the environment cannot be detected due to
            import errors or other exceptions.
        """
        if cls._env is not None:
            return cls._env

        try:
            from databricks.sdk.dbutils import RemoteDbUtils  # type: ignore

            if isinstance(dbutils, RemoteDbUtils):  # type: ignore [name-defined]
                cls._env = cls.Environment.DATABRICKS_CONNECT
                return cls._env
        except (ImportError, NameError):
            pass

        try:
            from notebookutils import mssparkutils  # type: ignore # noqa: F401

            cls._env = cls.Environment.FABRIC_UI
            return cls._env
        except ImportError:
            pass

        try:
            from dbruntime.dbutils import DBUtils  # type: ignore [import-not-found]  # noqa: F401

            cls._env = cls.Environment.DATABRICKS_UI
            return cls._env
        except ImportError:
            pass

        try:
            from pyspark.sql.connect.session import (
                SparkSession as RemoteSparkSession,  # type: ignore [import-not-found]  # noqa: F401
            )

            cls._env = cls.Environment.OTHER_REMOTE_SPARK
            return cls._env
        except ImportError:
            pass

        try:
            from pyspark.sql import SparkSession  # noqa: F401

            cls._env = cls.Environment.STANDALONE_SPARK
            return cls._env
        except ImportError:
            pass

        raise RuntimeError("Cannot detect environment.")

    @classmethod
    def get_spark_builder(cls):
        """Get the SparkSession builder based on the current environment."""
        cls._detect_env()
        builders = {
            cls.Environment.DATABRICKS_UI: SparkSession.builder,
            cls.Environment.FABRIC_UI: SparkSession.builder,
            cls.Environment.DATABRICKS_CONNECT: cls._get_databricks_connect_builder,
            cls.Environment.OTHER_REMOTE_SPARK: cls._get_databricks_connect_builder,
            cls.Environment.STANDALONE_SPARK: SparkSession.builder,
        }
        builder = builders.get(cls._env)
        if builder is None:
            raise ValueError(f"Unsupported environment: {cls._env}")

        match cls._env:
            case cls.Environment.DATABRICKS_CONNECT | cls.Environment.OTHER_REMOTE_SPARK:
                return builder()
            case _:
                return builder

    @staticmethod
    def _get_databricks_connect_builder():
        from databricks.connect import DatabricksSession

        return DatabricksSession.builder
