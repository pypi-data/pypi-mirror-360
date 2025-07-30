from enum import Enum

from pydantic import BaseModel, Field

from .. import enums
from . import ToolOutput


class FieldFormat(str, Enum):
    COMMA_SEPARATED_LIST = "comma-separated-list"
    JINJA_TEMPLATE = "jinja-template"
    DEFAULT = "default"


# TODO: this tool probably needs to be replaced by something that reads only a single
# datasource at a time, or takes in a list of datasource IDs.
class ReadDatasourcesInput(BaseModel):
    datasource_ids: str = Field(
        default="",
        json_schema_extra={
            "mandatory": True,
            "field_type": enums.CustomDataType.DOCUMENT.value,
            "format": FieldFormat.COMMA_SEPARATED_LIST.value,
        },
    )


class ReadDatasourcesOutput(ToolOutput):
    content: str = Field(default="")  # type: ignore


class CreateDatasourceInput(BaseModel):
    content_base64: str = Field(default="")
    content: str = Field(default="")
    content_url: str = Field(default="")
    content_csv: str = Field(default="")
    content_type: str = Field(default="", json_schema_extra={"mandatory": True})
    file_name: str = Field(default="")
    folder_id: int | None = Field(default=None)
    wait_time_out: int = Field(default=300)


class CreateDatasourceOutput(ToolOutput):
    datasource_id: int = Field()
    content_type: str = Field()
    project_id: int | None = Field(default=None)
    storage_config: str | None = Field(default=None)


class SearchDatasourceByNameInput(BaseModel):
    name: str = Field(default="", json_schema_extra={"mandatory": True})


class SearchDatasourceByNameOutput(ToolOutput):
    datasource_id: str | None = Field(default=None)


class DeleteDatasourceInput(BaseModel):
    datasource_id: str
    bypass_role_check: bool = False
    workflow_name: str | None = None


class DeleteDatasourceOutput(ToolOutput):
    success: bool
