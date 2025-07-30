# Helper Functions

import json
import shutil
from datetime import datetime, timedelta, timezone
import os
import platform
import yaml
import requests
import subprocess # Added for system checks
from dotenv import load_dotenv
import re
from pathlib import Path

def get_user_config_dir() -> Path:
    """Returns the path to the user-specific config directory."""
    return Path.home() / ".config" / "headroom"

def get_user_data_dir() -> Path:
    """Returns the path to the user-specific data directory."""
    return Path.home() / ".local" / "share" / "headroom"

def load_config() -> dict | None:
    # Load environment variables from .env file
    load_dotenv()

    config_dir = get_user_config_dir()
    config_file = config_dir / "config.yaml"

    # If the user config file doesn't exist, create it from the packaged default.
    if not config_file.exists():
        try:
            config_dir.mkdir(parents=True, exist_ok=True)
            # This path assumes the default config is packaged with the app
            default_config_path = Path(__file__).parent / "config.yaml"
            shutil.copy(default_config_path, config_file)
            print(f"Created default configuration at: {config_file}")
        except Exception as e:
            print(f"Error creating default config: {e}")
            return None

    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

            # Set defaults for conversation settings if not specified
            conversation_settings = {
                'max_entries': 10,
                'max_age_hours': 24
            }
            config['conversation'] = {**conversation_settings, **(config.get('conversation', {}))}

        # Load Ollama settings from environment variables
        ollama_endpoint = os.getenv("OLLAMA_ENDPOINT")
        ollama_model = os.getenv("OLLAMA_MODEL")

        if not ollama_endpoint or not ollama_model:
            print("Error: OLLAMA_ENDPOINT and OLLAMA_MODEL must be set in your .env file.")
            return None

        config['ollama'] = {'endpoint': ollama_endpoint, 'model': ollama_model}

        return config
        
    except yaml.YAMLError as e:
        print(f"Error loading configuration: {e}")
        return None

def load_conversation_history(config: dict) -> list:
    data_dir = get_user_data_dir()
    history_file = data_dir / "conversation_history.json"
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        with open(history_file, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_conversation_history(history: list, config: dict) -> None:
    data_dir = get_user_data_dir()
    history_file = data_dir / "conversation_history.json"

    # Create backup before saving
    if history_file.exists():
        shutil.copy2(history_file, f"{history_file}.backup")

    data_dir.mkdir(parents=True, exist_ok=True)
    with open(history_file, "w") as f:
        json.dump(history, f)

def truncate_history(history: list, max_entries: int = 10) -> list:
    return history[-max_entries:] if len(history) > max_entries else history

def prune_old_entries(history: list, max_age_hours: int = 24) -> list:
    now = datetime.now(timezone.utc)
    pruned = []
    for entry in history:
        ts = entry.get("timestamp")
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            age = now - dt.astimezone(timezone.utc)
            if age <= timedelta(hours=max_age_hours):
                pruned.append(entry)
        except Exception:
            continue
    return pruned

def _check_tool_exists(tool_name: str) -> bool:
    try:
        subprocess.run(["which", tool_name], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_system_context_str() -> str:
    import platform, getpass, socket
    context = []
    os_name = platform.system()
    if os_name == 'Linux':
        try:
            release_info = platform.freedesktop_os_release()
            os_pretty = release_info.get('PRETTY_NAME', 'Linux')
        except Exception:
            os_pretty = f"Linux ({platform.release()})"
    else:
        os_pretty = f"{os_name} {platform.release()}"
    context.append(f"OS: {os_pretty}")
    context.append(f"Architecture: {platform.machine()}")
    context.append(f"Python version: {platform.python_version()}")
    context.append(f"Current directory: {os.getcwd()}")
    context.append(f"User: {getpass.getuser()}")
    # Add tool presence
    from utils import _check_tool_exists
    tools = ["node", "npm", "yarn", "docker", "git", "python3", "pip", "systemctl", "apt", "snap", "flatpak"]
    tool_status = ", ".join(f"{tool}: {'yes' if _check_tool_exists(tool) else 'no'}" for tool in tools)
    context.append(f"Tools available: {tool_status}")
    return "\n".join(context)

def interpret_user_intent(prompt: str) -> dict | None:
    """
    Interprets simple user prompts to directly map to commands or tools.
    Returns a structured intent dictionary or None if no direct match.
    """
    prompt_lower = prompt.lower().strip()

    # Simple command mappings
    
    if prompt_lower.startswith("show me the contents of"):
        # NOTE: This assumes files are relative to the current working directory.
        # This is more portable than a hardcoded path.
        file_path = prompt_lower.replace("show me the contents of", "").strip().rstrip('.')
        if file_path.endswith(".yaml") or file_path.endswith(".yml"):
            return {"intent": "tool_use", "tool_name": "read_yaml_file", "arguments": {"file_path": file_path}}
        elif file_path.endswith(".json"):
            return {"intent": "tool_use", "tool_name": "read_json_file", "arguments": {"file_path": file_path}}
        elif file_path.endswith(".env"):
            return {"intent": "tool_use", "tool_name": "read_env_file", "arguments": {"file_path": file_path}}
        else:
            # For other file types, just cat it
            return {"intent": "command", "command": "raw_shell_command", "arguments": {"command_string": f"cat {file_path}"}}
    
    if prompt_lower == "what is the current cpu utilization and memory usage of this machine?":
        return {
            "intent": "plan",
            "plan_description": "Retrieve and display current CPU and memory usage.",
            "steps": [
                {
                    "description": "Get CPU utilization",
                    "tool_name": "parse_cpu_usage",
                    "arguments": {}
                },
                {
                    "description": "Get memory usage",
                    "tool_name": "parse_memory_usage",
                    "arguments": {}
                }
            ]
        }
    
    # Pattern for changing max_entries in config.yaml
    if prompt_lower.startswith("change the max_entries to"):
        try:
            value = int(prompt_lower.split("to")[-1].strip())
            return {
                "intent": "tool_use",
                "tool_name": "update_yaml_file",
                "arguments": {
                    "file_path": str(get_user_config_dir() / "config.yaml"),
                    "key_path": "conversation.max_entries",
                    "value": value
                }
            }
        except ValueError:
            pass # Fall through to LLM if parsing fails

    # Patterns for general package management
    # Install package
    match_install = re.search(r"install\s+(?:the\s+)?(?:package\s+)?(.+?)(?:\s+using\s+(apt|yum|dnf|snap|flatpak))?", prompt_lower)
    if match_install:
        package_name = match_install.group(1).strip()
        package_manager = match_install.group(2) # This will be None if not specified
        return {"intent": "tool_use", "tool_name": "install_package", "arguments": {"package_name": package_name, "package_manager": package_manager}}

    # Remove package
    match_remove = re.search(r"(?:remove|uninstall)\s+(?:the\s+)?(?:package\s+)?(.+?)(?:\s+using\s+(apt|yum|dnf|snap|flatpak))?", prompt_lower)
    if match_remove:
        package_name = match_remove.group(1).strip()
        package_manager = match_remove.group(2)
        return {"intent": "tool_use", "tool_name": "remove_package", "arguments": {"package_name": package_name, "package_manager": package_manager}}

    # List packages
    match_list = re.search(r"(?:list|show me)\s+(?:all\s+)?(?:installed\s+)?packages(?:\s+using\s+(apt|yum|dnf|snap|flatpak))?", prompt_lower)
    if match_list:
        package_manager = match_list.group(1)
        return {"intent": "tool_use", "tool_name": "list_packages", "arguments": {"package_manager": package_manager}}

    # Search package
    match_search = re.search(r"search\s+for\s+(?:package\s+)?(.+?)(?:\s+using\s+(apt|yum|dnf|snap|flatpak))?", prompt_lower)
    if match_search:
        package_name = match_search.group(1).strip()
        package_manager = match_search.group(2)
        return {"intent": "tool_use", "tool_name": "search_package", "arguments": {"package_name": package_name, "package_manager": package_manager}}

    # Original specific apt install rule (can be removed or kept for specificity)
    # if prompt_lower.startswith("install a package named"):
    #     package_name = prompt_lower.replace("install a package named", "").strip().replace(".", "")
    #     return {"intent": "tool_use", "tool_name": "install_package", "arguments": {"package_name": package_name, "package_manager": "apt"}} # Explicitly use apt here if rule is kept

    # New patterns for file system operations
    # Copy file/directory
    match_copy = re.search(r"copy\s+(.+?)\s+to\s+(.+?)(?:\s+recursively)?", prompt_lower)
    if match_copy:
        src = match_copy.group(1).strip()
        dst = match_copy.group(2).strip()
        recursive = "recursively" in prompt_lower
        # Assuming absolute paths will be provided by the user or handled by the LLM
        return {"intent": "tool_use", "tool_name": "copy_file", "arguments": {"src": src, "dst": dst, "recursive": recursive}}

    # Move file/directory
    match_move = re.search(r"move\s+(.+?)\s+to\s+(.+)", prompt_lower)
    if match_move:
        src = match_move.group(1).strip()
        dst = match_move.group(2).strip()
        # Assuming absolute paths will be provided by the user or handled by the LLM
        return {"intent": "tool_use", "tool_name": "move_file", "arguments": {"src": src, "dst": dst}}

    # Delete file/directory
    match_delete = re.search(r"delete\s+(.+?)(?:\s+and\s+its\s+contents|\s+recursively)?", prompt_lower)
    if match_delete:
        # Assuming absolute paths will be provided by the user or handled by the LLM
        path = match_delete.group(1).strip().replace('`', '') # Remove backticks if present
        recursive = "and its contents" in prompt_lower or "recursively" in prompt_lower
        
        # Determine if it's likely a directory or file based on recursive flag
        if recursive:
             return {"intent": "tool_use", "tool_name": "remove_directory", "arguments": {"path": path, "recursive": True}}
        else:
            return {"intent": "tool_use", "tool_name": "delete_file", "arguments": {"path": path}}

def load_prompt_template() -> str:
    try:
        # Load from the package directory
        template_path = Path(__file__).parent / "prompt_template.txt"
        with open(template_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return (
            "You are Max, an AI assistant. Use the following conversation history and user prompt to determine intent.\n"
            "Conversation history:\n{history}\nUser prompt:\n{prompt}\n"
        )

def format_command_generation_prompt(prompt: str, history: list, config: dict) -> str:
    template = load_prompt_template()
    available_commands = get_available_tools_summary(config)
    system_context = get_system_context_str()
    history_str = "\n".join([f"User: {h['prompt']}\nMax: {h['response']}" for h in history])
    try:
        return template.format(
            available_commands=available_commands,
            history=history_str,
            prompt=prompt,
            system_context=system_context
        )
    except KeyError as e:
        # Log the error for developers, but do not print to user
        import logging
        logging.error(f"Missing key in prompt template: {e}")
        # Fallback: just use the user prompt
        return prompt

def query_ollama(prompt: str, config: dict) -> str:
    # Load and process conversation history
    history = load_conversation_history(config)
    
    # Prune old entries and truncate if necessary
    history = prune_old_entries(history, config['conversation']['max_age_hours'])
    history = truncate_history(history, config['conversation']['max_entries'])
    
    # Format prompt with context
    full_prompt = format_command_generation_prompt(prompt, history, config)
    
    # print("DEBUG: Full prompt sent to LLM:\n", full_prompt)  # Debugging line
    
    payload = {
        "model": config["ollama"]["model"],
        "prompt": full_prompt,
        "stream": False, # Keep stream false for single JSON response
        # Removed "format": "json" to allow LLM to return plain text if no command is identified.
    }
    
    try:
        response = requests.post(
            config["ollama"]["endpoint"] + "/api/generate", 
            json=payload,
            timeout=60 # Increased to 60 seconds for complex tasks
        )
        
        raw_response_content = response.text.strip()
        
        try:
            # Attempt to parse the response as JSON
            parsed_response = json.loads(raw_response_content)
            result = parsed_response.get("response", "").strip()

            # Try to extract JSON code block from anywhere in the result
            code_block_match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", result)
            if code_block_match:
                json_str = code_block_match.group(1).strip()
            else:
                json_str = result  # fallback to the whole result

            try:
                # Now try to parse the cleaned result as JSON
                result_json = json.loads(json_str)
                intent = result_json.get("intent")
            except Exception:
                intent = None
        except json.JSONDecodeError:
            # If not valid JSON, treat the whole response as a chat response
            result = raw_response_content
            return json.dumps({"intent": "chat", "response": f"LLM returned non-JSON response: {result}"})

        # Save new entry to history
        history.append({
            "session_id": config.get('session_id'),
            "prompt": prompt,
            "response": result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        save_conversation_history(history, config)
        if 'result_json' in locals():
            return json.dumps(result_json)
        else:
            return raw_response_content # Return the raw content for max.py to parse
        
    except requests.exceptions.ConnectionError:
        return json.dumps({"intent": "chat", "response": "Error: Could not connect to Ollama. Please ensure Ollama is running and the endpoint in config.yaml is correct."})


    except Exception as e: # Catch any other unexpected errors
        return json.dumps({"intent": "chat", "response": f"An unexpected error occurred during LLM query: {str(e)}"})

def get_available_tools_summary(config):
    commands = config.get("commands", {})
    return "\n".join(f"- {name}: {details.get('description', '')}" for name, details in commands.items())
