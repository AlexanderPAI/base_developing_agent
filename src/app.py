import json, sys, subprocess, os, logging

from dotenv import load_dotenv

from openrouter import OpenRouter

from src.config import config
from src.tools import run_bash
from src.system_prompt import SYSTEM_PROMPT, LLM_TOOLS

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()


# client = Client(host="http://localhost:11434")
client = OpenRouter(api_key=config.llm_api_key)


def call_tool(name: str, arguments: dict) -> str:
    func = {"bash": run_bash}.get(name)
    if not func:
        return f"Error: unknown tool: {name}"
    try:
        return func(**arguments)
    except Exception as e:
        return f"Error: calling {name}: {e}"


def call_llm(messages, client: OpenRouter):
    response = client.chat.send(
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


def agent_loop(user_message: str) -> None:
    messages: list[dict[str, object]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    for turn in range(1, config.max_turns + 1):
        print(f"\n{'=' * 60}\n🔄 Turn {turn}\n{'=' * 60}")
        content, tool_calls = call_llm(messages, client)
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
            result = call_tool(function, arguments)
            print(f"   → {result[:500]}{'...' if len(result)>500 else ''}")
            messages.append({"role": "tool", "tool_call_id": tool_call_id, "content": result})
    print(f"\n⚠️  Max turns ({config.max_turns}) reached. Stopping.")

if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    if not prompt.strip():
        print("No task provided. Exiting.")
        sys.exit(1)
    agent_loop(prompt)
