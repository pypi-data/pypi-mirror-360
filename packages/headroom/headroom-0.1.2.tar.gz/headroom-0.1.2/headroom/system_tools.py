import subprocess
import json
import yaml
import os
import sys
from dotenv import dotenv_values
import glob as py_glob # Import Python's glob module
import re # Import regex module
import shutil

# Define commands for different package managers
PACKAGE_MANAGERS = {
    "apt": {
        "install": "sudo apt update && sudo apt install -y {package_name}",
        "remove": "sudo apt remove -y {package_name}",
        "list": "apt list --installed",
        "search": "apt search {package_name}",
    },
    "yum": {
        "install": "sudo yum install -y {package_name}",
        "remove": "sudo yum remove -y {package_name}",
        "list": "yum list installed",
        "search": "yum search {package_name}",
    },
    "dnf": {
        "install": "sudo dnf install -y {package_name}",
        "remove": "sudo dnf remove -y {package_name}",
        "list": "dnf list installed",
        "search": "dnf search {package_name}",
    },
    "snap": {
        "install": "sudo snap install {package_name}",
        "remove": "sudo snap remove {package_name}",
        "list": "snap list",
        "search": "snap find {package_name}",
    },
    "flatpak": {
        "install": "flatpak install -y flathub {package_name}", # Assuming flathub remote
        "remove": "flatpak uninstall -y {package_name}",
        "list": "flatpak list",
        "search": "flatpak search {package_name}",
    },
}

def detect_package_managers():
    """Detects which package managers are available on the system."""
    available_managers = []
    for manager in PACKAGE_MANAGERS.keys():
        # Use a simple check to see if the command exists
        result = subprocess.run(["which", manager], capture_output=True)
        if result.returncode == 0:
            available_managers.append(manager)
    return available_managers

def _execute_package_command(action, package_name=None, package_manager=None):
    """Helper to find the correct package manager and execute the command."""
    if sys.platform != "linux":
        return {"success": False, "output": "Package management tools are only supported on Linux."}

    if package_manager and package_manager not in PACKAGE_MANAGERS:
        return {"success": False, "output": f"Unsupported package manager specified: {package_manager}. Available managers: {list(PACKAGE_MANAGERS.keys())}"}

    managers_to_try = [package_manager] if package_manager else detect_package_managers()

    if not managers_to_try:
        return {"success": False, "output": "No supported package managers found on this system."}

    for manager in managers_to_try:
        if manager in PACKAGE_MANAGERS and action in PACKAGE_MANAGERS[manager]:
            command_template = PACKAGE_MANAGERS[manager][action]
            command = command_template.format(package_name=package_name) if package_name else command_template
            print(f"Attempting to use {manager} with command: {command}") # Log which manager is being used
            result = _run_command(command)
            if result["success"]:
                return {"success": True, "output": f"Using {manager}:\n{result['output']}"}
            else:
                 print(f"Command failed with {manager}: {result['output']}") # Log failure for this manager
                # If a specific manager was requested, return its failure directly
                 if package_manager:
                     return {"success": False, "output": f"Failed to execute command with {manager}: {result['output']}"}
                # Otherwise, try the next available manager
                 continue
        elif manager: # If manager was specified but action not found
             return {"success": False, "output": f"Action '{action}' is not supported by the '{manager}' package manager."}

    return {"success": False, "output": f"Failed to execute '{action}' for package '{package_name}' (or general listing/search) with any available package manager. Last attempt output: {result.get('output', 'N/A')}"}

def install_package(package_name: str, package_manager: str = None):
    """Installs a package using a specified or detected package manager."""
    return _execute_package_command("install", package_name=package_name, package_manager=package_manager)

def remove_package(package_name: str, package_manager: str = None):
    """Removes a package using a specified or detected package manager."""
    return _execute_package_command("remove", package_name=package_name, package_manager=package_manager)


def create_and_run_python_script(filename, code):
    """Creates and executes a Python script."""
    try:
        with open(filename, "w") as f:
            f.write(code)
        
        command_to_run_script = f"{sys.executable} {filename}"
        result = _run_command(command_to_run_script)
        
        if not result.get("success"):
            return {"success": False, "output": f"Script execution failed: {result['output']}"}
        else:
            return {"success": True, "output": result["output"]}
    except Exception as e:
        return {"success": False, "output": str(e)}

def _run_command(command):
    """Helper to run a shell command and return success status and output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=False,
            timeout=60
        )
        return {"success": result.returncode == 0, "output": result.stdout + result.stderr}
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "Command timed out."}
    except Exception as e:
        return {"success": False, "output": str(e)}

def list_packages(package_manager: str = None):
    """Lists installed packages using a specified or detected package manager."""
    return _execute_package_command("list", package_manager=package_manager)

def search_package(package_name: str, package_manager: str = None):
    """Searches for a package using a specified or detected package manager."""
    return _execute_package_command("search", package_name=package_name, package_manager=package_manager)

def check_command_exists(command_name):
    """Checks if a given shell command is available in the system's PATH."""
    result = _run_command(f"command -v {command_name}")
    return {"exists": result["success"], "path": result["output"].strip()}

def get_package_version(package_name, package_manager):
    """Gets the version of an installed package using a specified package manager."""
    import sys
    if sys.platform != "linux":
        return {"success": False, "output": "This tool is only supported on Linux."}
    if package_manager == "apt":
        result = _run_command(f"dpkg -s {package_name} | grep Version")
        if result["success"]:
            return {"success": True, "version": result["output"].split(": ")[1].strip()}
        else:
            return {"success": False, "output": f"Package {package_name} not found or version could not be determined."}
    elif package_manager == "npm":
        result = _run_command(f"npm list -g {package_name} --depth=0")
        if result["success"] and package_name in result["output"]:
            version_line = [line for line in result["output"].splitlines() if package_name in line and "@" in line]
            if version_line:
                version = version_line[0].split("@")[1].strip()
                return {"success": True, "version": version}
            else:
                return {"success": False, "output": f"Package {package_name} found but version could not be parsed."}
        else:
            return {"success": False, "output": f"Package {package_name} not found globally."}
    else:
        return {"success": False, "output": f"Unsupported package manager: {package_manager}"}

def check_service_status(service_name):
    """Checks the status of a systemd service."""
    import sys
    if sys.platform != "linux":
        return {"success": False, "output": "This tool is only supported on Linux."}
    result = _run_command(f"systemctl is-active {service_name}")
    status = result["output"].strip()
    return {"success": result["success"], "status": status, "output": result["output"]}

def manage_service(service_name, action):
    """Performs actions (start, stop, restart, enable, disable) on a systemd service."""
    import sys
    if sys.platform != "linux":
        return {"success": False, "output": "This tool is only supported on Linux."}
    if action not in ["start", "stop", "restart", "enable", "disable"]:
        return {"success": False, "output": "Invalid service action."}
    
    command = f"sudo systemctl {action} {service_name}"
    result = _run_command(command)
    return {"success": result["success"], "output": result["output"]}

def read_json_file(file_path):
    """Reads and parses a JSON file."""
    try:
        with open(file_path, "r") as f:
            content = json.load(f)
        return {"success": True, "content": content}
    except FileNotFoundError:
        return {"success": False, "output": f"File not found: {file_path}"}
    except json.JSONDecodeError:
        return {"success": False, "output": f"Invalid JSON in file: {file_path}"}
    except Exception as e:
        return {"success": False, "output": str(e)}

def write_json_file(file_path, content):
    """Writes content to a JSON file."""
    try:
        with open(file_path, "w") as f:
            json.dump(content, f, indent=4)
        return {"success": True, "output": f"Successfully wrote to {file_path}"}
    except Exception as e:
        return {"success": False, "output": str(e)}

def update_json_file(file_path, key_path, value):
    """Updates a specific key in a JSON file. key_path can be dot-separated for nested keys."""
    result = read_json_file(file_path)
    if not result["success"]:
        return result # Return error from read_json_file

    data = result["content"]
    keys = key_path.split(".")
    current = data
    for i, key in enumerate(keys):
        if i == len(keys) - 1:
            current[key] = value
        else:
            if not isinstance(current, dict) or key not in current:
                return {"success": False, "output": f"Key path not found or invalid: {key_path}"}
            current = current[key]
    
    return write_json_file(file_path, data)

def read_yaml_file(file_path):
    """Reads and parses a YAML file."""
    try:
        with open(file_path, "r") as f:
            content = yaml.safe_load(f)
        return {"success": True, "content": content}
    except FileNotFoundError:
        return {"success": False, "output": f"File not found: {file_path}"}
    except yaml.YAMLError:
        return {"success": False, "output": f"Invalid YAML in file: {file_path}"}
    except Exception as e:
        return {"success": False, "output": str(e)}

def write_yaml_file(file_path, content):
    """Writes content to a YAML file."""
    try:
        with open(file_path, "w") as f:
            yaml.safe_dump(content, f, indent=2)
        return {"success": True, "output": f"Successfully wrote to {file_path}"}
    except Exception as e:
        return {"success": False, "output": str(e)}

def update_yaml_file(file_path, key_path, value):
    """Updates a specific key in a YAML file. key_path can be dot-separated for nested keys."""
    result = read_yaml_file(file_path)
    if not result["success"]:
        return result # Return error from read_yaml_file

    data = result["content"]
    keys = key_path.split(".")
    current = data
    for i, key in enumerate(keys):
        if i == len(keys) - 1:
            current[key] = value
        else:
            if not isinstance(current, dict) or key not in current:
                return {"success": False, "output": f"Key path not found or invalid: {key_path}"}
            current = current[key]
    
    return write_yaml_file(file_path, data)

def read_env_file(file_path):
    """Reads and parses a .env file."""
    try:
        content = dotenv_values(file_path)
        return {"success": True, "content": content}
    except FileNotFoundError:
        return {"success": False, "output": f"File not found: {file_path}"}
    except Exception as e:
        return {"success": False, "output": str(e)}

def update_env_file(file_path, key, value):
    """Updates a key-value pair in a .env file. Creates the file if it doesn't exist."""
    try:
        # Read existing .env file content
        lines = []
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                lines = f.readlines()

        updated = False
        new_lines = []
        for line in lines:
            if line.strip().startswith(f"{key}="):
                new_lines.append(f"{key}={value}\n")
                updated = True
            else:
                new_lines.append(line)
        
        if not updated:
            new_lines.append(f"{key}={value}\n")

        with open(file_path, "w") as f:
            f.writelines(new_lines)
        
        return {"success": True, "output": f"Successfully updated {key} in {file_path}"}
    except Exception as e:
        return {"success": False, "output": str(e)}

def parse_cpu_usage():
    """Gets and parses CPU utilization."""
    if sys.platform != "linux":
        return {"success": False, "output": "CPU usage parsing is only supported on Linux."}
    result = _run_command("top -bn1 | grep 'Cpu(s)'")
    if result["success"]:
        try:
            cpu_line = result["output"].strip()
            # Example: %Cpu(s):  0.0 us,  0.0 sy,  0.0 ni, 100.0 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
            parts = cpu_line.split(':')[1].strip().split(',')
            us = float(parts[0].strip().replace('us', ''))
            sy = float(parts[1].strip().replace('sy', ''))
            id = float(parts[3].strip().replace('id', ''))
            
            total_cpu_usage = us + sy
            return {"success": True, "output": f"CPU Utilization: {total_cpu_usage:.1f}% (User: {us:.1f}%, System: {sy:.1f}%, Idle: {id:.1f}%)"}
        except Exception as e:
            return {"success": False, "output": f"Failed to parse CPU usage: {e}. Raw output: {result["output"]}"}
    else:
        return {"success": False, "output": f"Failed to get CPU usage: {result["output"]}"}

def parse_memory_usage():
    """Gets and parses memory usage."""
    if sys.platform != "linux":
        return {"success": False, "output": "Memory usage parsing is only supported on Linux."}
    result = _run_command("free -h | head -n 2")
    if result["success"]:
        try:
            mem_line = result["output"].splitlines()[1]
            # Example: Mem:            15Gi       1.7Gi        12Gi        20Mi       1.5Gi        13Gi
            parts = mem_line.split()
            total = parts[1]
            used = parts[2]
            free = parts[3]
            return {"success": True, "output": f"Memory Usage: Total: {total}, Used: {used}, Free: {free}"}
        except Exception as e:
            return {"success": False, "output": f"Failed to parse memory usage: {e}. Raw output: {result["output"]}"}
    else:
        return {"success": False, "output": f"Failed to get memory usage: {result["output"]}"}

def git_status():
    """Runs git status and returns the output."""
    result = _run_command("git status")
    return result

def git_diff():
    """Runs git diff and returns the output."""
    result = _run_command("git diff")
    return result

def git_commit(message: str):
    """Runs git commit with the given message."""
    result = _run_command(f"git commit -m \"{message}\"")
    return result

def list_directory(path: str):
    """Lists the contents of a directory, distinguishing between files and directories."""
    try:
        items = os.listdir(path)
        output = []
        for item in items:
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                output.append(f"[DIR] {item}")
            else:
                output.append(f"[FILE] {item}")
        return {"success": True, "output": "\n".join(output)}
    except FileNotFoundError:
        return {"success": False, "output": f"Directory not found: {path}"}
    except Exception as e:
        return {"success": False, "output": str(e)}

def search_file_content(pattern: str, path: str = ".", include: str = "*"):
    """Searches for a regex pattern within file contents in a specified directory."""
    try:
        # Use find and grep for efficiency, especially in large directories
        command = f"find {path} -name \"{include}\" -type f -print0 | xargs -0 grep -n -E \"{pattern}\""
        result = _run_command(command)
        if result["success"]:
            return {"success": True, "output": result["output"]}
        else:
            # grep returns non-zero exit code if no matches are found, which is not an error
            if "No such file or directory" in result["output"] or "Is a directory" in result["output"]:
                return {"success": False, "output": f"Error searching: {result["output"]}"}
            else:
                return {"success": True, "output": "No matches found."}
    except Exception as e:
        return {"success": False, "output": str(e)}

def glob_files(pattern: str, path: str = "."):
    """Finds files matching a glob pattern within a specified directory."""
    try:
        # os.path.join is important for constructing the full path for glob
        full_pattern = os.path.join(path, pattern)
        files = py_glob.glob(full_pattern, recursive=True)
        if files:
            return {"success": True, "output": "\n".join(files)}
        else:
            return {"success": True, "output": "No files found matching the pattern."}
    except Exception as e:
        return {"success": False, "output": str(e)}

def replace_in_file(file_path: str, old_string: str, new_string: str, expected_replacements: int = 1):
    """Replaces occurrences of old_string with new_string in a file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Use re.sub for replacement to handle potential regex in old_string if needed
        # For now, treating as literal string replacement
        replaced_content, num_replacements = re.subn(re.escape(old_string), new_string, content)

        if num_replacements == 0:
            return {"success": False, "output": f"No occurrences of '{old_string}' found in '{file_path}'."}
        elif expected_replacements is not None and num_replacements != expected_replacements:
            return {"success": False, "output": f"Expected {expected_replacements} replacements but found {num_replacements} in '{file_path}'."}

        with open(file_path, 'w') as f:
            f.write(replaced_content)
        
        return {"success": True, "output": f"Successfully replaced {num_replacements} occurrences in '{file_path}'."}
    except FileNotFoundError:
        return {"success": False, "output": f"File not found: {file_path}"}
    except Exception as e:
        return {"success": False, "output": str(e)}

def web_search(query: str) -> dict:
    return {"success": False, "output": "Web search is not implemented yet. This is a placeholder."}

def web_fetch(url: str):
    return {"success": False, "output": "Web fetch functionality is not yet implemented. This is a placeholder."}

def copy_file(src, dst, recursive=False):
    """Copies a file or directory to a new location."""
    try:
        if recursive:
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        return {"success": True, "output": f"Copied {src} to {dst}"}
    except FileNotFoundError:
        return {"success": False, "output": f"Error: Source not found: {src}"}
    except PermissionError:
        return {"success": False, "output": f"Error: Permission denied to copy {src} to {dst}. Run Max with necessary privileges."}
    except IsADirectoryError as e:
         return {"success": False, "output": f"Error: Destination {dst} is a directory. {e}"}
    except Exception as e:
        return {"success": False, "output": str(e)}

def move_file(src, dst):
    """Moves a file or directory to a new location."""
    try:
        shutil.move(src, dst)
        return {"success": True, "output": f"Moved {src} to {dst}"}
    except FileNotFoundError:
        return {"success": False, "output": f"Error: Source not found for move: {src}"}
    except PermissionError:
        return {"success": False, "output": f"Error: Permission denied to move {src} to {dst}. Run Max with necessary privileges."}
    except Exception as e:
        return {"success": False, "output": str(e)}

def make_directory(path, exist_ok=True):
    """Creates a new directory."""
    try:
        os.makedirs(path, exist_ok=exist_ok)
        return {"success": True, "output": f"Directory created: {path}"}
    except Exception as e:
        return {"success": False, "output": str(e)}

def delete_file(path):
    """Deletes a file."""
    try:
        os.remove(path)
        return {"success": True, "output": f"File removed: {path}"}
    except Exception as e:
        return {"success": False, "output": str(e)}

def remove_directory(path, recursive=False):
    """Removes a directory."""
    try:
        if not os.path.isdir(path):
             return {"success": False, "output": f"Error: Path is not a directory: {path}. Use delete_file to remove files."}

        if recursive:
            shutil.rmtree(path)
        else:
            # os.rmdir only removes empty directories
            if os.path.isfile(path):
                 os.remove(path)
                 return {"success": True, "output": f"File removed: {path}"}
            else: # Assume it's a directory
                os.rmdir(path)
        return {"success": True, "output": f"Removed: {path} (recursive: {recursive})"}
    except FileNotFoundError:
        return {"success": False, "output": f"Error: Path not found for removal: {path}"}
    except PermissionError:
        return {"success": False, "output": f"Error: Permission denied to remove {path}. Run Max with necessary privileges."}
    except OSError as e:
         if "Directory not empty" in str(e) and not recursive:
             return {"success": False, "output": f"Error: Directory not empty: {path}. Use 'recursive=True' to remove contents."}
         return {"success": False, "output": f"Error removing {path}: {str(e)}"}
    except Exception as e:
        return {"success": False, "output": str(e)}

def change_permissions(path, mode):
    """Changes the permissions of a file or directory."""
    try:
        os.chmod(path, int(mode, 8))
        return {"success": True, "output": f"Permissions changed for {path} to {mode}"}
    except Exception as e:
        return {"success": False, "output": str(e)}

def change_owner(path, owner):
    """Changes the owner of a file or directory."""
    try:
        subprocess.check_call(['chown', owner, path])
        return {"success": True, "output": f"Owner changed for {path} to {owner}"}
    except Exception as e:
        return {"success": False, "output": str(e)}

if sys.platform.startswith("linux"):
    # Linux-specific code
    pass
elif sys.platform == "win32":
    # Windows-specific code
    pass
else:
    # Fallback or error
    pass