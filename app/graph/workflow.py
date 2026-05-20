"""
Workflow: Defines the agentic workflow state machine.
Routes queries through agents: Planner -> Generator -> Validator -> Executor -> Summarizer.
"""
import logging
from typing import Dict, Any
from agents.planner import PlannerAgent
from agents.sql_generator import SQLGeneratorAgent
from agents.validator import ValidatorAgent
from agents.executor import ExecutorAgent
from agents.summarizer import SummarizerAgent

logger = logging.getLogger(__name__)


class WorkflowState:
    """
    Represents the state throughout the workflow execution.
    """
    def __init__(self):
        self.user_query: str = ""
        self.plan: str = ""
        self.sql: str = ""
        self.is_valid: bool = False
        self.execution_results: Dict[str, Any] = {}
        self.final_answer: str = ""
        self.error: str = ""
        self.retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            "user_query": self.user_query,
            "plan": self.plan,
            "sql": self.sql,
            "is_valid": self.is_valid,
            "execution_results": self.execution_results,
            "final_answer": self.final_answer,
            "error": self.error,
            "retry_count": self.retry_count,
        }


class Text2SQLWorkflow:
    """
    Orchestrates the text-to-SQL agentic workflow.
    """
    
    MAX_RETRIES = 3
    
    def __init__(self):
        self.planner = None
        self.generator = None
        self.validator = None
        self.executor = None
        self.summarizer = None
    
    def _ensure_agents(self):
        """Initialize agents lazily."""
        if self.planner is None:
            self.planner = PlannerAgent()
        if self.generator is None:
            self.generator = SQLGeneratorAgent()
        if self.validator is None:
            self.validator = ValidatorAgent()
        if self.executor is None:
            self.executor = ExecutorAgent()
        if self.summarizer is None:
            self.summarizer = SummarizerAgent()
    
    def run(self, user_query: str) -> Dict[str, Any]:
        """
        Execute the workflow for a given user query.
        
        Args:
            user_query (str): The natural language query.
        
        Returns:
            Dict[str, Any]: The final workflow state and answer.
        """
        logger.info(f"Starting workflow for query: {user_query}")
        
        # Initialize agents lazily
        self._ensure_agents()
        
        state = WorkflowState()
        state.user_query = user_query
        
        try:
            # Step 1: Plan
            logger.info("Step 1: Planning...")
            state = self._plan_step(state)
            if state.error:
                logger.error(f"Planning failed: {state.error}")
                return state.to_dict()
            
            # Step 2-3: Generate & Validate (with retry loop)
            logger.info("Step 2-3: Generating and validating SQL...")
            for attempt in range(self.MAX_RETRIES):
                state = self._generate_step(state)
                if state.error:
                    logger.error(f"Generation failed: {state.error}")
                    return state.to_dict()
                
                state = self._validate_step(state)
                
                if state.is_valid:
                    logger.info(f"SQL validation passed (attempt {attempt + 1})")
                    break
                else:
                    logger.warning(f"SQL validation failed (attempt {attempt + 1})")
                    state.retry_count = attempt + 1
                    if attempt == self.MAX_RETRIES - 1:
                        logger.error(f"Max retries ({self.MAX_RETRIES}) exceeded")
                        state.error = "Failed to generate valid SQL after multiple attempts"
                        return state.to_dict()
            
            # Step 4: Execute
            logger.info("Step 4: Executing query...")
            state = self._execute_step(state)
            if state.error:
                logger.error(f"Execution failed: {state.error}")
                return state.to_dict()
            
            # Step 5: Summarize
            logger.info("Step 5: Summarizing results...")
            state = self._summarize_step(state)
            if state.error:
                logger.error(f"Summarization failed: {state.error}")
                return state.to_dict()
            
            logger.info("Workflow completed successfully")
            return state.to_dict()
        
        except Exception as e:
            logger.error(f"Unexpected workflow error: {str(e)}")
            state.error = f"Workflow error: {str(e)}"
            return state.to_dict()
    
    def _plan_step(self, state: WorkflowState) -> WorkflowState:
        """Planner step: Analyze query and create plan."""
        try:
            result = self.planner.plan(state.user_query)
            if not result.get("success"):
                state.error = result.get("error", "Planning failed")
            else:
                state.plan = result.get("plan", "")
        except Exception as e:
            state.error = f"Planner error: {str(e)}"
            logger.error(state.error)
        return state
    
    def _generate_step(self, state: WorkflowState) -> WorkflowState:
        """SQL Generator step: Generate SQL from plan."""
        try:
            result = self.generator.generate(state.plan, state.user_query)
            if not result.get("success"):
                state.error = result.get("error", "SQL generation failed")
            else:
                state.sql = result.get("sql", "")
                state.error = ""
        except Exception as e:
            state.error = f"Generator error: {str(e)}"
            logger.error(state.error)
        return state
    
    def _validate_step(self, state: WorkflowState) -> WorkflowState:
        """Validator step: Validate SQL syntax and security."""
        try:
            result = self.validator.validate(state.sql)
            state.is_valid = result.get("is_valid", False)
            
            if not state.is_valid:
                issues = result.get("security_issues", []) + result.get("syntax_errors", [])
                state.error = f"SQL validation failed: {'; '.join(issues)}"
                logger.warning(f"Validation failed: {state.error}")
            else:
                state.error = ""
                logger.info("SQL validation passed")
        except Exception as e:
            state.is_valid = False
            state.error = f"Validator error: {str(e)}"
            logger.error(state.error)
        return state
    
    def _execute_step(self, state: WorkflowState) -> WorkflowState:
        """Executor step: Execute the validated SQL query."""
        try:
            result = self.executor.execute(state.sql)
            state.execution_results = result
            
            if not result.get("success"):
                state.error = result.get("error", "Execution failed")
                logger.error(f"Executor error: {state.error}")
            else:
                logger.info(f"Query executed successfully")
        except Exception as e:
            state.error = f"Executor error: {str(e)}"
            state.execution_results = {"success": False, "error": state.error}
            logger.error(state.error)
        return state
    
    def _summarize_step(self, state: WorkflowState) -> WorkflowState:
        """Summarizer step: Convert results to natural language."""
        try:
            result = self.summarizer.summarize(state.user_query, state.execution_results)
            
            if not result.get("success"):
                state.error = result.get("error", "Summarization failed")
                logger.error(f"Summarizer error: {state.error}")
            else:
                state.final_answer = result.get("summary", "")
        except Exception as e:
            state.error = f"Summarizer error: {str(e)}"
            logger.error(state.error)
        return state
