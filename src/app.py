import json, sys, subprocess, os, logging

from dotenv import load_dotenv

from openrouter import OpenRouter

from src.config import config
from src.tools import tools
from src.system_prompt import build_system_prompt, LLM_TOOLS
from src.agent_core import AgentCore

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


agent = AgentCore(tools=tools)


def agent_loop(user_message: str) -> None:
    messages: list[dict[str, object]] = [
        {"role": "system", "content": build_system_prompt()},
        {"role": "user", "content": user_message},
    ]

    for turn in range(1, config.max_turns + 1):
        print(f"\n{'=' * 60}\n🔄 Turn {turn}\n{'=' * 60}")
        content, tool_calls = agent.call_llm(messages)
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
            result = agent.call_tool(function, arguments)
            print(f"   → {result[:500]}{'...' if len(result)>500 else ''}")
            messages.append({"role": "tool", "tool_call_id": tool_call_id, "content": result})
    print(f"\n⚠️  Max turns ({config.max_turns}) reached. Stopping.")

if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    if not prompt.strip():
        print("No task provided. Exiting.")
        sys.exit(1)
    agent_loop(prompt)
