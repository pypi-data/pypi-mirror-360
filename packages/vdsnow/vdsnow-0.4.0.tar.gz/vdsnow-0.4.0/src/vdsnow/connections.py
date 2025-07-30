from pathlib import Path
import tomli
import tomli_w
import click
from rich.console import Console
import subprocess
import os

# --- Constants ---
CONFIG_TOML_PATH = Path("config.toml")
DOTENV_PATH = Path(".env")
console = Console()

# --- Helper Functions ---

def _update_config_toml(conn_name: str) -> None:
    """Safely updates the config.toml file."""
    config = {}
    if CONFIG_TOML_PATH.exists():
        with CONFIG_TOML_PATH.open("rb") as f:
            config = tomli.load(f)

    # Set the default connection name
    config["default_connection_name"] = conn_name

    # Ensure the [connections] section exists
    if "connections" not in config:
        config["connections"] = {}

    # Update the specific connection details
    config["connections"][conn_name] = {
        "account": "",
        "user": "",
        "role": "",
        "warehouse": "",
        "database": "",
        "schema": "",
        "authenticator": "SNOWFLAKE_JWT",
        "private_key_path": "",
    }

    # Adding also headless connection table (ci/cd process)
    config["connections"]["headless"] = {
        "account": "",
        "user": "",
        "role": "",
        "warehouse": "",
        "database": "",
        "schema": "",
        "authenticator": "SNOWFLAKE_JWT",
        "private_key_raw": "",
    }

    with CONFIG_TOML_PATH.open("wb") as f:
        tomli_w.dump(config, f)
    # This is required by snowcli for security.
    try:
        os.chmod(CONFIG_TOML_PATH, 0o600)
        console.print(f"[green]✓ Set secure permissions for:[/green] {CONFIG_TOML_PATH}")
    except OSError as e:
        # This might fail on some systems (like Windows), but the error from snowcli
        # is primarily a Unix-like system concern. We'll just warn the user.
        console.print(f"[yellow]Warning: Could not set permissions for {CONFIG_TOML_PATH}. "
                        f"This might be required on your OS. Error: {e}[/yellow]")

    console.print(f"[green]✓ Updated configuration file:[/green] {CONFIG_TOML_PATH}")


def _update_dotenv(conn_name: str, values: dict) -> None:
    """Intelligently updates the .env file, preserving existing content."""
    env_prefix = f"SNOWFLAKE_CONNECTIONS_{conn_name.upper()}"

    new_vars = {
        f"{env_prefix}_ACCOUNT": values.get("account", ""),
        f"{env_prefix}_USER": values.get("user", ""),
        f"{env_prefix}_ROLE": values.get("role", ""),
        f"{env_prefix}_DATABASE": values.get("database", ""),
        f"{env_prefix}_SCHEMA": values.get("schema", ""),
        f"{env_prefix}_WAREHOUSE": values.get("warehouse", ""),
        f"{env_prefix}_AUTHENTICATOR": "SNOWFLAKE_JWT",
        f"{env_prefix}_PRIVATE_KEY_PATH": f"~/.ssh/vdsnow_{conn_name}_rsa_key.p8",
        "SNOWFLAKE_HOME": ".",
        "VDSNOW_ENV": "local"
    }

    if not DOTENV_PATH.exists():
        DOTENV_PATH.touch()

    lines = DOTENV_PATH.read_text().splitlines()
    output_lines = []
    found_vars = set()

    # Update existing variables in place
    for line in lines:
        match_found = False
        for var_name, var_value in new_vars.items():
            if line.startswith(f"export {var_name}="):
                output_lines.append(f'export {var_name}="{var_value}"')
                found_vars.add(var_name)
                match_found = True
                break
        if not match_found:
            output_lines.append(line)

    # Append any new variables that weren't found
    for var_name, var_value in new_vars.items():
        if var_name not in found_vars:
            output_lines.append(f'export {var_name}="{var_value}"')

    DOTENV_PATH.write_text("\n".join(output_lines) + "\n")
    console.print(f"[green]✓ Updated environment file:[/green] {DOTENV_PATH}")


# --- Public CLI-Facing Function ---

def init_connection() -> None:
    """Interactively creates or updates a Snowflake connection."""
    console.print("\n[bold cyan]❄️ Setting up a new Snowflake Connection ❄️[/bold cyan]")

    conn_name = click.prompt("Connection Name", default="local", type=str)

    console.print("\nPlease provide your connection details. Press Enter to leave a field blank.")

    conn_values = {
        "account": click.prompt("Account", default="", show_default=False),
        "user": click.prompt("User", default="", show_default=False),
        "role": click.prompt("Role", default="", show_default=False),
        "warehouse": click.prompt("Warehouse", default="", show_default=False),
        "database": click.prompt("Database", default="", show_default=False),
        "schema": click.prompt("Schema", default="", show_default=False),
    }

    _update_config_toml(conn_name)
    _update_dotenv(conn_name, conn_values)

    console.print("\n[bold green]✅ Connection configured![/bold green]")
    console.print("   - You must now generate a private/public key pair for JWT authentication.")
    console.print("   - Fill in the blank values and update the private key path if needed.")


def test_connection() -> None:
    """
    Runs 'snow connection test' to validate the default connection.
    This provides a wrapper around the snowcli command, showing live output.
    """
    console.print("\n[bold cyan]🧪 Running 'snow connection test'...[/bold cyan]")
    console.print("   (This uses your default connection defined in config.toml)")

    try:
        # The command is provided as a list for security and correctness.
        command = ["snow", "connection", "test"]

        # We run the command and let its output stream directly to the user's terminal.
        # `check=True` will automatically raise a CalledProcessError if the command
        # returns a non-zero exit code (i.e., it fails).
        subprocess.run(command, check=True)

        # Note: We don't need to print a success message here because a successful
        # `snow connection test` prints its own "Connection ... tested successfully."

    except FileNotFoundError:
        # This error occurs if the 'snow' executable cannot be found at all (rare).
        console.print("\n[bold red]❌ ERROR: `snow` command not found.[/bold red]")
        console.print("   Please ensure the Snowflake CLI is installed and in your system's PATH.")

    except subprocess.CalledProcessError:
        # This error is raised by `check=True` when the command fails.
        # snowcli will have already printed a detailed error message (e.g., bad credentials).
        # We just add a concluding message to make it clear that our tool caught the failure.
        console.print("\n[bold red]❌ Connection test failed. See the output above from snowcli for details.[/bold red]")
