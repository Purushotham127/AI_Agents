from __future__ import annotations

import json
import os
from typing import Any

import dotenv
import pyodbc


def get_db_connection():
    """Internal helper to establish a raw DB connection."""
    dotenv.load_dotenv(".env")
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    conn_str = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    return pyodbc.connect(conn_str)


def register_db_tools(mcp_server: Any) -> None:
    @mcp_server.tool()
    def fetch_all_tables() -> str:
        """List the base tables in the connected SQL database."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            return json.dumps({"status": "success", "tables": tables})
        except Exception as exc:
            return json.dumps({"status": "error", "message": str(exc)})

    @mcp_server.tool()
    def create_table(table_name: str, columns: str) -> str:
        """Create a database table with the provided SQL column definitions."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(f"CREATE TABLE {table_name} ({columns})")
            conn.commit()
            conn.close()
            return json.dumps({"status": "success", "message": f"Table {table_name} created"})
        except Exception as exc:
            return json.dumps({"status": "error", "message": str(exc)})

    @mcp_server.tool()
    def insert_data(table_name: str, data: dict) -> str:
        """Insert a single row of data into a table."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["?"] * len(data))
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            cursor.execute(query, list(data.values()))
            conn.commit()
            conn.close()
            return json.dumps({"status": "success", "message": f"Data inserted into {table_name}"})
        except Exception as exc:
            return json.dumps({"status": "error", "message": str(exc)})

    @mcp_server.tool()
    def get_table_schema(table_name: str) -> str:
        """List the columns for a database table."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
            columns = [row[0] for row in cursor.fetchall()]
            conn.close()
            return json.dumps({"status": "success", "columns": columns})
        except Exception as exc:
            return json.dumps({"status": "error", "message": str(exc)})

    @mcp_server.tool()
    def query_data(query: str) -> str:
        """Execute a raw SQL SELECT query and return the rows."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            result = [dict(zip(columns, row)) for row in rows]
            conn.close()
            return json.dumps({"status": "success", "data": result})
        except Exception as exc:
            return json.dumps({"status": "error", "message": str(exc)})

    @mcp_server.tool()
    def delete_data(table_name: str, condition: str) -> str:
        """Delete rows from a table based on a SQL condition."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {table_name} WHERE {condition}")
            conn.commit()
            conn.close()
            return json.dumps({"status": "success", "message": f"Data deleted from {table_name}"})
        except Exception as exc:
            return json.dumps({"status": "error", "message": str(exc)})
