import re
from pathlib import Path
from typing import List, Set, Tuple, Dict, Any
from rich.console import Console
from graphlib import TopologicalSorter, CycleError
from vdsnow.context import get_context_from_path, get_default_context

console = Console()


def _parse_dependencies(file_path: Path, content: str) -> List[str]:
    """Parses '-- vdsnow_depends_on:' comments from a SQL file."""
    dependencies = []
    # This regex finds the dependency declaration and captures the path.
    pattern = re.compile(r"^\s*--\s*vdsnow_depends_on:\s*(.+?)\s*$", re.MULTILINE)
    matches = pattern.findall(content)

    for rel_path_str in matches:
        # Resolve the dependency path relative to the file it's in.
        dep_path = (file_path.parent / rel_path_str).resolve()
        # Normalize it to be relative to the project root for consistency.
        project_relative_dep = dep_path.relative_to(Path.cwd())
        dependencies.append(str(project_relative_dep))

    return dependencies


def _recursive_parse(
    file_path: Path,
    full_new_state: List[Dict[str, Any]],
    processed_files: Set[Path],
    use_local_context: bool,
) -> None:
    """Recursively parse a file, collecting data for all leaf nodes."""
    if file_path in processed_files:
        return
    processed_files.add(file_path)

    if not file_path.exists():
        console.print(f"[yellow]Warning: Source file not found, skipping: {file_path}[/yellow]")
        return

    content = file_path.read_text()
    is_manifest = "!source" in content

    if is_manifest:
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("!source"):
                source_path_str = line.split("!source")[1].strip()
                next_file_path = Path(source_path_str)
                _recursive_parse(next_file_path, full_new_state, processed_files, use_local_context)
    else:
        # This is a leaf file (./snowflake_structure). We must generate a state object for it.
        db, schema = (None, None)
        if use_local_context:
            db, schema = get_default_context()
        else:
            db, schema = get_context_from_path(file_path)

        if db and schema:
            abs_path = file_path.resolve()
            command = f"use schema {db}.{schema}; !source {abs_path}"

            # Get dependencies
            dependencies = _parse_dependencies(file_path, content)

            # Create the structured state object for this file
            state_object = {
                "path": str(file_path),
                "command": command,
                "depends_on": dependencies,
                "sql": content,
            }
            full_new_state.append(state_object)


def _sort_graph(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sorts a list of nodes based on their dependencies using a topological sort."""
    sorter = TopologicalSorter()
    node_map = {node['path']: node for node in nodes}

    for path, node in node_map.items():
        sorter.add(path, *node['depends_on'])

    try:
        sorted_paths = list(sorter.static_order())
        console.print("   [dim]Dependency graph sorted successfully.[/dim]")
        return [node_map[path] for path in sorted_paths]
    except CycleError as e:
        console.print("\n[bold red]❌ ERROR: A circular dependency was detected in your project.[/bold red]")
        console.print(f"   Cycle: {' -> '.join(e.args[1])}")
        # Return an empty list to finish execution
        return []


def compile_plan(
    start_file: Path,
    use_local_context: bool,
    differ_mode: bool,
    old_state: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Compiles a start file into a dependency-sorted execution plan.
    """
    console.print("\n[bold cyan]🔎 Compiling execution plan...[/bold cyan]")

    # 1. Parse all files to get a flat list of nodes and their dependencies
    parsed_nodes: List[Dict[str, Any]] = []
    processed: Set[Path] = set()
    _recursive_parse(start_file, parsed_nodes, processed, use_local_context)

    # 2. Sort the nodes based on the dependency graph
    full_new_state = _sort_graph(parsed_nodes)
    if not full_new_state and parsed_nodes: # Check if sorting failed
        return [], []

    # 3. Perform the diff against the sorted list
    if not differ_mode:
        console.print("   [dim]Standard mode: all compiled files will be executed in order.[/dim]")
        return full_new_state, full_new_state

    console.print("   [dim]--differ mode enabled: checking for changes against vdstate.json...[/dim]")
    commands_to_run: List[Dict[str, Any]] = []
    for new_node in full_new_state:
        path = new_node["path"]
        old_node = old_state.get(path)

        # A node must be re-run if it's new, its SQL has changed,
        # OR if any of its dependencies have changed.
        if not old_node or old_node["sql"] != new_node["sql"]:
            commands_to_run.append(new_node)
            continue

    return commands_to_run, full_new_state
