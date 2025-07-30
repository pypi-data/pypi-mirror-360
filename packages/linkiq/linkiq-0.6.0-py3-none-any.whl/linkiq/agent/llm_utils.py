import os
from openai import OpenAI
from anthropic import Anthropic
from groq import Groq
from rich.console import Console

console = Console()

class LLMUtilsError(Exception):
    """Base exception for LLMUtils errors"""
    pass

class NoAPIKeyError(LLMUtilsError):
    """Raised when no API keys are available"""
    pass

class APICallError(LLMUtilsError):
    """Raised when an API call fails"""
    pass

class ModelProviderNotAvailableError(LLMUtilsError):
    """Raised when requested model provider is not available"""
    pass

class LLMUtils:

    def __new__(cls, *args, **kwargs):
        groq_key = os.getenv("GROQ_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if not groq_key and not openai_key and not anthropic_key:
            raise NoAPIKeyError("No API keys found. Please set at least one of: GROQ_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY")
        return super().__new__(cls)

    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY", "")
        self.groq_client = Groq(api_key=self.groq_key) if self.groq_key else None

        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.openai_client = OpenAI(api_key=self.openai_key) if self.openai_key else None

        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.anthropic_client = Anthropic(api_key=self.anthropic_key) if self.anthropic_key else None
        
        self.clients = {}
        if self.groq_client:
            self.clients["groq"] = self.groq_client
        if self.openai_client:
            self.clients["openai"] = self.openai_client
        if self.anthropic_client:
            self.clients["anthropic"] = self.anthropic_client

        console.print(f"Initialized LLMUtils with providers: {list(self.clients.keys())}", style="white")

    def call_openai_gpt(self, prompt: str, model: str = None, 
                        max_tokens: int = 1024, chat_history: list = None, system_prompt: str = None) -> str:
        """
        Make a request to OpenAI's GPT model with chat history support.
        
        Args:
            prompt: The user prompt
            model: OpenAI model name (defaults to gpt-4)
            max_tokens: Maximum tokens in response
            chat_history: List of previous messages
            system_prompt: System prompt to prepend
            
        Returns:
            str: The model's response
            
        Raises:
            APICallError: If the API call fails
        """
        if not self.openai_client:
            raise ModelProviderNotAvailableError("OpenAI client not available. Check your OPENAI_API_KEY.")
            
        try:
            if model is None:
                model = "gpt-4"
            
            if chat_history is None:
                chat_history = []
            
            messages = chat_history.copy()
            
            if system_prompt:
                messages.insert(0, {"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})
            
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )

            reply = response.choices[0].message.content.strip()
            console.print(f"OpenAI API call successful with model: {model}", style="white")
            return reply
            
        except Exception as e:
            error_msg = f"Error with OpenAI API: {e}"
            console.print(error_msg, style="red")
            raise APICallError(error_msg) from e

    def call_groq(self, prompt: str, model: str = None, chat_history: list = None, system_prompt: str = None) -> str:
        """
        Make a request to the Groq API with chat history support.
        
        Args:
            prompt: The user prompt
            model: Groq model name (defaults to llama-3.1-8b-instant)
            chat_history: List of previous messages
            system_prompt: System prompt to prepend
            
        Returns:
            str: The model's response
            
        Raises:
            APICallError: If the API call fails
        """
        if not self.groq_client:
            raise ModelProviderNotAvailableError("Groq client not available. Check your GROQ_API_KEY.")
            
        try:
            if model is None:
                model = "llama-3.1-8b-instant"
                
            if chat_history is None:
                chat_history = []
                
            messages = chat_history.copy()
            
            if system_prompt:
                messages.insert(0, {"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})
            
            response = self.groq_client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=0.3
            )
            
            console.print(f"Groq API call successful with model: {model}", style="white")
            reply = response.choices[0].message.content.strip()
            return reply
            
        except Exception as e:
            error_msg = f"Error with Groq API: {e}"
            console.print(error_msg, style="red")
            raise APICallError(error_msg) from e
    
    def call_anthropic(self, prompt: str, model: str = None, chat_history: list = None, system_prompt: str = None) -> str:
        """
        Make a request to the Anthropic Claude API with chat history support.
        
        Args:
            prompt: The user prompt
            model: Anthropic model name (defaults to claude-3-5-sonnet-20241022)
            chat_history: List of previous messages
            system_prompt: System prompt to use
            
        Returns:
            str: The model's response
            
        Raises:
            APICallError: If the API call fails
        """
        if not self.anthropic_client:
            raise ModelProviderNotAvailableError("Anthropic client not available. Check your ANTHROPIC_API_KEY.")
            
        try:
            if model is None:
                model = "claude-3-5-sonnet-20241022"
                
            if chat_history is None:
                chat_history = []
                
            messages = chat_history.copy()
            messages.append({"role": "user", "content": prompt})

            # Anthropic handles system prompt as a separate parameter
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=1024,
                messages=messages,
                system=system_prompt if system_prompt else ""
            )

            console.print(f"Anthropic API call successful with model: {model}", style="white")
            reply = response.content[0].text.strip() if response.content else ""
            return reply

        except Exception as e:
            error_msg = f"Error with Anthropic API: {e}"
            console.print(error_msg, style="red")
            raise APICallError(error_msg) from e

    def call_llm(self, prompt: str, model_provider: str = None, model: str = None,
                 chat_history: list = None, system_prompt: str = None) -> str:
        """
        Attempts to call the preferred LLM provider (if available), else falls back to any available one.
        
        Args:
            prompt: The user prompt
            model_provider: Preferred provider ("openai", "groq", or "anthropic")
            model: Specific model name
            chat_history: List of previous messages
            system_prompt: System prompt
            
        Returns:
            str: The model's response
            
        Raises:
            ModelProviderNotAvailableError: If no providers are available
            APICallError: If all API calls fail
        """
        if chat_history is None:
            chat_history = []

        if not self.clients:
            raise ModelProviderNotAvailableError("No available model providers. Please configure an API key.")

        def call_provider(provider: str) -> str:
            if provider == "openai":
                return self.call_openai_gpt(prompt, model, chat_history=chat_history, system_prompt=system_prompt)
            elif provider == "groq":
                return self.call_groq(prompt, model, chat_history=chat_history, system_prompt=system_prompt)
            elif provider == "anthropic":
                return self.call_anthropic(prompt, model, chat_history=chat_history, system_prompt=system_prompt)

        requested = model_provider.lower() if model_provider else None

        # Try requested provider first
        if requested and requested in self.clients:
            try:
                return call_provider(requested)
            except APICallError as e:
                console.print(f"Failed to use requested provider '{requested}': {e}", style="yellow")
                console.print("Attempting fallback to other providers...", style="yellow")
        elif requested:
            console.print(f"Model provider '{requested}' not available. Available providers: {list(self.clients.keys())}", style="yellow")

        # Fallback to any available provider
        last_error = None
        for provider in self.clients:
            if provider == requested:  # Skip if we already tried it
                continue
                
            try:
                console.print(f"Using fallback model provider '{provider}'", style="yellow")
                return call_provider(provider)
            except APICallError as e:
                console.print(f"Fallback provider '{provider}' failed: {e}", style="yellow")
                last_error = e
                continue

        # If we get here, all providers failed
        error_msg = f"All available providers failed. Last error: {last_error}"
        console.print(error_msg, style="red")
        raise APICallError(error_msg)

    def get_available_providers(self) -> list:
        """
        Returns a list of available providers.
        
        Returns:
            list: List of available provider names
        """
        return list(self.clients.keys())

    def is_provider_available(self, provider: str) -> bool:
        """
        Check if a specific provider is available.
        
        Args:
            provider: Provider name to check
            
        Returns:
            bool: True if provider is available, False otherwise
        """
        return provider.lower() in self.clients