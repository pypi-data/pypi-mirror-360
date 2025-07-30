import shutil
from pathlib import Path
from typing import Optional, List

import click
from rich.console import Console

# --- Constants ---
FOLDERS: List[str] = ["tables", "views", "functions", "file_formats"]
BASE_DIR_NAME: str = "snowflake_structure"
SETUP_BASE_DIR_NAME: str = "setup"

console = Console()


# --- Reusable Helper Functions ---

def _find_existing_databases() -> List[str]:
    root_dir = Path(BASE_DIR_NAME)
    if not root_dir.is_dir():
        return []
    return [d.name for d in root_dir.iterdir() if d.is_dir()]


def _prompt_for_schemas() -> List[str]:
    schemas: List[str] = []
    while True:
        schema_name: str = click.prompt("Enter a schema name", type=str)
        schemas.append(schema_name)
        if not click.confirm("\nDo you want to add another schema?", default=False):
            break
    return schemas



# --- Core Worker Functions ---

def create_schema_folders(db_name: str, schemas: List[str]) -> None:
    db_dir = Path(BASE_DIR_NAME) / db_name
    for schema in schemas:
        schema_dir = db_dir / schema
        if not schema_dir.exists():
            console.print(f"  [cyan]Creating structure for schema:[/cyan] {schema}")
            for folder in FOLDERS:
                target_path = schema_dir / folder
                example_target_file = target_path / f"example__{folder}.sql"

                # create folder
                target_path.mkdir(parents=True, exist_ok=True)
                console.print(f"    [green]✓ Created:[/green] {str(target_path)}")

                # add example__file
                example_target_file.write_text("SELECT CURRENT_DATE() AS DATE;")

        else:
            console.print(
                f"[bold yellow]Warning:[/bold yellow] Schema directory './{schema_dir}' already exists. Skipping."
            )


def _update_source_manifest(manifest_file: Path, source_paths: List[Path], comment_prefix: str) -> None:
    """
    THE NEW GENERIC HELPER: Intelligently updates a manifest file.
    It reads the file, compares it to the desired source paths, and appends
    only the new source commands, preserving existing content and order.
    """
    existing_commands = set()
    if manifest_file.exists():
        lines = manifest_file.read_text().splitlines()
        existing_commands = {line.strip() for line in lines if line.strip()}

    # Generate the desired commands from the source paths
    desired_commands = []
    for path in source_paths:
        # Create a block with a comment and the source command
        block = [f"-- {comment_prefix}: {path.name}", f"!source ./{path}"]
        desired_commands.extend(block)

    # Find commands that are not already in the file
    new_commands = [cmd for cmd in desired_commands if cmd not in existing_commands]

    if new_commands:
        console.print(f"    [yellow]Updating:[/yellow] {str(manifest_file)}")
        with manifest_file.open("a") as f:
            if existing_commands:
                f.write("\n\n") # Use two newlines to separate blocks
            # We must write the new commands in pairs (comment + source)
            # This logic handles adding the full new blocks correctly.
            new_content = []
            for i in range(0, len(new_commands), 2):
                 new_content.append("\n".join(new_commands[i:i+2]))
            f.write("\n\n".join(new_content))
            console.print(f"      [green]✓ Appended {len(new_content)} new block(s).[/green]")
    else:
        console.print(f"    [green]✓ Up-to-date:[/green] {str(manifest_file)}")


def _update_object_type_sql_manifests(setup_schema_dir: Path) -> None:
    """
    Uses the generic helper to update object-type manifests
    (e.g., tables.sql, views.sql) by dynamically discovering folders.
    """
    db_name = setup_schema_dir.parent.name
    schema_name = setup_schema_dir.name
    snowflake_schema_dir = Path(BASE_DIR_NAME) / db_name / schema_name

    if not snowflake_schema_dir.is_dir():
        return # Nothing to do if the source schema folder doesn't exist

    # Discover all subdirectories (tables, views, procedures, etc.)
    discovered_folders = sorted([d for d in snowflake_schema_dir.iterdir() if d.is_dir()])

    for source_dir in discovered_folders:
        folder_name = source_dir.name
        manifest_file = setup_schema_dir / f"{folder_name}.sql"

        # Find all .sql files in the source directory to be included
        sql_files = sorted(source_dir.glob("*.sql"))

        # If a manifest file doesn't exist yet and there are no sql files,
        # create an empty manifest. This handles newly created empty folders.
        if not sql_files and not manifest_file.exists():
            manifest_file.touch()

        _update_source_manifest(manifest_file, sql_files, "FILE")


def _update_schema_setup_sql(schema_dir: Path) -> None:
    """
    Uses the generic helper to update the main schema setup.sql file.
    """
    manifest_file = schema_dir / "setup.sql"

    # Find all object-type manifests (.sql files except setup.sql)
    source_files = sorted([f for f in schema_dir.glob("*.sql") if f.name != "setup.sql"])

    _update_source_manifest(manifest_file, source_files, "OBJECT TYPE")


def _generate_database_setup_sql(db_dir: Path) -> None:
    # by folder names, not manual editing.
    setup_file = db_dir / "setup.sql"
    schema_dirs = sorted([d for d in db_dir.iterdir() if d.is_dir()])
    content_blocks = []
    for schema_dir in schema_dirs:
        schema_setup_path = schema_dir / "setup.sql"
        if schema_setup_path.exists(): # Only add if it exists
            block = [f"-- SCHEMA: {schema_dir.name}", f"!source ./{schema_setup_path}"]
            content_blocks.append("\n".join(block))
    setup_file.write_text("\n\n".join(content_blocks))
    console.print(f"  [green]✓ Generated:[/green] {str(setup_file)}")


def _generate_project_setup_sql(setup_root: Path) -> None:
    """Generates the final, top-level setup script for the entire project."""
    project_setup_file = setup_root / "setup.sql"

    # Discover all database directories within the setup folder
    all_dirs = sorted([d for d in setup_root.iterdir() if d.is_dir()])
    db_setup_dirs = [d for d in all_dirs if d.name != "ci"]

    content_blocks = []
    for db_dir in db_setup_dirs:

        db_setup_path = db_dir / "setup.sql"
        if db_setup_path.exists():
            block = [f"-- DATABASE: {db_dir.name}", f"!source ./{db_setup_path}"]
            content_blocks.append("\n".join(block))

    project_setup_file.write_text("\n\n".join(content_blocks))
    console.print(f"\n[bold green]✓ Generated Project Setup Script:[/bold green] {str(project_setup_file)}")


# --- Public CLI-Facing Functions ---

def refresh_setup_scripts() -> None:
    """
    Scans the entire project and regenerates ALL generated scripts intelligently.
    """
    console.print(f"\n[bold cyan]🔄 Refreshing all setup scripts...[/bold cyan]")
    structure_root = Path(BASE_DIR_NAME)
    if not structure_root.is_dir():
        console.print(f"[bold red]Error:[/bold red] Project structure './{structure_root}' not found.")
        return

    db_dirs = [d for d in structure_root.iterdir() if d.is_dir()]

    for db_dir in db_dirs:
        console.print(f"  [cyan]Processing Database:[/cyan] {db_dir.name}")
        schema_dirs = [d for d in db_dir.iterdir() if d.is_dir()]
        for schema_dir in schema_dirs:
            setup_schema_dir = Path(SETUP_BASE_DIR_NAME) / db_dir.name / schema_dir.name
            setup_schema_dir.mkdir(parents=True, exist_ok=True)

            _update_object_type_sql_manifests(setup_schema_dir)
            _update_schema_setup_sql(setup_schema_dir)

        setup_db_dir = Path(SETUP_BASE_DIR_NAME) / db_dir.name
        _generate_database_setup_sql(setup_db_dir)


    setup_root = Path(SETUP_BASE_DIR_NAME)
    _generate_project_setup_sql(setup_root)

    console.print("\n[bold green]✅ All setup scripts are now up-to-date![/bold green]")


def init_snowflake_structure() -> None:
    """Initializes the entire project structure from scratch."""
    if Path(BASE_DIR_NAME).exists():
        console.print(f"[bold yellow]Warning:[/bold yellow] Project already initialized.")
        return

    console.print(f"\n[bold cyan]❄️ Initializing New Snowflake Project ❄️[/bold cyan]")
    db_name: str = click.prompt("Enter the database name", type=str)
    schemas = _prompt_for_schemas()

    if not schemas:
        console.print("[bold yellow]No schemas provided. Aborting.[/bold yellow]")
        return

    # Just create the folders. Refresh will handle the rest.
    create_schema_folders(db_name, schemas)
    # Create the empty setup directories needed for refresh to find them
    for schema in schemas:
        (Path(SETUP_BASE_DIR_NAME) / db_name / schema).mkdir(parents=True, exist_ok=True)

    refresh_setup_scripts()


def add_schema_to_database(db_name: Optional[str], schema_names: List[str]) -> None:
    """Adds one or more schemas to a specified database."""
    existing_databases = _find_existing_databases()
    if not existing_databases:
        console.print(f"[bold red]Error:[/bold red] No databases found.")
        return

    if not db_name:
        db_name = click.prompt("Database to add schemas to?", type=click.Choice(existing_databases))

    if db_name not in existing_databases:
        console.print(f"[bold red]Error:[/bold red] Database '{db_name}' not found.")
        return

    if not schema_names:
        schema_names = _prompt_for_schemas()

    if not schema_names:
        console.print("[bold yellow]No schemas provided. Aborting.[/bold yellow]")
        return

    create_schema_folders(db_name, schema_names)
    # Create the empty setup directories
    for schema in schema_names:
        (Path(SETUP_BASE_DIR_NAME) / db_name / schema).mkdir(parents=True, exist_ok=True)

    refresh_setup_scripts()


def add_database() -> None:
    """Interactively adds a new database and its schemas to the project."""
    if not Path(BASE_DIR_NAME).is_dir():
        console.print(f"[bold red]Error:[/bold red] Project not initialized. Run 'setup init' first.")
        return

    console.print(f"\n[bold cyan]❄️ Adding a New Database ❄️[/bold cyan]")
    db_name: str = click.prompt("Enter the new database name", type=str)
    schemas: List[str] = _prompt_for_schemas()

    if not schemas:
        console.print("[bold yellow]No schemas provided. Aborting.[/bold yellow]")
        return

    create_schema_folders(db_name, schemas)
    # Create the empty setup directories
    for schema in schemas:
        (Path(SETUP_BASE_DIR_NAME) / db_name / schema).mkdir(parents=True, exist_ok=True)

    refresh_setup_scripts()


def recreate_snowflake_structure() -> None:
    """Deletes and re-initializes the entire project structure."""
    for dir_name in [BASE_DIR_NAME, SETUP_BASE_DIR_NAME]:
        if Path(dir_name).exists():
            click.confirm(
                f"This will permanently delete './{dir_name}'. Are you sure?",
                abort=True,
            )
            console.print(f"[bold red]Deleting existing structure: ./{dir_name}[/bold red]")
            shutil.rmtree(dir_name)
            console.print("[green]✓ Deletion complete.[/green]")

    init_snowflake_structure()


def create_ci_files() -> None:
    """
    Creates the 'setup/ci' directory and the necessary SQL scripts for CI/CD workflows.
    """
    console.print("\n[bold cyan]🚀 Scaffolding CI/CD workflow files...[/bold cyan]")

    setup_dir = Path(SETUP_BASE_DIR_NAME)
    if not setup_dir.is_dir():
        console.print(f"[bold red]❌ ERROR: The '{setup_dir}' directory does not exist.[/bold red]")
        console.print("   Please run 'vdsnow setup init' first to create the project structure.")
        return

    ci_dir = setup_dir / "ci"
    ci_dir.mkdir(exist_ok=True)

    # Define the content for each file
    files_to_create = {
        "create_schema.sql": (
            "CREATE OR REPLACE SCHEMA <% ctx.env.SNOWFLAKE_CONNECTIONS_HEADLESS_DATABASE %>."
            "<% ctx.env.SNOWFLAKE_CONNECTIONS_HEADLESS_SCHEMA %> WITH MANAGED ACCESS;"
        ),
        "setup.sql": (
            "-- CREATE CI SCHEMA + DEPLOY PROJECT\n"
            "!source ./setup/ci/create_schema.sql\n"
            "!source ./setup/setup.sql"
        ),
        "drop_schema.sql": (
            "DROP SCHEMA IF EXISTS <% ctx.env.SNOWFLAKE_CONNECTIONS_HEADLESS_DATABASE %>."
            "<% ctx.env.SNOWFLAKE_CONNECTIONS_HEADLESS_SCHEMA %>;"
        ),
    }

    created_files = []
    for filename, content in files_to_create.items():
        file_path = ci_dir / filename
        file_path.write_text(content)
        created_files.append(f"[green]'{file_path}'[/green]")

    console.print(f"   ✅ Successfully created CI files: {', '.join(created_files)}")
    console.print("\n[bold yellow]Next Steps:[/bold yellow] You can now use these files in your CI pipeline.")
