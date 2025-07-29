from typing import Any

from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.nl_to_sql_models import (
    DatabaseCredentials,
    DatabaseHierarchy,
    DatabaseSelection,
    Enum,
    NLToSQLInput,
    NLToSQLOutput,
    SchemaSelection,
    SourceSelectionInput,
    SourceSelectionOutput,
    SQADatabaseConfig,
    SqlDialect,
    SqlType,
)

__all__ = [
    "DatabaseCredentials",
    "DatabaseHierarchy",
    "DatabaseSelection",
    "Enum",
    "NLToSQLInput",
    "NLToSQLOutput",
    "SQADatabaseConfig",
    "SchemaSelection",
    "SourceSelectionInput",
    "SourceSelectionOutput",
    "SqlDialect",
    "SqlType",
    "generate_sql",
]


def generate_sql(
    *,
    query: str,
    num_tables_to_filter_for_sql_generation: int = DEFAULT,
    sample_rows: dict[str, list[dict[str, Any]]] | None = DEFAULT,
    database_config: SQADatabaseConfig,
) -> NLToSQLOutput:
    """
    Convert natural language queries to SQL with automatic table selection.

    This tool combines table selection and SQL generation into a single step:
    1. Analyzes your query to select the most relevant tables
    2. Generates optimized SQL using the selected tables
    3. Converts to the appropriate SQL dialect for your database
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = NLToSQLInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="nl_to_sql", name="generate_sql", input=input_model.model_dump()
    )
    return NLToSQLOutput.model_validate(output_model)
