import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

from rich.console import Console

console = Console()
STATE_FILE = Path("vdstate.json")

def load_state() -> Dict[str, Any]:
    """
    Loads the vdstate.json file.
    Returns a dictionary keyed by file path for efficient lookups.
    """
    if not STATE_FILE.exists():
        return {}

    try:
        with open(STATE_FILE, "r") as f:
            state_data = json.load(f)

        # Convert the list of objects into a path-keyed dictionary
        return {item['path']: item for item in state_data.get('files', [])}
    except (json.JSONDecodeError, KeyError):
        console.print(f"[bold yellow]Warning: Could not parse '{STATE_FILE}'. Treating as empty state.[/bold yellow]")
        return {}


def save_state(new_state_files: list) -> None:
    """
    Saves the new state to vdstate.json, overwriting the old file.
    """
    now_utc = datetime.now(timezone.utc).isoformat()

    full_state = {
        "vdsnow_version": "1.0", # can get this from __version__ later
        "generated_at": now_utc,
        "files": new_state_files
    }

    with open(STATE_FILE, "w") as f:
        json.dump(full_state, f, indent=2)

    console.print(f"   [dim]State updated successfully in '{STATE_FILE}'[/dim]")


def get_state_from_remote(database: str, schema: str, path: str) -> None:
    """
    Runs 'snow sql -q "GET @RAW.VD.VDSNOW file:///<path>/to/project/"
    This provides a wrapper around the snowcli command, showing live output.
    """
    console.print("\n[bold cyan]🧪 Running 'snow get vdstate.json'...[/bold cyan]")

    LOCAL_PATH: Path = Path(path).resolve()
    COMMAND: str = fr"GET @{database}.{schema}.VDSNOW file:///{LOCAL_PATH}/"

    try:
        # The command is provided as a list for security and correctness.
        command = ["snow", "sql", "-q", COMMAND]

        # We run the command and let its output stream directly to the user's terminal.
        # `check=True` will automatically raise a CalledProcessError if the command
        # returns a non-zero exit code (i.e., it fails).
        subprocess.run(command, check=True)

        # Note: We don't need to print a success message here because a successful

    except FileNotFoundError:
        # This error occurs if the 'snow' executable cannot be found at all (rare).
        console.print("\n[bold red]❌ ERROR: `snow` command not found.[/bold red]")
        console.print("   Please ensure the Snowflake CLI is installed and in your system's PATH.")

    except subprocess.CalledProcessError:
        # This error is raised by `check=True` when the command fails.
        # snowcli will have already printed a detailed error message (e.g., bad credentials).
        # We just add a concluding message to make it clear that our tool caught the failure.
        console.print("\n[bold red]❌ Connection test failed. See the output above from snowcli for details.[/bold red]")
