import typing as t
from enum import Enum
from typing import Optional
from urllib.parse import quote_plus, urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.engine import URL

from . import ToolOutput


class SqlType(str, Enum):
    INTEGER = "integer"
    BIGINT = "bigint"
    FLOAT = "float"
    STRING = "string"
    TEXT = "text"
    DATETIME = "datetime"
    DATE = "date"
    TIME = "time"
    BOOLEAN = "boolean"
    JSON = "json"


class SqlDialect(str, Enum):
    TRINO = "trino"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MSSQL = "mssql"
    ORACLE = "oracle"
    SNOWFLAKE = "snowflake"


class DatabaseCredentials(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None

    model_config = ConfigDict(protected_namespaces=())


class DatabaseSelection(BaseModel):
    """Represents selected databases and their child selections"""

    name: str
    schemas: dict[str, "SchemaSelection"] = Field(default_factory=dict)
    fully_selected: bool = False

    def get_selected_schemas(self) -> set[str]:
        """Returns all selected schema names for this database"""
        if self.fully_selected:
            return set(self.schemas.keys())
        return {name for name, schema in self.schemas.items() if schema.is_selected()}

    def is_selected(self) -> bool:
        """Returns True if the database or any of its schemas are selected"""
        return self.fully_selected or any(
            schema.is_selected() for schema in self.schemas.values()
        )


class SchemaSelection(BaseModel):
    """Represents selected schemas and their child tables"""

    name: str
    database: str
    tables: list[str] = Field(default_factory=list)
    fully_selected: bool = False

    def is_selected(self) -> bool:
        """Returns True if the schema or any of its tables are selected"""
        return self.fully_selected or bool(self.tables)

    def get_selected_tables(self) -> set[str]:
        """Returns all selected table names for this schema"""
        return set(self.tables)


class DatabaseHierarchy(BaseModel):
    """Root model representing the entire database selection hierarchy"""

    databases: dict[str, DatabaseSelection] = Field(default_factory=dict)

    def add_selection(self, selection: str) -> None:
        """
        Adds a selection to the hierarchy.

        Args:
            selection: String in format "<db>" or "<db>.<schema>" or
            "<db>.<schema>.<table>"
        """
        parts = selection.split(".")

        if len(parts) > 3:
            raise ValueError(f"Invalid selection format: {selection}")

        db_name = parts[0]
        if db_name not in self.databases:
            self.databases[db_name] = DatabaseSelection(name=db_name)

        db = self.databases[db_name]

        if len(parts) == 1:
            # Database level selection
            db.fully_selected = True
            return

        schema_name = parts[1]
        if schema_name not in db.schemas:
            db.schemas[schema_name] = SchemaSelection(name=schema_name, database=db_name)

        schema = db.schemas[schema_name]

        if len(parts) == 2:
            # Schema level selection
            schema.fully_selected = True
            return

        # Table level selection
        table_name = parts[2]
        if table_name not in schema.tables:
            schema.tables.append(table_name)

    def get_selected_databases(self) -> set[str]:
        """Returns all selected database names"""
        return {name for name, db in self.databases.items() if db.is_selected()}

    def get_selected_schemas(self, database: str) -> set[str]:
        """Returns all selected schema names for a given database"""
        if database not in self.databases:
            return set()
        return self.databases[database].get_selected_schemas()

    def get_selected_tables(self, database: str, schema: str) -> set[str]:
        """Returns all selected table names for a given database and schema"""
        if database not in self.databases:
            return set()
        db = self.databases[database]
        if schema not in db.schemas:
            return set()
        return db.schemas[schema].get_selected_tables()

    def is_schema_selected(self, database_name: str, schema_name: str) -> bool:
        """Check if a schema is selected in the hierarchy."""
        if database_name not in self.databases:
            return False
        if self.databases[database_name].fully_selected:
            return True
        return schema_name in self.get_selected_schemas(database_name)

    def is_table_selected(
        self, database_name: str, schema_name: str, table_name: str
    ) -> bool:
        """Check if a table is selected in the hierarchy."""
        if database_name not in self.databases:
            return False
        # if either db or schema are fully selected, then table is also selected
        if self.databases[database_name].fully_selected:
            return True
        # If Schema itself is not selected, then table cant be selected.
        if schema_name not in self.get_selected_schemas(database_name):
            return False
        # if schema is fully selected, without selecting individual tables.
        if self.databases[database_name].schemas[schema_name].fully_selected:
            return True
        # Check if any of the individual tables selected match the input.
        selected_tables = self.get_selected_tables(database_name, schema_name)
        return not selected_tables or table_name in selected_tables

    # Example usage:
    def get_database_hierarchy(self, database: str) -> Optional["DatabaseHierarchy"]:
        """
        Returns a new DatabaseHierarchy containing only the specified database's
        selections.
        If the database doesn't exist in the current hierarchy, returns None.

        Args:
            database: Name of the database to extract

        Returns:
            DatabaseHierarchy containing only the specified database, or None if not found
        """
        if database not in self.databases:
            return None

        new_hierarchy = DatabaseHierarchy()
        new_hierarchy.databases[database] = self.databases[database]
        return new_hierarchy


class SQADatabaseConfig(BaseModel):
    dialect: SqlDialect
    driver: Optional[str] = None
    database: str = "default"
    schema_name: Optional[str] = None
    credentials: Optional[DatabaseCredentials] = None
    query_params: dict[str, str] = Field(default_factory=dict)
    http_scheme: str = "https"
    verify_ssl: bool = True
    sql_query: str | None = None
    excluded_schemas: list[str] | None = Field(default_factory=lambda: [])
    db_hierarchy_selection: Optional[DatabaseHierarchy] = None

    @classmethod
    def from_url(cls, uri: str, schema_name: Optional[str] = None) -> "SQADatabaseConfig":
        parsed = urlparse(uri)
        dialect, driver = (
            parsed.scheme.split("+") if "+" in parsed.scheme else (parsed.scheme, None)
        )
        query_params = (
            dict(param.split("=") for param in parsed.query.split("&"))
            if parsed.query
            else {}
        )

        if dialect == "sqlite":
            return cls(
                dialect=SqlDialect(dialect),
                driver=driver,
                schema_name=schema_name,
                database=parsed.path.lstrip("/") if parsed.path else ":memory:",
                query_params=query_params,
            )

        credentials = DatabaseCredentials(
            username=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port or cls._get_default_port(dialect),
        )

        return cls(
            dialect=SqlDialect(dialect),
            driver=driver,
            database=parsed.path.lstrip("/") if parsed.path else "",
            schema_name=schema_name,
            credentials=credentials,
            query_params=query_params,
            http_scheme=parsed.scheme,
        )

    def to_url(self) -> URL:
        if self.dialect == SqlDialect.SQLITE:
            return URL.create(
                drivername=f"{self.dialect.value}"
                f"{f'+{self.driver}' if self.driver else ''}",
                database=self.database or ":memory:",
                query=self.query_params,
            )

        return URL.create(
            drivername=f"{self.dialect.value}{f'+{self.driver}' if self.driver else ''}",
            username=self.credentials.username if self.credentials else None,
            password=self.credentials.password if self.credentials else None,
            host=self.credentials.host if self.credentials else None,
            port=self.credentials.port if self.credentials else None,
            database=self.database,
            query=self.query_params,
        )

    def to_connection_url(self) -> str:
        if self.dialect == SqlDialect.SQLITE:
            return f"sqlite:///{self.database}"

        if not self.credentials:
            return f"{self.dialect.value}://{self.database}"

        auth = (
            f"{quote_plus(self.credentials.username)}:{quote_plus(self.credentials.password)}@"
            if self.credentials.username and self.credentials.password
            else ""
        )
        return f"{self.dialect.value}://{auth}{self.credentials.host}:{self.credentials.port}/{self.database}"

    @staticmethod
    def _get_default_port(dialect: str | None) -> int:
        return {
            "postgresql": 5432,
            "trino": 443,
            "mysql": 3306,
            "oracle": 1521,
            "mssql": 1433,
        }.get(dialect or "", 443)


class SourceSelectionInput(BaseModel):
    """Input model for source/table selection"""

    query: str = Field(
        description="Natural language query to analyze for table selection"
    )
    num_tables: int = Field(
        default=3, ge=1, description="Number of most relevant tables to return"
    )
    database_config: SQADatabaseConfig = Field(
        description="Database configuration for connecting to the target database"
    )

    @classmethod
    @field_validator("database_config", mode="before")
    def validate_database_config(cls, v: t.Any) -> SQADatabaseConfig:
        """Transform dict to SQADatabaseConfig and validate configuration"""
        # If it's already an SQADatabaseConfig, use it directly
        if isinstance(v, SQADatabaseConfig):
            config = v
        # If it's a dict, transform to SQADatabaseConfig
        elif isinstance(v, dict):
            try:
                config = SQADatabaseConfig(**v)
            except Exception as e:
                raise ValueError(f"Invalid database configuration: {str(e)}")
        else:
            raise ValueError(
                "database_config must be a dictionary or SQADatabaseConfig object"
            )

        # Basic validation checks
        if not config.database:
            raise ValueError("Database name is required")

        if config.dialect.value not in [
            "postgresql",
            "mysql",
            "sqlite",
            "trino",
            "mssql",
            "oracle",
            "snowflake",
        ]:
            raise ValueError(f"Unsupported database dialect: {config.dialect.value}")

        # For non-SQLite databases, validate credentials
        if config.dialect.value != "sqlite":
            if not config.credentials:
                raise ValueError(
                    "Database credentials are required for non-SQLite databases"
                )
            if not config.credentials.host:
                raise ValueError("Database host is required")
            if not config.credentials.username:
                raise ValueError("Database username is required")
            if not config.credentials.password:
                raise ValueError("Database password is required")

        return config


class SourceSelectionOutput(ToolOutput):
    """Output model for source/table selection"""

    relevant_tables: list[dict[str, t.Any]] = Field(
        description="List of tables selected with relevance scores and reasoning"
    )
    explanation: str = Field(
        description="Overall explanation of the table selection process"
    )
    table_definitions: list[dict[str, t.Any]] = Field(
        description="Detailed definitions of the selected tables"
    )


class NLToSQLInput(BaseModel):
    """Input model for NL-to-SQL conversion"""

    query: str = Field(description="Natural language query to convert to SQL")
    num_tables_to_filter_for_sql_generation: int = Field(
        default=3,
        ge=1,
        description="Number of most relevant tables to select for SQL generation",
    )
    sample_rows: t.Optional[dict[str, list[dict[str, t.Any]]]] = Field(
        default=None,
        description="Optional sample data to provide context for SQL generation",
    )
    connector_name: str = Field(
        description="Name of the connector to use for the database"
    )


class NLToSQLOutput(ToolOutput):
    """Output model for NL-to-SQL conversion"""

    sql_query: str = Field(description="Generated PostgreSQL query")
    dialect_sql_query: t.Optional[str] = Field(
        default=None, description="Query converted to target database dialect"
    )
    explanation: str = Field(description="Explanation of the generated SQL query")
    table_selection_explanation: str = Field(
        description="Explanation of why specific tables were selected"
    )
    selected_tables: list[dict[str, t.Any]] = Field(
        description="List of tables that were selected for the query"
    )
    database_name: str = Field(description="Name of the database used")


class ExecuteSQLInput(BaseModel):
    """Input model for SQL execution"""

    sql_query: str = Field(description="SQL query to execute")
    database_name: str = Field(description="Name of the database to execute the query on")
    connector_name: str = Field(
        description="Name of the connector to use for the database"
    )
    limit: Optional[int] = Field(
        default=None, description="Optional limit for the number of rows to return"
    )


class ExecuteSQLOutput(ToolOutput):
    """Output model for SQL execution returning a pandas DataFrame"""

    data: list[dict[str, t.Any]] = Field(
        description="Query results as a list of dictionaries (rows)"
    )
    columns: list[str] = Field(description="Column names in the result set")
    row_count: int = Field(description="Total number of rows returned")
    database_name: str = Field(
        description="Name of the database where query was executed"
    )
    execution_time_ms: Optional[float] = Field(
        default=None, description="Query execution time in milliseconds"
    )


class ListDatabasesInput(BaseModel):
    """Input model for listing databases"""

    connector_name: str = Field(
        description="Name of the connector to use for the database"
    )


class ListDatabasesOutput(ToolOutput):
    """Output model for listing databases"""

    databases: list[str] = Field(description="List of available database names")


class ListSchemasInput(BaseModel):
    """Input model for listing schemas in a database"""

    database_name: str = Field(description="Name of the database to list schemas from")
    connector_name: str = Field(
        description="Name of the connector to use for the database"
    )


class ListSchemasOutput(ToolOutput):
    """Output model for listing schemas"""

    schemas: list[str] = Field(description="List of schema names in the database")
    database_name: str = Field(description="Name of the database")


class ListTablesInput(BaseModel):
    """Input model for listing tables in a schema"""

    database_name: str = Field(description="Name of the database")
    schema_name: str = Field(description="Name of the schema to list tables from")
    connector_name: str = Field(
        description="Name of the connector to use for the database"
    )


class ListTablesOutput(ToolOutput):
    """Output model for listing tables"""

    tables: list[str] = Field(description="List of table names in the schema")
    database_name: str = Field(description="Name of the database")
    schema_name: str = Field(description="Name of the schema")
    count: int = Field(description="Total number of tables")


class SearchTablesInput(BaseModel):
    """Input model for searching tables using natural language"""

    query: str = Field(description="Natural language query to search for relevant tables")
    connector_name: str = Field(
        description="Name of the connector to use for the database"
    )
    num_tables: int = Field(
        default=10, ge=1, description="Maximum number of relevant tables to return"
    )


class SearchTablesOutput(ToolOutput):
    """Output model for table search results"""

    relevant_tables: list[dict[str, t.Any]] = Field(
        description="List of tables with relevance scores and metadata"
    )
    explanation: str = Field(description="Explanation of why these tables were selected")
    count: int = Field(description="Number of tables found")
