import json

from typing import Callable, Optional

from ollama import Client
from openrouter import OpenRouter

from src.config import config
from src.system_prompt import LLM_TOOLS, build_system_prompt


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


    def invoke(self, user_message: str) -> None:
        """Invoke a message"""
        messages: list[dict[str, object]] = [
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": user_message},
        ]

        for turn in range(1, config.max_turns + 1):
            print(f"\n{'=' * 60}\n🔄 Turn {turn}\n{'=' * 60}")
            content, tool_calls = self.call_llm(messages)
            if content:
                print(f"\n🤖 {content}")
            if not tool_calls:
                print("(no text output)" if not content else "")
                print("✅ Agent finished")
                return
            prefix = "\n" if content else ""
            messages.append({
                "role": "assistant",
                "content": content or None,
                "tool_calls": [tool_call.model_dump() for tool_call in tool_calls],
            })
            for tool_call in tool_calls:
                function = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                tool_call_id = tool_call.id
                print(f"{prefix}🔧 Tool: {function}({json.dumps(arguments, ensure_ascii=False)})")
                result = self.call_tool(function, arguments)
                print(f"   → {result[:500]}{'...' if len(result) > 500 else ''}")
                messages.append({"role": "tool", "tool_call_id": tool_call_id, "content": result})
        print(f"\n⚠️  Max turns ({config.max_turns}) reached. Stopping.")
