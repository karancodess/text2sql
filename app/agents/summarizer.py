"""
Summarizer Agent: Converts database results to natural language answers.
"""
import logging
import json
from typing import Dict, Any
from agents.llm import get_llm
from prompts import SUMMARIZER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class SummarizerAgent:
    """
    Summarizes database query results into natural language responses.
    """
    
    def __init__(self):
        self.llm = None
        self.system_prompt = SUMMARIZER_SYSTEM_PROMPT
    
    def _ensure_llm(self):
        """Initialize LLM lazily."""
        if self.llm is None:
            self.llm = get_llm()
    
    def summarize(
        self,
        user_query: str,
        execution_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Convert database results to a natural language answer.
        
        Args:
            user_query (str): The original user query.
            execution_results (Dict[str, Any]): The database execution results.
        
        Returns:
            Dict[str, Any]: Contains the natural language summary.
        """
        try:
            self._ensure_llm()
            logger.info("Summarizing results...")
            
            # Format results for display
            if not execution_results.get("success"):
                error_msg = execution_results.get("error", "Unknown error")
                return {
                    "success": False,
                    "summary": f"An error occurred while querying the database: {error_msg}",
                    "error": error_msg,
                }
            
            rows = execution_results.get("rows", [])
            row_count = execution_results.get("row_count", 0)
            
            # Format results as JSON string for LLM
            results_str = json.dumps(rows, indent=2, default=str)
            
            if row_count == 0:
                results_str = "No results found."
            
            # Create messages for LLM
            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": f"User Query: {user_query}\n\nDatabase Results:\n{results_str}\n\nRow Count: {row_count}"
                }
            ]
            
            # Invoke LLM
            summary = self.llm.invoke(messages)
            
            logger.info(f"Summary generated: {summary[:200]}...")
            
            return {
                "success": True,
                "summary": summary,
                "error": None,
            }
        
        except Exception as e:
            logger.error(f"Error in summarizer agent: {str(e)}")
            return {
                "success": False,
                "summary": f"Error summarizing results: {str(e)}",
                "error": str(e),
            }
