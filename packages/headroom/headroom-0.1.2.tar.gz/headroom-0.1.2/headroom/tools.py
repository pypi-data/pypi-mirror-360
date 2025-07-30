# CLI command tools

import time
import subprocess
import sys

def execute_command(command: str, stream_output: bool = True) -> dict:
    """
    Executes a shell command.
    If stream_output is True, output is streamed to the terminal in real-time.
    Returns a dict with 'success' and 'output' keys.
    """
    # OS check: Allow on Linux, macOS, and Windows
    if not (sys.platform.startswith("linux") or sys.platform == "darwin" or sys.platform.startswith("win")):
        return {"success": False, "output": "Shell command execution is only supported on Linux, macOS, or Windows."}

    process = None
    output_lines = []
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1 # Line-buffered output
        )

        if stream_output:
            # Stream output in real-time
            while True:
                stdout_line = process.stdout.readline() if process.stdout else ''
                stderr_line = process.stderr.readline() if process.stderr else ''

                if stdout_line:
                    print(stdout_line, end='')
                    output_lines.append(stdout_line)
                if stderr_line:
                    print(stderr_line, end='')
                    output_lines.append(stderr_line)

                if not stdout_line and not stderr_line and process.poll() is not None:
                    break
                
                # Avoid busy-waiting
                if process.poll() is None and not stdout_line and not stderr_line:
                    time.sleep(0.05) # Small delay to prevent 100% CPU usage

            # Ensure all output is collected after process finishes
            remaining_stdout, remaining_stderr = process.communicate()
            if remaining_stdout:
                print(remaining_stdout, end='')
                output_lines.append(remaining_stdout)
            if remaining_stderr:
                print(remaining_stderr, end='')
                output_lines.append(remaining_stderr)
        else:
            # Just collect output without streaming
            remaining_stdout, remaining_stderr = process.communicate()
            if remaining_stdout:
                output_lines.append(remaining_stdout)
            if remaining_stderr:
                output_lines.append(remaining_stderr)

        full_output = "".join(output_lines)
        success = process.returncode == 0

        if not success:
            if "Unable to locate package" in full_output or "not found" in full_output:
                return {"success": False, "output": f"Command failed: {full_output}\n\nSuggestion: The package might not exist or the package lists are outdated. Try running `sudo apt update` and then try installing the package again. Also, double-check the package name for typos."}
            else:
                return {"success": False, "output": f"Command failed: {full_output}"}
        else:
            return {"success": True, "output": full_output}

    except Exception as e:
        if process:
            process.kill() # Ensure process is terminated on error
        return {"success": False, "output": str(e)}
