from typing import Callable, Optional

from ollama import Client
from openrouter import OpenRouter

from src.config import config
from src.system_prompt import SYSTEM_PROMPT, LLM_TOOLS

class AgentCore:
    """Agent core class"""
    CLIENTS = {
        "ollama": Client(host="http://localhost:11434"), # todo Сделать адаптер для консистентности, ollama пока не будет работать
        "open_router": OpenRouter(api_key=config.llm_api_key)
    }


    def __init__(self, tools: Optional[dict[str, Callable[..., str]]] = None, client: Optional[OpenRouter] = None) -> None:
        self.client = client if client else OpenRouter(api_key=config.llm_api_key)
        self.tools: dict[str, Callable[..., str]] = (
            tools if tools is not None else {}
        )

    def call_tool(self, name: str, arguments: dict) -> str:
        """Call a tool"""
        func = self.tools.get(name)
        if func is None:
            return f"No such tool: {name}"
        try:
            return func(**arguments)
        except Exception as e:
            return f"Error: calling {name}: {e}"


    def call_llm(self, messages: dict[str, str]):
        """Call a message"""
        response = self.client.chat.send(
            model=config.llm_model,
            messages=messages,
            tools=LLM_TOOLS,
            tool_choice="auto",
            temperature=0.1,
            max_tokens=4096,
            stream=False,
        )

        message = response.choices[0].message

        content = (message.content or "").strip()
        tool_calls = message.tool_calls or []

        return content, tool_calls

