import re
from pathlib import Path
from typing import List, Tuple, Set

from rich.console import Console

# --- Constants ---
BASE_DIR_NAME: str = "snowflake_structure"
SETUP_BASE_DIR_NAME: str = "setup"

console = Console()

# --- Core Logic Function (for reuse in tests) ---


def _get_structure_discrepancies() -> Tuple[List[str], List[str]]:
    """
    Scans setup and snowflake_structure directories to find discrepancies.

    Returns:
        A tuple containing two lists:
        - broken_links: Paths in setup files that point to non-existent files in snowflake_structure.
        - unreferenced_paths: Files in snowflake_structure not mentioned in any setup file.
    """
    setup_root = Path(SETUP_BASE_DIR_NAME)
    structure_root = Path(BASE_DIR_NAME)

    if not setup_root.is_dir() or not structure_root.is_dir():
        return [], []

    # 1. Find all TERMINAL paths referenced in setup files.
    # A terminal path is one that points into the snowflake_structure directory.
    terminal_source_pointers: Set[Path] = set()
    source_pattern = re.compile(r"!source\s+\./(.*)")

    for setup_file in setup_root.glob("**/*.sql"):
        content = setup_file.read_text()
        for line in content.splitlines():
            match = source_pattern.search(line)
            if match:
                path_str = match.group(1).strip()

                # We only care about validating paths that are supposed to be in snowflake_structure.
                # This ignores intermediate manifest files (e.g., setup.sql sourcing tables.sql).
                if path_str.startswith(BASE_DIR_NAME):
                    terminal_source_pointers.add(Path(path_str))

    # 2. Find all existing .sql files in the snowflake_structure directory.
    existing_in_structure: Set[Path] = {
        p for p in structure_root.glob("**/*.sql")
    }

    # 3. Compare the sets to find discrepancies.
    broken_links = [str(p) for p in terminal_source_pointers if p not in existing_in_structure]
    unreferenced_paths = [str(p) for p in existing_in_structure if p not in terminal_source_pointers]

    return sorted(broken_links), sorted(unreferenced_paths)


# --- Public CLI-Facing Function ---

def check_folder_structure() -> None:
    """
    Validates the project structure, checking for broken links and unreferenced files.
    """
    console.print("\n[bold cyan]🔎 Validating project structure...[/bold cyan]")

    broken_links, unreferenced_paths = _get_structure_discrepancies()

    has_errors = bool(broken_links)
    has_warnings = bool(unreferenced_paths)

    if not has_errors and not has_warnings:
        console.print("[bold green]✅ Structure is valid. All files are linked correctly.[/bold green]")
        return

    if has_errors:
        console.print("\n[bold red]❌ FAILED: Found broken links in setup files![/bold red]")
        console.print("   These files are sourced in your `./setup` directory but do not exist.")
        for link in broken_links:
            console.print(f"   - [red]{link}[/red]")

    if has_warnings:
        console.print("\n[bold yellow]⚠️ WARNING: Found unreferenced files in structure.[/bold yellow]")
        console.print("   These files exist in `./snowflake_structure` but are not sourced in any setup script.")
        for path in unreferenced_paths:
            console.print(f"   - [yellow]{path}[/yellow]")

    if has_errors:
        console.print("\n[bold red]--> Please fix the broken links before deploying.[/bold red]")
