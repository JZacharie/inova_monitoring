from typing import Any, List, Dict
from sqlalchemy import text
from sqlalchemy.engine import Engine, create_engine
from .config import settings

def get_db_url() -> str:
    """
    Construct the SQLAlchemy database URL from settings.
    """
    # Using psycopg2-binary for the connection
    return f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"

def get_engine() -> Engine:
    """
    Create and return a SQLAlchemy engine.
    """
    return create_engine(get_db_url())

def execute_query(query: str, params: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    """
    Execute a raw SQL query and return the results as a list of dictionaries.
    """
    engine = get_engine()
    with engine.connect() as connection:
        result = connection.execute(text(query), params or {})
        # If the query returns rows (like SELECT)
        if result.returns_rows:
            return [dict(row._mapping) for row in result]
        return []

def get_table_data(table_name: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Fetch all data from a specific table.
    """
    # Note: Using f-string for table name is safe here only if table_name is trusted/hardcoded.
    # In a real app, you'd want more validation to prevent SQL injection.
    query = f"SELECT * FROM {table_name} LIMIT :limit"
    return execute_query(query, {"limit": limit})
