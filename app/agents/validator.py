"""
Validator Agent: Validates SQL queries for syntax and security.
"""
import logging
import json
import re
from typing import Dict, Any
from agents.llm import get_llm
from prompts import VALIDATOR_SYSTEM_PROMPT
from tools.db_tools import check_destructive_operations

logger = logging.getLogger(__name__)


class ValidatorAgent:
    """
    Validates SQL queries for syntax correctness and security issues.
    """
    
    def __init__(self):
        self.llm = None
        self.system_prompt = VALIDATOR_SYSTEM_PROMPT
    
    def _ensure_llm(self):
        """Initialize LLM lazily."""
        if self.llm is None:
            self.llm = get_llm()
    
    def validate(self, sql_query: str) -> Dict[str, Any]:
        """
        Validate a SQL query for syntax and security.
        
        Args:
            sql_query (str): The SQL query to validate.
        
        Returns:
            Dict[str, Any]: Validation result with is_valid flag and details.
        """
        try:
            self._ensure_llm()
            logger.info(f"Validating SQL query: {sql_query[:100]}...")
            
            # First, do a quick check for destructive operations
            has_destructive = check_destructive_operations(sql_query)
            
            if has_destructive:
                logger.warning("Query contains destructive operations")
                return {
                    "is_valid": False,
                    "has_destructive_operations": True,
                    "syntax_errors": [],
                    "security_issues": ["Query contains destructive operations (DELETE, UPDATE, INSERT, DROP, etc.)"],
                    "warnings": [],
                    "feedback": "For security, only SELECT queries are allowed.",
                }
            
            # Create messages for LLM validation
            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": f"Validate this SQL query:\n{sql_query}"
                }
            ]
            
            # Invoke LLM
            validation_response = self.llm.invoke(messages)
            
            # Parse JSON response
            validation_data = self._parse_validation_response(validation_response)
            
            logger.info(f"Validation result: {validation_data}")
            
            return validation_data
        
        except Exception as e:
            logger.error(f"Error in validator agent: {str(e)}")
            return {
                "is_valid": False,
                "has_destructive_operations": False,
                "syntax_errors": [str(e)],
                "security_issues": [],
                "warnings": [],
                "feedback": "Validation failed",
            }
    
    @staticmethod
    def _parse_validation_response(response: str) -> Dict[str, Any]:
        """
        Parse validation response.
        
        Args:
            response (str): The validation response text.
        
        Returns:
            Dict[str, Any]: Parsed validation data.
        """
        try:
            # Try to extract JSON from response
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except (json.JSONDecodeError, AttributeError):
            pass
        
        # Fallback parsing
        is_valid = "valid" in response.lower() and "error" not in response.lower()
        
        return {
            "is_valid": is_valid,
            "has_destructive_operations": False,
            "syntax_errors": [] if is_valid else ["Unable to fully parse response"],
            "security_issues": [],
            "warnings": [],
            "feedback": response[:200],
        }
