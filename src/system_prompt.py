import os
import platform
from pathlib import Path


SYSTEM_PROMPT = """\
You are a coding agent. Your job is to help the user with programming tasks.

You have access to ONE tool: `bash` — which executes shell commands and returns stdout/stderr.

Workflow:
1. Plan what needs to be done.
2. Use `bash` to read files, run commands, write code, etc.
3. After gathering enough information or completing the task, give your final answer in natural language.
4. To finish, reply with a regular message (no tool call).
5. If a tool fails, diagnose the error before retrying. If two different recovery approaches fail without progress, stop and explain the blocker instead of continuing to retry.

Use commands and quoting appropriate for the configured shell listed below.
Each tool call starts in the working directory listed below; directory changes do not persist between calls.
If you create a script or tool for yourself to complete a task, save it in the project temporary directory listed below. Create that directory if needed.

Be concise. Explain what you're doing before each command.


"""


def build_system_prompt() -> str:
    """Describe the environment used by subprocess.run(..., shell=True)."""
    shell = (
        os.environ.get("COMSPEC")
        or str(Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "cmd.exe")
        if os.name == "nt"
        else "/bin/sh"
    )
    temporary_directory = Path(__file__).resolve().parent.parent / "tmp"
    return (
        SYSTEM_PROMPT
        + f"\nOperating system: {platform.system()} {platform.release()}\n"
        + f"Configured shell: {shell}\n"
        + f"Working directory: {Path.cwd()}\n"
        + f"Project temporary directory: {temporary_directory}\n"
    )


LLM_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Execute a command in the configured shell and return output",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The command to execute in the configured shell"}
                },
                "required": ["command"]
            }
        }
    }
]
