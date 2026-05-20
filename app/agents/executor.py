"""
Executor Agent: Executes validated SQL queries against the database.
"""
import logging
from typing import Dict, Any
from tools.db_tools import execute_query

logger = logging.getLogger(__name__)


class ExecutorAgent:
    """
    Executes validated SQL queries and returns results.
    """
    
    def __init__(self):
        pass
    
    def execute(self, sql_query: str) -> Dict[str, Any]:
        """
        Execute a validated SQL query.
        
        Args:
            sql_query (str): The validated SQL query to execute.
        
        Returns:
            Dict[str, Any]: Execution results with rows and status.
        """
        try:
            logger.info(f"Executing SQL query: {sql_query[:100]}...")
            
            # Execute the query
            result = execute_query(sql_query)
            
            if result["success"]:
                logger.info(f"Query executed successfully. Rows: {result['row_count']}")
            else:
                logger.error(f"Query execution failed: {result['error']}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error in executor agent: {str(e)}")
            return {
                "success": False,
                "row_count": 0,
                "rows": [],
                "error": str(e),
            }
