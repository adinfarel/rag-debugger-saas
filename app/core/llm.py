"""
Base LLM service utilizing the Groq API.
Handles API calls, default model routing, and error handling.
"""
from groq import Groq, GroqError
from app.core.config import settings
from app.core.logger import get_logger
from typing import Optional

logger = get_logger(__name__)

class GroqClient:
    """Singleton-like client for Groq API interactions."""
    
    def __init__(self):
        """Initializes the Groq client using the API key from settings."""
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        
        self.default_model = "llama-3.1-8b-instant"
    
    def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.0,
    ) -> str:
        """
        Generates a response from the Groq LLM.

        Args:
            prompt (str): The input prompt for the LLM.
            model (Optional[str]): The specific model to use. Defaults to standard mixtral.
            temperature (float): Sampling temperature. Defaults to 0.0 for deterministic outputs.

        Returns:
            str: The generated text response.
            
        Raises:
            Exception: If the API call fails after handling attempts.
        """
        selected_model = model or self.default_model
        logger.info(f"Generating text using model: {selected_model}")
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role":"system", "content": "You are an expert AI reliability engineer system."},
                    {"role": "user", "content": prompt}
                ],
                model=selected_model,
                temperature=temperature,
                max_tokens=2048,
            )
            
            result = response.choices[0].message.content
            logger.debug(f"Received respose: {result}")
            
            return result
        
        except GroqError as e:
            logger.error(f"Groq API error: {e}")
            raise
        except Exception as e:
            logger.critical(f"Unexpected error during text generation: {e}")
            raise

llm_client = GroqClient()