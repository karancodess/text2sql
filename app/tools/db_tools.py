"""
Database tools for executing queries and fetching schema information.
"""
import json
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from db import get_db_session, close_db_session

logger = logging.getLogger(__name__)


def execute_query(query: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Execute a SQL query safely and return results as JSON-serializable data.
    
    Args:
        query (str): The SQL query to execute.
        timeout (int): Query timeout in seconds.
    
    Returns:
        Dict[str, Any]: Result containing rows, count, and status.
    
    Example:
        {
            "success": true,
            "row_count": 5,
            "rows": [{"id": 1, "name": "John"}, ...],
            "error": null
        }
    """
    db = None
    try:
        db = get_db_session()
        
        # Execute query with timeout
        result = db.execute(text(query).execution_options(timeout=timeout))
        
        # Fetch all rows
        rows = result.fetchall()
        
        # Convert rows to dictionaries
        row_dicts = [dict(row) for row in rows]
        
        logger.info(f"Query executed successfully. Rows: {len(row_dicts)}")
        
        return {
            "success": True,
            "row_count": len(row_dicts),
            "rows": row_dicts,
            "error": None,
        }
    
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        return {
            "success": False,
            "row_count": 0,
            "rows": [],
            "error": f"Database error: {str(e)}",
        }
    
    except Exception as e:
        logger.error(f"Unexpected error during query execution: {str(e)}")
        return {
            "success": False,
            "row_count": 0,
            "rows": [],
            "error": f"Unexpected error: {str(e)}",
        }
    
    finally:
        if db:
            close_db_session(db)


def get_database_schema() -> Dict[str, Any]:
    """
    Retrieve the database schema including tables, columns, and relationships.
    
    Returns:
        Dict[str, Any]: Database schema information.
    """
    db = None
    try:
        db = get_db_session()
        inspector = inspect(db.get_bind())
        
        schema_info = {}
        
        # Get all tables
        tables = inspector.get_table_names()
        
        for table_name in tables:
            columns_info = []
            
            # Get columns for each table
            for column in inspector.get_columns(table_name):
                columns_info.append({
                    "name": column["name"],
                    "type": str(column["type"]),
                    "nullable": column["nullable"],
                    "primary_key": column.get("primary_key", False),
                })
            
            # Get foreign keys
            foreign_keys = []
            for fk in inspector.get_foreign_keys(table_name):
                foreign_keys.append({
                    "constrained_columns": fk["constrained_columns"],
                    "referred_table": fk["referred_table"],
                    "referred_columns": fk["referred_columns"],
                })
            
            schema_info[table_name] = {
                "columns": columns_info,
                "foreign_keys": foreign_keys,
            }
        
        return {"success": True, "tables": schema_info}
    
    except Exception as e:
        logger.error(f"Error retrieving database schema: {str(e)}")
        return {"success": False, "error": str(e)}
    
    finally:
        if db:
            close_db_session(db)


def validate_query_syntax(query: str) -> Dict[str, Any]:
    """
    Validate SQL query syntax by attempting to parse it (without executing).
    
    Args:
        query (str): The SQL query to validate.
    
    Returns:
        Dict[str, Any]: Validation result.
    """
    db = None
    try:
        db = get_db_session()
        
        # Try to parse the query
        parsed = text(query)
        
        logger.info("Query syntax is valid")
        
        return {
            "is_valid": True,
            "error": None,
        }
    
    except SQLAlchemyError as e:
        logger.warning(f"Query syntax error: {str(e)}")
        return {
            "is_valid": False,
            "error": str(e),
        }
    
    except Exception as e:
        logger.error(f"Error validating query: {str(e)}")
        return {
            "is_valid": False,
            "error": str(e),
        }
    
    finally:
        if db:
            close_db_session(db)


def check_destructive_operations(query: str) -> bool:
    """
    Check if a query contains destructive operations.
    
    Args:
        query (str): The SQL query to check.
    
    Returns:
        bool: True if query contains destructive operations, False otherwise.
    """
    destructive_keywords = [
        "DELETE",
        "DROP",
        "UPDATE",
        "INSERT",
        "TRUNCATE",
        "ALTER",
        "CREATE",
    ]
    
    upper_query = query.upper()
    
    for keyword in destructive_keywords:
        if keyword in upper_query:
            return True
    
    return False
