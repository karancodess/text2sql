"""
SQL Generator Agent: Generates PostgreSQL queries based on plans.
"""
import logging
import re
from typing import Dict, Any
from agents.llm import get_llm
from prompts import SQL_GENERATOR_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class SQLGeneratorAgent:
    """
    Generates PostgreSQL queries based on database access plans.
    """
    
    def __init__(self):
        self.llm = None
        self.system_prompt = SQL_GENERATOR_SYSTEM_PROMPT
    
    def _ensure_llm(self):
        """Initialize LLM lazily."""
        if self.llm is None:
            self.llm = get_llm()
    
    def generate(self, plan: str, user_query: str) -> Dict[str, Any]:
        """
        Generate a SQL query from a plan.
        
        Args:
            plan (str): The strategic plan from the planner agent.
            user_query (str): The original user query for context.
        
        Returns:
            Dict[str, Any]: Contains the generated SQL query or errors.
        """
        try:
            self._ensure_llm()
            logger.info(f"Generating SQL for plan: {plan[:100]}...")
            
            # Create messages for LLM
            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": f"Plan: {plan}\n\nOriginal Query: {user_query}"
                }
            ]
            
            # Invoke LLM
            sql_query = self.llm.invoke(messages)
            
            # Clean up SQL query - remove markdown code blocks if present
            sql_query = self._clean_sql(sql_query)
            
            logger.info(f"SQL generated: {sql_query[:200]}...")
            
            return {
                "success": True,
                "sql": sql_query,
                "error": None,
            }
        
        except Exception as e:
            logger.error(f"Error in SQL generator agent: {str(e)}")
            return {
                "success": False,
                "sql": None,
                "error": str(e),
            }
    
    @staticmethod
    def _clean_sql(sql: str) -> str:
        """
        Clean up SQL query by removing markdown code blocks and extra whitespace.
        
        Args:
            sql (str): Raw SQL string potentially with markdown.
        
        Returns:
            str: Cleaned SQL query.
        """
        # Remove markdown code blocks
        sql = re.sub(r"```sql\n?", "", sql)
        sql = re.sub(r"```\n?", "", sql)
        sql = re.sub(r"^```", "", sql, flags=re.MULTILINE)
        sql = re.sub(r"```$", "", sql, flags=re.MULTILINE)
        
        # Remove extra whitespace
        sql = sql.strip()
        
        return sql
