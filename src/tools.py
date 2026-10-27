import subprocess

def run_bash(command: str) -> str:
    """This function runs a bash command and returns the output of the command"""
    try:
        command_result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=120)
        out = command_result.stdout + (f"\nSTDERR:\n{command_result.stderr}" if command_result.stderr else "")
        return f"Exit code: {command_result.returncode}\n{out}"
    except subprocess.TimeoutExpired:
        return "Error: command timed out after 120s"
