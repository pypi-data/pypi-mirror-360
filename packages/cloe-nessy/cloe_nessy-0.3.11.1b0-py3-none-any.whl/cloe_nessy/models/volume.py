from pathlib import Path
from typing import Any

from jinja2 import TemplateNotFound
from pydantic import BaseModel, field_validator

try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files  # Python < 3.9 fallback

from ..logging import LoggerMixin
from .mixins.template_loader_mixin import TemplateLoaderMixin


class Volume(TemplateLoaderMixin, LoggerMixin, BaseModel):
    """Volume class for managing volumes."""

    identifier: str
    storage_path: str | Path
    comment: str | None = None

    @field_validator("identifier")
    def check_identifier(cls, value):
        """Check the identifier."""
        if value.count(".") != 2:
            raise ValueError("The identifier must be in the format 'catalog.schema.volume_name'.")
        return value

    @property
    def storage_identifier(self) -> str:
        """Return the storage identifier."""
        return f"/Volumes/{self.catalog}/{self.schema}/{self.name}/"

    @property
    def catalog(self) -> str:
        """Return the catalog name."""
        return self.identifier.split(".")[0]

    @property
    def schema_name(self) -> str:
        """Return the schema name."""
        return self.identifier.split(".")[1]

    @property
    def name(self) -> str:
        """Return the table name."""
        return self.identifier.split(".")[2]

    @property
    def escaped_identifier(self) -> str:
        """Return the escaped identifier."""
        return f"`{self.catalog}`.`{self.schema_name}`.`{self.name}`"

    def model_post_init(self, __context: Any) -> None:
        """Post init method for the Table model."""
        self._console_logger = self.get_console_logger()
        self._console_logger.debug(f"Model for volume [ '{self.identifier}' ] has been initialized.")

    def get_create_statement(
        self,
        if_not_exists: bool = True,
    ):
        """Get the create statement for the Volume.

        Args:
            if_not_exists: Whether to include the IF NOT EXISTS clause in the create statement

        Returns:
                The rendered create statement as a string.
        """
        # Use importlib.resources for robust template loading
        try:
            template_files = files("cloe_nessy.models") / "templates"
            template_content = (template_files / "create_volume.sql.j2").read_text()

            # Create template directly from string content
            from jinja2 import BaseLoader, Environment

            env = Environment(loader=BaseLoader(), keep_trailing_newline=True)
            template = env.from_string(template_content)

        except (FileNotFoundError, AttributeError):
            # Fallback to the old method if importlib.resources fails
            template_name = "create_volume.sql.j2"
            templates = Path(__file__).parent / "templates"
            try:
                template = self.get_template(templates, template_name)
            except TemplateNotFound as template_err:
                self._console_logger.error(f"Template [ {template_name} ] not found.")
                raise template_err

        render = template.render(volume=self, if_not_exists=if_not_exists)
        return render
