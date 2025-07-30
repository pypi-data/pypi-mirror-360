import os
from abc import ABCMeta, abstractmethod
from typing import TypeAlias

import constants
import httpx
from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from openai import AsyncOpenAI, DefaultAsyncHttpxClient

ModelProvider: TypeAlias = None | AsyncOpenAI | AsyncAnthropic

load_dotenv()


class ClientBrand(metaclass=ABCMeta):
    def __init__(self, name: str):
        self.name: str = name
        self.error_messages: list[str] = []

    @abstractmethod
    def get_client(self) -> ModelProvider:
        pass

    def get_error_messages(self):
        return self.error_messages

    def __repr__(self) -> str:
        return self.name


class ClientAnthopicBrand(ClientBrand):
    def __init__(self):
        super().__init__("ClientAnthopicBrand")
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            self.client = None
            self.error_messages.append("Please set ANTHROPIC_API_KEY variable")
        else:
            self.client: ModelProvider = AsyncAnthropic(api_key=api_key)

    def get_client(self) -> ModelProvider:
        return self.client


class ClientCrilBrand(ClientBrand):
    def __init__(self):
        super().__init__("ClientCrilBrand")
        api_key = os.getenv("LLM_API_KEY")
        if not api_key:
            self.client = None
            self.error_messages.append("Please set LLM_API_KEY variable")
        else:
            self.client: ModelProvider = AsyncOpenAI(
                base_url=constants.BASE_CRIL_URL,
                api_key=api_key,
                http_client=DefaultAsyncHttpxClient(
                    proxy=None,
                    transport=httpx.AsyncHTTPTransport(local_address="0.0.0.0"),
                ),
            )

    def get_client(self) -> ModelProvider:
        return self.client


class ClientGPTBrand(ClientBrand):
    def __init__(self):
        super().__init__("ClientGPTBrand")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.client = None
            self.error_messages.append("Please set OPENAI_API_KEY variable")
        else:
            self.client: ModelProvider = AsyncOpenAI(api_key=api_key)

    def get_client(self) -> ModelProvider:
        return self.client


class ClientGoogleBrand(ClientBrand):
    def __init__(self):
        super().__init__("ClientGoogleBrand")
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            self.client = None
            self.error_messages.append("Please set GOOGLE_API_KEY variable")
        else:
            self.client: ModelProvider = AsyncOpenAI(
                base_url=constants.BASE_GOOGLE_GEMINI_URL,
                api_key=api_key,
            )

    def get_client(self) -> ModelProvider:
        return self.client
