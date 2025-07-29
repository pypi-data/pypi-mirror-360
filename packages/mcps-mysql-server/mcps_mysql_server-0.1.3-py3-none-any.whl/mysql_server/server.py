import asyncio
import logging
import os
import sys
from mysql.connector import connect, Error
from mcp.server.fastmcp import FastMCP
from mcp.types import Resource, Tool, TextContent
from pydantic import AnyUrl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mysql_server")

def get_db_config():
    """Get database configuration from environment variables."""
    config = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE"),
        "charset": os.getenv("MYSQL_CHARSET", "utf8mb4"),
        "collation": os.getenv("MYSQL_COLLATION", "utf8mb4_unicode_ci"),
        "autocommit": True,
        "sql_mode": os.getenv("MYSQL_SQL_MODE", "TRADITIONAL")
    }

    config = {k: v for k, v in config.items() if v is not None}

    if not all([config.get("user"), config.get("password"), config.get("database")]):
        logger.error("Missing required database configuration. Please check environment variables:")
        logger.error("MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DATABASE are required")
        raise ValueError("Missing required database configuration")

    return config

# Initialize server
mcp = FastMCP("mysql_server")

@mcp.tool()
async def execute_sql(query: str) -> str:
    """Execute an SQL query on the MySQL server.
    
    Args:
        query: The SQL query to execute
    """
    config = get_db_config()
    logger.info(f"Executing SQL query: {query}")

    try:
        logger.info(f"Connecting to MySQL with charset: {config.get('charset')}, collation: {config.get('collation')}")
        with connect(**config) as conn:
            logger.info(f"Successfully connected to MySQL server version: {conn.get_server_info()}")
            with conn.cursor() as cursor:
                cursor.execute(query)

                if query.strip().upper().startswith("SHOW TABLES"):
                    tables = cursor.fetchall()
                    result = ["Tables_in_" + config["database"]]
                    result.extend([table[0] for table in tables])
                    return "\n".join(result)

                elif cursor.description is not None:
                    columns = [desc[0] for desc in cursor.description]
                    try:
                        rows = cursor.fetchall()
                        result = [",".join(map(str, row)) for row in rows]
                        return "\n".join([",".join(columns)] + result)
                    except Error as e:
                        logger.warning(f"Error fetching results: {str(e)}")
                        return f"Query executed but error fetching results: {str(e)}"

                else:
                    conn.commit()
                    return f"Query executed successfully. Rows affected: {cursor.rowcount}"

    except Error as e:
        logger.error(f"Error executing SQL '{query}': {e}")
        logger.error(f"Error code: {e.errno}, SQL state: {e.sqlstate}")
        raise RuntimeError(f"Error executing query: {str(e)}")

@mcp.resource("mysql://tables")
async def list_tables() -> str:
    """List all tables in the database."""
    config = get_db_config()
    try:
        logger.info(f"Connecting to MySQL with charset: {config.get('charset')}, collation: {config.get('collation')}")
        with connect(**config) as conn:
            logger.info(f"Successfully connected to MySQL server version: {conn.get_server_info()}")
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                result = ["Tables_in_" + config["database"]]
                result.extend([table[0] for table in tables])
                return "\n".join(result)

    except Error as e:
        logger.error(f"Failed to list tables: {str(e)}")
        logger.error(f"Error code: {e.errno}, SQL state: {e.sqlstate}")
        raise RuntimeError(f"Failed to list tables: {str(e)}")

@mcp.resource("mysql://table/{table_name}")
async def get_table_schema(table_name: str) -> str:
    """Get the schema of a specific table.
    
    Args:
        table_name: The name of the table to get the schema for
    """
    config = get_db_config()
    try:
        logger.info(f"Connecting to MySQL with charset: {config.get('charset')}, collation: {config.get('collation')}")
        with connect(**config) as conn:
            logger.info(f"Successfully connected to MySQL server version: {conn.get_server_info()}")
            with conn.cursor() as cursor:
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                result = ["Field,Type,Null,Key,Default,Extra"]
                result.extend([",".join(map(str, column)) for column in columns])
                return "\n".join(result)

    except Error as e:
        logger.error(f"Failed to get schema for table {table_name}: {str(e)}")
        logger.error(f"Error code: {e.errno}, SQL state: {e.sqlstate}")
        raise RuntimeError(f"Failed to get schema for table {table_name}: {str(e)}")

def run():
    """Entry point for the package."""
    logger.info("Starting MySQL MCP server via entry point")
    try:
        mcp.run()
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    run() 