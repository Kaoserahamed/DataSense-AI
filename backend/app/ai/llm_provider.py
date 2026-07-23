from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate_completion(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI implementation of LLM provider"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        self.model = "gpt-4-turbo-preview"
        self._available = False
        
        try:
            if api_key and api_key != "sk-test-key" and not api_key.startswith("your-"):
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)
                self._available = True
                logger.info("OpenAI provider initialized successfully")
            else:
                logger.warning("OpenAI API key not configured or invalid")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI provider: {str(e)}")
            self._available = False
    
    def is_available(self) -> bool:
        return self._available and self.client is not None
    
    def generate_completion(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        if not self.is_available():
            raise RuntimeError("OpenAI provider is not available. Please configure a valid API key.")
        
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 1500)
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise RuntimeError(f"Failed to generate AI completion: {str(e)}")


class GeminiProvider(LLMProvider):
    """Google Gemini implementation of LLM provider"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = None
        self.model_name = None
        self._available = False
        
        # Updated list - using latest stable models available for new users
        models_to_try = [
            'models/gemini-3.6-flash',       # Newest stable flash (3.6)
            'models/gemini-3.5-flash',       # Stable 3.5 flash
            'models/gemini-flash-latest',    # Latest flash auto-updated
            'models/gemini-pro-latest',      # Latest pro fallback
            'models/gemini-2.0-flash'        # Stable 2.0 fallback
        ]
        
        if api_key and not api_key.startswith("your-") and len(api_key) > 10:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            # Select the first available model
            for model_name in models_to_try:
                try:
                    self.model_name = model_name
                    self._available = True
                    logger.info(f"Google Gemini provider initialized successfully with {model_name}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to set model {model_name}: {str(e)}")
                    continue
            
            if not self._available:
                logger.error("Failed to initialize Gemini with any available model")
        else:
            logger.warning("Google API key not configured or invalid")
    
    def is_available(self) -> bool:
        return self._available
    
    def generate_completion(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        if not self.is_available():
            raise RuntimeError("Gemini provider is not available. Please configure a valid API key.")
        
        try:
            import google.generativeai as genai
            
            # Pass system_instruction directly to GenerativeModel if present
            model_kwargs = {}
            if system_prompt:
                model_kwargs['system_instruction'] = system_prompt
            
            model = genai.GenerativeModel(self.model_name, **model_kwargs)
            
            # Generate content
            response = model.generate_content(
                prompt,
                generation_config={
                    'temperature': kwargs.get('temperature', 0.7),
                    'max_output_tokens': kwargs.get('max_tokens', 1500),
                }
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise RuntimeError(f"Failed to generate AI completion: {str(e)}")


class LLMFactory:
    """Factory to create LLM provider instances"""
    
    @staticmethod
    def create_provider(provider_type: str = "auto") -> LLMProvider:
        from app.core.config import settings
        
        api_key = settings.OPENAI_API_KEY
        
        # Auto-detect provider based on API key format
        if provider_type == "auto":
            if api_key.startswith("sk-"):
                provider_type = "openai"
                logger.info("Detected OpenAI API key")
            elif api_key.startswith("AIza") or api_key.startswith("AQ."):
                provider_type = "gemini"
                logger.info("Detected Google Gemini API key")
            else:
                # Default to Gemini for unknown formats (Google has various key formats)
                logger.warning(f"Unknown API key format (starts with: {api_key[:5]}...), trying Gemini")
                provider_type = "gemini"
        
        if provider_type == "openai":
            return OpenAIProvider(api_key)
        elif provider_type == "gemini":
            return GeminiProvider(api_key)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_type}")


# Global instance
llm_provider = LLMFactory.create_provider()
