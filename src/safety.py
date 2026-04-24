"""
Safety module for AI computer controller.
Defines dangerous operations and provides confirmation mechanisms.
"""

from rich.console import Console
from rich.panel import Panel

console = Console()

# List of dangerous action types that require user confirmation
DANGEROUS_ACTION_TYPES = {
    "delete_file",
    "delete_directory", 
    "format_drive",
    "system_command",
    "registry_edit",
    "shutdown",
    "restart",
}

# Dangerous file extensions
DANGEROUS_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".ps1", ".scr", ".com",
    ".msi", ".vbs", ".js", ".reg",
}

# Dangerous content patterns
DANGEROUS_CONTENT_PATTERNS = [
    "rm -rf",
    "del /s",
    "del /q",
    "format",
    "mkfs",
    "shutdown -r",
    "shutdown -s",
    "reg delete",
    "reg add",
]

def is_dangerous_action(action_type, params=None):
    """Check if an action type is considered dangerous."""
    if action_type in DANGEROUS_ACTION_TYPES:
        return True
    
    # Check file operations
    if action_type in ("write_file", "delete_file"):
        path = params.get("path", "") if params else ""
        # Check extension
        for ext in DANGEROUS_EXTENSIONS:
            if path.lower().endswith(ext):
                return True
        # Check content
        content = params.get("content", "") if params else ""
        for pattern in DANGEROUS_CONTENT_PATTERNS:
            if pattern.lower() in content.lower():
                return True
    
    return False

def confirm_dangerous_action(action_type, params=None, cli=None):
    """
    Ask user to confirm a dangerous action.
    
    Returns True if user confirms, False otherwise.
    """
    description = _get_action_description(action_type, params)
    
    console.print(Panel(
        f"[red]DANGEROUS OPERATION DETECTED[/red]\n\n"
        f"Action: {description}\n\n"
        "This action could potentially harm your system.\n"
        "Do you want to allow it?",
        title="Safety Warning",
        border_style="red"
    ))
    
    if cli:
        return cli.confirm("Allow this action?")
    else:
        response = input("Allow this action? (y/N): ")
        return response.lower() in ("y", "yes")

def _get_action_description(action_type, params):
    """Get human-readable description of the action."""
    if not params:
        return action_type
    
    if action_type in ("write_file", "delete_file", "read_file"):
        return f"{action_type}: {params.get('path', 'unknown')}"
    elif action_type == "system_command":
        return f"Execute command: {params.get('command', 'unknown')}"
    elif action_type in ("shutdown", "restart"):
        return f"System {action_type}"
    else:
        return f"{action_type}: {params}"
