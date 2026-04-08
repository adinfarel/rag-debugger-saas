"""
Base LLM service utilizing the Groq API.
Handles API calls, default model routing, and error handling.
"""
import json
import regex as re
from groq import Groq, GroqError
from app.core.config import settings
from app.core.logger import get_logger
from typing import Optional

logger = get_logger(__name__)

class GroqClient:
    """Singleton-like client for Groq API interactions."""
    
    TIERING_SYSTEM = {
        "pro": {"model_name": "llama-3.3-70b-versatile",
                 "tier_prompt": """
            \n\n[SYSTEM INSTRUCTION: You are an Elite AI Reliability Engineer. 
            Provide highly technical, architectural advice. Include code snippets if possible. 
            Be extremely precise.]"""},
        "thinking": {"model_name": "llama-3.1-8b-instant",
                     "tier_prompt": """
            \n\n[SYSTEM INSTRUCTION: You MUST wrap your step-by-step logical reasoning 
            inside <think> ... </think> tags BEFORE providing the final answer.]"""},
        "free": {"model_name": "llama-3.1-8b-instant",
                 "tier_prompt": """
            \n\n[SYSTEM INSTRUCTION: Provide a brief, standard, and helpful response.]"""}
    }
    
    def __init__(self):
        """Initializes the Groq client using the API key from settings."""
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        
        self.default_model = "llama-3.1-8b-instant"
    
    def generate_text(
        self,
        prompt: str,
        temperature: float = 0.0,
        tier: str = "free",
    ) -> str:
        """
        Generates a response from the Groq LLM.

        Args:
            prompt (str): The input prompt for the LLM.
            temperature (float): Sampling temperature. Defaults to 0.0 for deterministic outputs.
            tier: to classify user into different tier and provide different response based on tier. Defaults to "free".

        Returns:
            str: The generated text response.
            
        Raises:
            Exception: If the API call fails after handling attempts.
        """
        model = self.TIERING_SYSTEM.get(tier, {}).get("model_name", self.default_model)
        final_prompt = self.TIERING_SYSTEM.get(tier, {}).get("tier_prompt", "") + prompt
        
        selected_model = model or self.default_model
        logger.info(f"Generating text using model: {selected_model}")
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role":"system", "content": "You are an expert AI reliability engineer system."},
                    {"role": "user", "content": final_prompt}
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
    
    def clean_json(self, text: str) -> str:
        """This function can be used to remove tag <think> and </think> from the text."""
        text_to_think = re.sub(r'\[SYSTEM INSTRUCTION:.*?\]', '', text, flags=re.DOTALL)
        
        text_to_think = re.sub(r'<think>.*?</think>', '', text_to_think, flags=re.DOTALL)
        
        match = re.search(r'(\{.*?\}|\[.*?\])', text_to_think, flags=re.DOTALL)
        
        if match:
            cleaned = match.group(1).strip()
            # Fix case: AI ngasih {"A", "B"} padahal harusnya ["A", "B"]
            if cleaned.startswith('{') and not ':' in cleaned:
                cleaned = cleaned.replace('{', '[').replace('}', ']')
            return cleaned
            
        return text_to_think.strip()


    def generate_with_tools(
        self,
        prompt: str,
        tools_schema: list,
        available_tools: dict,
        temperature: float = 0.0,
        tier: str = "free",
    ) -> str:
        """
        Generates text and automatically handles function calling (tools) loop natively via Groq.
        """
        model = self.TIERING_SYSTEM.get(tier, {}).get("model_name", self.default_model)
        final_prompt = self.TIERING_SYSTEM.get(tier, {}).get("tier_prompt", "") + prompt
        
        messages = [
            {"role": "system", "content": "You are an expert AI reliability engineer system."},
            {"role": "user", "content": final_prompt},
        ]
        
        logger.info(f"Generating text with tools using model: {model}")
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools_schema,
                tool_choice="auto", # Model will decide when to call tools based on the prompt and conversation
                temperature=temperature,
                max_tokens=2048,
            )
            
            response_message = response.choices[0].message
            tool_calls = getattr(response_message, "tool_calls", [])
            
            if not tool_calls:
                logger.info(f"[LLM] Model answered without using any tools.")
                return response_message.content
        
            logger.info(f"[LLM] Model decided to use tools {[t.function.name for t in tool_calls]}")
            
            assistant_message = {
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": [
                    {
                        "id": t.id,
                        "type": "function",
                        "function": {
                            "name": t.function.name,
                            "arguments": t.function.arguments
                        }
                    } for t in tool_calls
                ]
            }   
            
            messages.append(assistant_message)
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_tools.get(function_name)
                
                if function_to_call:
                    function_args = json.loads(tool_call.function.arguments)
                    logger.info(f"[TOOL EXECUTOR] Running {function_name} with args: {function_args}")
                    
                    function_response = function_to_call.invoke(function_args)
                    
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_response)
                    })
            
            logger.info("[LLM] Sending tool results back to model for final answer...")
            second_response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=2048,
            )
            
            return second_response.choices[0].message.content
        
        except GroqError as e:
            logger.error(f"Groq API error during tool generation: {e}")
            raise
        except Exception as e:
            logger.critical(f"Unexpected error during tool generation: {e}")
            raise
        
llm_client = GroqClient()