from enum import Enum
from pydantic import BaseModel
from dotenv import load_dotenv
import os
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
typhoon_api_key = os.getenv("TYPHOON_API_KEY")


class ModelName(Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    CLAUDE = "claude"
    TYPHOON = "typhoon"


class LLM:
    def __init__(self, model_name: ModelName, temperature: float = 0, model_version: str = None):
        """
        Initialize an LLM instance with the specified model provider.

        Args:
            model_name: The provider name ("openai", "gemini", or "claude")
            temperature: Controls randomness in responses (0.0 to 1.0)
            model_version: Specific model version to use (if None, uses default)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.model_version = model_version
        self.model = self._initialize_model()

    def _initialize_model(self):
        """Initialize and return the appropriate LLM based on model_name."""
        if self.model_name == "openai":
            from langchain_openai import ChatOpenAI
            model_version = self.model_version or "gpt-4o-mini"
            return ChatOpenAI(temperature=self.temperature, model=model_version, api_key=openai_api_key)

        elif self.model_name == "gemini":
            from langchain_google_genai import ChatGoogleGenerativeAI
            model_version = self.model_version or "gemini-1.5-flash"
            return ChatGoogleGenerativeAI(temperature=self.temperature, model=model_version, api_key=gemini_api_key)

        elif self.model_name == "claude":
            from langchain_anthropic import ChatAnthropic
            model_version = self.model_version or "claude-3-sonnet-20240229"
            return ChatAnthropic(temperature=self.temperature, model=model_version, api_key=anthropic_api_key)

        elif self.model_name == "typhoon":
            from langchain_openai import ChatOpenAI
            model_version = self.model_version or "typhoon-v2-70b-instruct"
            return ChatOpenAI(temperature=self.temperature, model=model_version, api_key=typhoon_api_key, base_url='https://api.opentyphoon.ai/v1')

        else:
            raise ValueError(
                f"Unsupported model: {self.model_name}. Choose from 'openai', 'gemini', or 'claude'")

    def with_structured_output(self, schema: BaseModel):
        return self.model.with_structured_output(schema)

    def invoke(self, prompt: str):
        return self.model.invoke(prompt)
