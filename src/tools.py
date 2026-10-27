import os
import subprocess


def _decode_output(output: bytes) -> str:
    """Prefer UTF-8, then the Windows console encoding for legacy commands."""
    try:
        return output.decode("utf-8")
    except UnicodeDecodeError:
        if os.name == "nt":
            import ctypes

            code_page = ctypes.windll.kernel32.GetConsoleOutputCP()
            if not code_page:
                code_page = ctypes.windll.kernel32.GetOEMCP()
            return output.decode(f"cp{code_page}", errors="replace")
        return output.decode("utf-8", errors="replace")

def run_bash(command: str) -> str:
    """Run a command in the platform's default subprocess shell and return its output."""
    try:
        command_result = subprocess.run(command, shell=True, capture_output=True, timeout=120)
        stdout = _decode_output(command_result.stdout)
        stderr = _decode_output(command_result.stderr)
        out = stdout + (f"\nSTDERR:\n{stderr}" if stderr else "")
        return f"Exit code: {command_result.returncode}\n{out}"
    except subprocess.TimeoutExpired:
        return "Error: command timed out after 120s"


tools = {"bash": run_bash}
