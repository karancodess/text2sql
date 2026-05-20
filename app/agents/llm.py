"""
Centralized LLM configuration and instantiation.
Supports both OpenAI and Google Gemini APIs.
"""
import logging
from config import settings

logger = logging.getLogger(__name__)


class SimpleLLM:
    """Wrapper for LLM calls using direct API access."""
    
    def __init__(self, provider: str, api_key: str, model: str):
        self.provider = provider
        self.api_key = api_key
        self.model = model
    
    def invoke(self, messages: list, **kwargs) -> str:
        """
        Invoke the LLM with messages.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters
        
        Returns:
            str: The LLM response text
        """
        if self.provider == "openai":
            return self._invoke_openai(messages, **kwargs)
        elif self.provider == "gemini":
            return self._invoke_gemini(messages, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _invoke_openai(self, messages: list, **kwargs) -> str:
        """Invoke OpenAI API."""
        try:
            import openai
            openai.api_key = self.api_key
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2000),
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            raise
    
    def _invoke_gemini(self, messages: list, **kwargs) -> str:
        """Invoke Google Gemini API."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            model = genai.GenerativeModel(self.model)
            
            # Convert messages to Gemini format
            content = "\n".join([m.get("content", "") for m in messages])
            
            response = model.generate_content(
                content,
                generation_config=genai.types.GenerationConfig(
                    temperature=kwargs.get("temperature", 0.7),
                    max_output_tokens=kwargs.get("max_tokens", 2000),
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            raise


class LLMFactory:
    """Factory for creating LLM instances."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMFactory, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self) -> SimpleLLM:
        """
        Initialize the LLM based on provider settings.
        
        Returns:
            SimpleLLM: The configured language model instance.
        
        Raises:
            ValueError: If LLM provider is not supported or API key is missing.
        """
        if settings.llm_provider == "openai":
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY not set in environment variables")
            
            logger.info(f"Initializing OpenAI with model: {settings.llm_model}")
            return SimpleLLM(
                provider="openai",
                api_key=settings.openai_api_key,
                model=settings.llm_model,
            )
        
        elif settings.llm_provider == "gemini":
            if not settings.gemini_api_key:
                raise ValueError("GEMINI_API_KEY not set in environment variables")
            
            logger.info(f"Initializing Google Gemini with model: {settings.llm_model}")
            return SimpleLLM(
                provider="gemini",
                api_key=settings.gemini_api_key,
                model=settings.llm_model,
            )
        
        else:
            raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
    
    def get_llm(self) -> SimpleLLM:
        """
        Get the initialized LLM instance.
        
        Returns:
            SimpleLLM: The language model instance.
        """
        return self.llm


# Global LLM instance (lazy initialization)
_llm_factory = None


def get_llm() -> SimpleLLM:
    """
    Get the global LLM instance.
    
    Returns:
        SimpleLLM: The language model instance.
    """
    global _llm_factory
    if _llm_factory is None:
        _llm_factory = LLMFactory()
    return _llm_factory.get_llm()
