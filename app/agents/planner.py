"""
Planner Agent: Analyzes user queries and creates strategic database access plans.
"""
import logging
from typing import Dict, Any
from agents.llm import get_llm
from prompts import PLANNER_SYSTEM_PROMPT, DATABASE_SCHEMA

logger = logging.getLogger(__name__)


class PlannerAgent:
    """
    Analyzes natural language queries to create database access plans.
    """
    
    def __init__(self):
        self.llm = None
        self.system_prompt = PLANNER_SYSTEM_PROMPT
    
    def _ensure_llm(self):
        """Initialize LLM lazily."""
        if self.llm is None:
            self.llm = get_llm()
    
    def plan(self, user_query: str) -> Dict[str, Any]:
        """
        Create a strategic plan for how to query the database.
        
        Args:
            user_query (str): The user's natural language query.
        
        Returns:
            Dict[str, Any]: Contains the plan and any errors.
        """
        try:
            self._ensure_llm()
            logger.info(f"Planning for query: {user_query}")
            
            # Create messages for LLM
            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": user_query
                }
            ]
            
            # Invoke LLM
            plan_text = self.llm.invoke(messages)
            
            logger.info(f"Plan generated: {plan_text[:200]}...")
            
            return {
                "success": True,
                "plan": plan_text,
                "error": None,
            }
        
        except Exception as e:
            logger.error(f"Error in planner agent: {str(e)}")
            return {
                "success": False,
                "plan": None,
                "error": str(e),
            }
