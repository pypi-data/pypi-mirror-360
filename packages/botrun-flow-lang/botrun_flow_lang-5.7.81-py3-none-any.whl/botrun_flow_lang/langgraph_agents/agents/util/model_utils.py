"""
Utility module for LLM model-related functionality, including API key rotation.
"""

import random
from langchain_anthropic import ChatAnthropic


class RotatingChatAnthropic:
    """A wrapper class for ChatAnthropic that rotates through multiple API keys."""

    def __init__(self, model_name, keys, temperature=0, max_tokens=8192):
        """
        Initialize the rotating key model.

        Args:
            model_name: The name of the Anthropic model to use
            keys: List of API keys to rotate through
            temperature: The temperature for model generation
            max_tokens: The maximum number of tokens to generate
        """
        self.keys = keys
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize with the first key
        self.base_model = ChatAnthropic(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            api_key=random.choice(self.keys) if self.keys else None,
        )

    def invoke(self, *args, **kwargs):
        """
        Invoke the model with a randomly selected API key.

        This method is called when the model is invoked through LangChain.
        """
        if self.keys:
            # Select a random key for this invocation
            self.base_model.client.api_key = random.choice(self.keys)
        return self.base_model.invoke(*args, **kwargs)

    def stream(self, *args, **kwargs):
        """
        Stream the model response with a randomly selected API key.

        This method handles streaming output from the model.
        """
        if self.keys:
            # Select a random key for this streaming invocation
            self.base_model.client.api_key = random.choice(self.keys)
        return self.base_model.stream(*args, **kwargs)

    def __getattr__(self, name):
        """
        Forward any other attribute access to the base model.

        This ensures compatibility with the original ChatAnthropic class.
        """
        return getattr(self.base_model, name)
