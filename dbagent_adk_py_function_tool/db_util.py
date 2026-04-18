import os
from typing import Any, Dict, List, Optional, Tuple

try:
    import pyodbc
except ImportError as exc:
    pyodbc = None


def _quote_identifier(identifier: str) -> str:
    return f"[{identifier.replace(']', ']]')}]"


def _parse_table_name(table_name: str) -> str:
    if '.' in table_name:
        schema, table = table_name.split('.', 1)
    else:
        schema, table = 'dbo', table_name
    return f"{_quote_identifier(schema)}.{_quote_identifier(table)}"


def _get_connection(database_name: Optional[str] = None):
    if pyodbc is None:
        raise ImportError(
            'pyodbc is required for MSSQL connectivity. Install it in your environment.'
        )

    host = os.environ.get('DB_HOST')
    user = os.environ.get('DB_USER')
    password = os.environ.get('DB_PASSWORD')
    driver = os.environ.get('DB_DRIVER', 'ODBC Driver 18 for SQL Server')
    port = os.environ.get('DB_PORT', '1433')
    trusted = os.environ.get('DB_TRUSTED_CONNECTION', 'false').lower() in (
        'true', '1', 'yes', 'y', 'no','n','0'
    )

    if not host:
        raise ValueError('DB_HOST is not set in environment variables.')

    connection_parts = [f'DRIVER={{{driver}}}', f'SERVER={host},{port}']
    if database_name:
        connection_parts.append(f'DATABASE={database_name}')

    if trusted:
        connection_parts.append('Trusted_Connection=Yes')
    else:
        if not user or not password:
            raise ValueError(
                'DB_USER and DB_PASSWORD must be set in environment variables when not using trusted connection.'
            )
        connection_parts.append(f'UID={user}')
        connection_parts.append(f'PWD={password}')
        connection_parts.append('Encrypt=yes')
        connection_parts.append('TrustServerCertificate=yes')

    conn_str = ';'.join(connection_parts) + ';'
    return pyodbc.connect(conn_str, autocommit=True, timeout=30)


def _apply_select_limit(query: str, limit: int) -> str:
    normalized = query.lstrip()
    if not normalized[:6].lower() == 'select':
        return query

    remainder = normalized[6:]
    stripped = remainder.lstrip()

    if stripped.lower().startswith('top'):
        return query

    if stripped.lower().startswith('distinct'):
        return f"SELECT DISTINCT TOP {limit} {stripped[8:]}"
    if stripped.lower().startswith('all'):
        return f"SELECT ALL TOP {limit} {stripped[3:]}"

    return f"SELECT TOP {limit} {stripped}"


def list_databases() -> Dict[str, Any]:
    """Return available database names on the configured MSSQL server."""
    try:
        with _get_connection('master') as conn:
            cursor = conn.execute(
                'SELECT name FROM sys.databases ORDER BY name;'
            )
            databases = [row[0] for row in cursor.fetchall()]
        return {
            'success': True,
            'databases': databases,
        }
    except Exception as exc:
        return {
            'success': False,
            'message': f'Unable to list databases: {exc}',
        }


def list_tables(database_name: str) -> Dict[str, Any]:
    """Return table names for the given MSSQL database."""
    try:
        with _get_connection(database_name) as conn:
            cursor = conn.execute(
                "SELECT TABLE_SCHEMA, TABLE_NAME "
                "FROM INFORMATION_SCHEMA.TABLES "
                "WHERE TABLE_TYPE = 'BASE TABLE' "
                "ORDER BY TABLE_SCHEMA, TABLE_NAME;"
            )
            tables = [f"{row[0]}.{row[1]}" for row in cursor.fetchall()]
        return {
            'success': True,
            'database': database_name,
            'tables': tables,
        }
    except Exception as exc:
        return {
            'success': False,
            'message': f'Unable to list tables: {exc}',
        }


def get_table_schema(database_name: str, table_name: str) -> Dict[str, Any]:
    """Return schema details for a table in the MSSQL database."""
    try:
        schema, table = (
            table_name.split('.', 1)
            if '.' in table_name
            else ('dbo', table_name)
        )
        with _get_connection(database_name) as conn:
            cursor = conn.execute(
                "SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, "
                "CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, NUMERIC_SCALE, COLUMN_DEFAULT "
                "FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ? "
                "ORDER BY ORDINAL_POSITION;",
                (schema, table),
            )
            schema_rows = [
                {
                    'column_name': row.COLUMN_NAME,
                    'data_type': row.DATA_TYPE,
                    'is_nullable': row.IS_NULLABLE,
                    'max_length': row.CHARACTER_MAXIMUM_LENGTH,
                    'numeric_precision': row.NUMERIC_PRECISION,
                    'numeric_scale': row.NUMERIC_SCALE,
                    'column_default': row.COLUMN_DEFAULT,
                }
                for row in cursor.fetchall()
            ]

        if not schema_rows:
            return {
                'success': False,
                'message': f"Table not found or no schema available for '{table_name}'",
            }

        return {
            'success': True,
            'database': database_name,
            'table': table_name,
            'schema': schema_rows,
        }
    except Exception as exc:
        return {
            'success': False,
            'message': f'Unable to get table schema: {exc}',
        }


def read_table_rows(
    database_name: str,
    table_name: str,
    limit: int = 100,
) -> Dict[str, Any]:
    """Return rows from a specific MSSQL table."""
    try:
        object_name = _parse_table_name(table_name)
        query = f"SELECT TOP {limit} * FROM {object_name};"
        with _get_connection(database_name) as conn:
            cursor = conn.execute(query)
            columns = [column[0] for column in cursor.description] if cursor.description else []
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return {
            'success': True,
            'database': database_name,
            'table': table_name,
            'columns': columns,
            'rows': rows,
        }
    except Exception as exc:
        return {
            'success': False,
            'message': f'Unable to read table rows: {exc}',
        }


def execute_read_query(
    database_name: str,
    query: str,
    limit: int = 100,
) -> Dict[str, Any]:
    """Execute a read-only SQL Server query."""
    normalized = query.strip().lower()
    if not normalized.startswith(('select', 'with')):
        return {
            'success': False,
            'message': 'Only read-only SELECT or WITH queries are allowed.',
        }

    if normalized.startswith('select') and 'top' not in normalized[:20]:
        query = _apply_select_limit(query, limit)

    try:
        with _get_connection(database_name) as conn:
            cursor = conn.execute(query)
            columns = [column[0] for column in cursor.description] if cursor.description else []
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return {
            'success': True,
            'database': database_name,
            'query': query,
            'columns': columns,
            'rows': rows,
        }
    except Exception as exc:
        return {
            'success': False,
            'message': f'Unable to execute read query: {exc}',
        }


def find_tables_by_column(database_name: str, column_name: str) -> Dict[str, Any]:
    """Return tables in a database that contain the requested column."""
    try:
        with _get_connection(database_name) as conn:
            cursor = conn.execute(
                "SELECT TABLE_SCHEMA, TABLE_NAME "
                "FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE COLUMN_NAME = ? "
                "ORDER BY TABLE_SCHEMA, TABLE_NAME;",
                (column_name,),
            )
            tables = [f"{row.TABLE_SCHEMA}.{row.TABLE_NAME}" for row in cursor.fetchall()]

        if not tables:
            return {
                'success': False,
                'message': f"Column '{column_name}' not found in database '{database_name}'",
            }

        return {
            'success': True,
            'database': database_name,
            'column_name': column_name,
            'tables': tables,
        }
    except Exception as exc:
        return {
            'success': False,
            'message': f'Unable to find tables by column: {exc}',
        }


def find_column_across_databases(column_name: str, limit_databases: int = 20) -> Dict[str, Any]:
    """Search all available databases for tables that contain the requested column."""
    try:
        dbs_result = list_databases()
        if not dbs_result.get('success'):
            return dbs_result

        matches = []
        databases = dbs_result.get('databases', [])[:limit_databases]
        for database_name in databases:
            with _get_connection(database_name) as conn:
                cursor = conn.execute(
                    "SELECT TABLE_SCHEMA, TABLE_NAME "
                    "FROM INFORMATION_SCHEMA.COLUMNS "
                    "WHERE COLUMN_NAME = ? "
                    "ORDER BY TABLE_SCHEMA, TABLE_NAME;",
                    (column_name,),
                )
                for row in cursor.fetchall():
                    matches.append(
                        {
                            'database': database_name,
                            'table': f"{row.TABLE_SCHEMA}.{row.TABLE_NAME}",
                            'column_name': column_name,
                        }
                    )

        if not matches:
            return {
                'success': False,
                'message': f"Column '{column_name}' not found in the first {len(databases)} databases.",
            }

        return {
            'success': True,
            'column_name': column_name,
            'matches': matches,
        }
    except Exception as exc:
        return {
            'success': False,
            'message': f'Unable to search column across databases: {exc}',
        }


def search_column_values(
    database_name: str,
    column_name: str,
    limit: int = 100,
) -> Dict[str, Any]:
    """Return values for a column across all tables in a database that contain it."""
    try:
        tables_result = find_tables_by_column(database_name, column_name)
        if not tables_result.get('success'):
            return tables_result

        values_by_table = {}
        for table_name in tables_result.get('tables', []):
            object_name = _parse_table_name(table_name)
            query = f"SELECT TOP {limit} { _quote_identifier(column_name) } FROM {object_name};"
            with _get_connection(database_name) as conn:
                cursor = conn.execute(query)
                rows = [row[0] for row in cursor.fetchall()]
            values_by_table[table_name] = rows

        return {
            'success': True,
            'database': database_name,
            'column_name': column_name,
            'values_by_table': values_by_table,
        }
    except Exception as exc:
        return {
            'success': False,
            'message': f'Unable to search column values: {exc}',
        }
