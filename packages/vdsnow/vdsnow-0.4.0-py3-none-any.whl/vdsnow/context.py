import os
import tomli
from pathlib import Path
from typing import Tuple, Optional


def get_context_from_path(file_path: Path) -> Tuple[Optional[str], Optional[str]]:
    """
    Parses a file path to extract the database and schema names by looking for
    a 'setup' or 'snowflake_structure' directory anywhere in the path.
    """
    try:
        resolved_path = file_path.resolve()
        parts = resolved_path.parts
    except FileNotFoundError:
        parts = file_path.parts

    try:
        if 'setup' in parts:
            root_index = parts.index('setup')
        elif 'snowflake_structure' in parts:
            root_index = parts.index('snowflake_structure')
        else:
            return None, None

        if len(parts) > root_index + 2:
            db = parts[root_index + 1]
            schema = parts[root_index + 2]
            return db, schema
        else:
            return None, None
    except ValueError:
        return None, None


def get_default_context() -> Tuple[Optional[str], Optional[str]]:
    """
    Gets the default database and schema from config and environment variables.
    """
    try:
        with open("config.toml", "rb") as f:
            config = tomli.load(f)

        # Use the default connection if specified, otherwise try 'local'
        conn_name = config.get("default_connection_name", "local")

        prefix = f"SNOWFLAKE_CONNECTIONS_{conn_name.upper()}"
        db = os.getenv(f"{prefix}_DATABASE")
        schema = os.getenv(f"{prefix}_SCHEMA")
        return db, schema
    except FileNotFoundError:
        return None, None
