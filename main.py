import json, sys, subprocess
import requests

from ollama import Client


LLM_BASE_URL = "..."
LLM_API_KEY = "..."
LLM_MODEL = "qwen3.5:9b"
# LLM_HEADERS = {"Content-Type": "application/json", "Authorization": f"Bearer {LLM_API_KEY}"}
LLM_HEADERS = {"Content-Type": "application/json"}
MAX_TURNS = 1000

SYSTEM_PROMPT = """\
You are a coding agent. Your job is to help the user with programming tasks.

You have access to ONE tool: `bash` — which executes shell commands and returns stdout/stderr.

Workflow:
1. Plan what needs to be done.
2. Use `bash` to read files, run commands, write code, etc.
3. After gathering enough information or completing the task, give your final answer in natural language.
4. To finish, reply with a regular message (no tool call).

Be concise. Explain what you're doing before each command."""

LLM_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "powershell",
            "description": "Execute a shell command and return output",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The powershell command to execute"},
                    "required": ["command"]
                }
            }
        }
    }
]


client = Client(host="http://localhost:11434")


def run_bash(command: str) -> str:
    try:
        command_result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=120)
        out = command_result.stdout + (f"\nSTDERR:\n{command_result.stderr}" if command_result.stderr else "")
        return f"Exit code: {command_result.returncode}\n{out}"
    except subprocess.TimeoutExpired:
        return "Error: command timed out after 120s"


def call_tool(name: str, arguments: dict) -> str:
    func = {"powershell": run_bash}.get(name)
    if not func:
        return f"Error: unknown tool: {name}"
    try:
        return func(**arguments)
    except Exception as e:
        return f"Error: calling {name}: {e}"


def call_llm(messages):\
    # payload = {"model": LLM_MODEL, "messages": messages, "tools": LLM_TOOLS, "tool_choices": "auto", "temperature": 0.1, "max_tokens": 4096}

    return client.chat(model=LLM_MODEL, messages=messages)


if __name__ == "__main__":
    user_prompt = "Привет, что ты умеешь?"

    messages = [
        {"role": "user", "content": user_prompt},
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    llm_response = call_llm(messages)
    print(llm_response.message.content)
