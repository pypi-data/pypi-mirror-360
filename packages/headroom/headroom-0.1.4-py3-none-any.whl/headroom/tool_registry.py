from . import system_tools

TOOL_REGISTRY = {
    # System Information Tools
    "create_and_run_python_script": {
        "function": system_tools.create_and_run_python_script,
        "args": ["filename", "code"],
        "confirmation_prompt": "I am proposing to create and run a script named '{filename}'."
    },
    # File/Directory Reading/Writing Tools
    "read_json_file": {
        "function": system_tools.read_json_file,
        "args": ["file_path"],
    },
    "write_json_file": {
        "function": system_tools.write_json_file,
        "args": ["file_path", "content"],
        "confirmation_prompt": "Are you sure you want to write to '{file_path}'? This will overwrite existing content."
    },
    "update_json_file": {
        "function": system_tools.update_json_file,
        "args": ["file_path", "key_path", "value"],
        "confirmation_prompt": "Are you sure you want to update '{key_path}' in '{file_path}' with '{value}'?"
    },
    "read_yaml_file": {
        "function": system_tools.read_yaml_file,
        "args": ["file_path"],
    },
    "write_yaml_file": {
        "function": system_tools.write_yaml_file,
        "args": ["file_path", "content"],
        "confirmation_prompt": "Are you sure you want to write to '{file_path}'? This will overwrite existing content."
    },
    "update_yaml_file": {
        "function": system_tools.update_yaml_file,
        "args": ["file_path", "key_path", "value"],
        "confirmation_prompt": "Are you sure you want to update '{key_path}' in '{file_path}' with '{value}'?"
    },
    "read_env_file": {
        "function": system_tools.read_env_file,
        "args": ["file_path"],
    },
    "update_env_file": {
        "function": system_tools.update_env_file,
        "args": ["file_path", "key", "value"],
        "confirmation_prompt": "Are you sure you want to update '{key}' in '{file_path}' with '{value}'?"
    },
    "delete_file": {
        "function": system_tools.delete_file,
        "args": ["path"],
        "confirmation_prompt": "Are you sure you want to delete the file '{path}'?"
    },
    "copy_file": {
        "function": system_tools.copy_file,
        "args": ["src", "dst"],
        "optional_args": ["recursive"],
        "confirmation_prompt": "Copy '{src}' to '{dst}'? (recursive: {recursive})"
    },
    "move_file": {
        "function": system_tools.move_file,
        "args": ["src", "dst"],
        "confirmation_prompt": "Move '{src}' to '{dst}'?"
    },
    "make_directory": {
        "function": system_tools.make_directory,
        "args": ["path"],
        "optional_args": ["exist_ok"],
        "confirmation_prompt": "Create directory '{path}'? (exist_ok: {exist_ok})"
    },
    "remove_directory": {
        "function": system_tools.remove_directory,
        "args": ["path"],
        "optional_args": ["recursive"],
        "confirmation_prompt": "Remove directory '{path}'? (recursive: {recursive})"
    },
    "change_permissions": {
        "function": system_tools.change_permissions,
        "args": ["path", "mode"],
        "confirmation_prompt": "Change permissions for '{path}' to '{mode}'?"
    },
    "change_owner": {
        "function": system_tools.change_owner,
        "args": ["path", "owner"],
        "confirmation_prompt": "Change owner for '{path}' to '{owner}'?"
    },
    # Package Management Tools
    "install_package": {
        "function": system_tools.install_package,
        "args": ["package_name"],
        "optional_args": ["package_manager"],
        "confirmation_prompt": "Install package '{package_name}'?"
    },
    "list_packages": {
        "function": system_tools.list_packages,
        "args": [],
        "optional_args": ["package_manager"],
        "confirmation_prompt": "List installed packages?"
    },
    "remove_package": {
        "function": system_tools.remove_package,
        "args": ["package_name"],
        "optional_args": ["package_manager"],
        "confirmation_prompt": "Remove package '{package_name}'?"
    },
    "search_package": {
        "function": system_tools.search_package,
        "args": ["package_name"],
        "optional_args": ["package_manager"],
        "confirmation_prompt": "Search for package '{package_name}'?"
    },
    # Service Management Tools
    "check_service_status": {
        "function": system_tools.check_service_status,
        "args": ["service_name"],
    },
    "manage_service": {
        "function": system_tools.manage_service,
        "args": ["service_name", "action"],
        "confirmation_prompt": "Are you sure you want to {action} service '{service_name}'?"
    },
    # File/Directory Operations Tools (excluding read/write)
    "list_directory": {
        "function": system_tools.list_directory,
        "args": ["path"],
    },
    "search_file_content": {
        "function": system_tools.search_file_content,
        "args": ["pattern"],
        "optional_args": ["path", "include"],
    },
    "glob_files": {
        "function": system_tools.glob_files,
        "args": ["pattern"],
        "optional_args": ["path"],
    },
    "replace_in_file": {
        "function": system_tools.replace_in_file,
        "args": ["file_path", "old_string", "new_string"],
        "confirmation_prompt": "Are you sure you want to replace content in '{file_path}'?"
    },
    # Web Tools
    "web_search": {
        "function": system_tools.web_search,
        "args": ["query"],
        "confirmation_prompt": "I am proposing to perform a web search for '{query}'."
    },
    "web_fetch": {
        "function": system_tools.web_fetch,
        "args": ["url"],
        "confirmation_prompt": "I am proposing to fetch content from '{url}'."
    },
    # Command & Version Tools
    "check_command_exists": {
        "function": system_tools.check_command_exists,
        "args": ["command_name"],
    },
}