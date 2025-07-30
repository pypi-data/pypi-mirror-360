# ❄️ vdsnow: A Modern CLI for Snowflake Development

**vdsnow** is a powerful command-line interface designed to streamline and professionalize the entire lifecycle of your Snowflake projects. It provides tools for project scaffolding, intelligent SQL execution, state management, and dependency resolution, turning complex deployments into simple, repeatable commands. vdsnow is designed by leveraging the snowflake cli (snowcli), working not only as a wrapper of it but also as a helper tool to improve your CI/CD workflows.

Think of it as a lightweight, state-aware orchestrator for your Snowflake SQL code, inspired by best practices from tools like dbt and Terraform.


---

## Core Features

-   **Project Scaffolding**: Initialize a clean, standardized folder structure for your databases and schemas in seconds.
-   **Intelligent Execution**: Run SQL files with automatic context detection based on folder structure.
-   **Folder Validates**: Ensure that your folder structure is valid ie there are no files listed to be deployed that they don't exist in your snowflake_structure folder.
-   **State-Aware Deployments**: Only deploy what's changed. `vdsnow` tracks the state of your project and can run differential deployments, saving time and reducing risk.
-   **Dependency Management (DAG)**: Explicitly define dependencies between your SQL files. `vdsnow` builds a Directed Acyclic Graph (DAG) to ensure objects are deployed in the correct order, every time.
-   **CI/CD Ready**: Designed for automation with headless connection support via environment variables.
-   **Safe Planning**: Use the `plan` command to see what changes will be made before you apply them.

---

## Installation

`vdsnow` is managed as a Python project. In this README installation is handled via `uv`.

```bash
uv add vdsnow
```

---

## Configuration / Connections

Configuration is handled through two primary files at the root of your project. To init your connection settings, run:

```bash
uv run vdsnow connection  init
```

Then, you will be prompted to enter your Snowflake informations. After that, you can edit either the `config.toml` file or the `.env` file if needed.

### 1. `config.toml`

This file defines your connection configurations. You can define multiple connections (e.g., `local`, `headless`).

*Example `config.toml`:*
```toml
default_connection_name = "local"

[connections.local]
account = ""
user = ""
role = ""
warehouse = ""
database = ""
schema = ""
authenticator = "SNOWFLAKE_JWT"
private_key_path = ""

```

### 2. `.env` File

This file stores secrets and environment-specific variables. **It should be added to your `.gitignore` file.** `vdsnow` automatically loads this file at runtime.

*Example `.env`:*
```bash
export SNOWFLAKE_CONNECTIONS_LOCAL_ACCOUNT="my_snowflake_account_identified"
...
```

---

## Project Structure

`vdsnow` creates and manages two key directories:

-   `snowflake_structure/`: This is where your raw SQL files live. The folder hierarchy (`<database>/<schema>/...`) is where you organize your DDL scripts (tables, views, procedures, etc.).
-   `setup/`: This directory contains auto-generated "manifest" files (`setup.sql`). These files orchestrate the execution of the raw SQL in `snowflake_structure/` by using `!source` commands. You should generally not edit these files by hand; use `vdsnow setup refresh-scripts` to update them.

---

## Command Reference

### `uv run vdsnow setup`

Commands for managing the project's folder and script structure.

-   `init`: Interactively creates the initial `snowflake_structure/` and `setup/` directories (should be your first command).
-   `add-database`: Adds a new database folder to the structure.
-   `add-schema`: Adds a new schema folder to a specified database.
-   `refresh-scripts`: **Important!** Scans your `snowflake_structure/` and regenerates all `setup.sql` manifest files to reflect the current state of your project.
-   `create-ci`: Creates the necessary SQL scripts in `setup/ci/` for CI/CD workflows.

### `vdsnow sql`

Commands for planning, executing, and managing the state of your SQL deployments.

-   `plan`: Compiles and displays the execution plan without running it.
    -   `-f, --file`: The root `.sql` file to plan (defaults to `setup/setup.sql`).
    -   `--local`: Shows the plan for the default sandbox context.
    -   `--differ`: Shows a plan containing only files that have changed since the last run.

-   `execute`: Executes the SQL deployment plan - `./compiled` folder is created and aloows you to see what is running.
    -   `-f, --file`: The root `.sql` file to execute.
    -   `--local`: Runs the deployment in the default sandbox context.
    -   `--differ`: Executes only the files that have changed since the last run. Updates `vdstate.json` on success.
    -   `-q, --query`: Executes only the specified query.

-   `refresh-state`: Re-scans the project and updates `vdstate.json` without executing any SQL.
    -   `-f, --file`: The root `.sql` file to build the state from (defaults to `setup/setup.sql`).
    -   `--local`: Builds the state based on the local context.

-   `get-state-from-remote`: Retrieves the state from a remote Snowflake account. This command will pull the state from the remote account and overwrite `vdstate.json` in case it exists.
    -    `--db`: The name of the database to retrieve the state from.
    -    `--schema`: The name of the schema to retrieve the state from.

### `vdsnow check`

Commands for validating your project and environment.

-   `version`: Checks the installed `snowcli` version.
-   `folder-structure`: Validates the project structure for discrepancies. It raises an error if a file is listed to be deployed (inside `./setup`) but it's not found in `./snowflake_structure`. It raises a warning if a file is defined in `./snowflake_structure` but it's not found in `./setup`.

### `vdsnow connection`

Commands for managing Snowflake connections.

-   `init`: Interactively creates or updates a connection configuration in `config.toml`.
-   `test`: Tests the configured Snowflake connection.

---

## Advanced Features

### State Management (`vdstate.json`)

`vdsnow` creates a `vdstate.json` file after the first successful `execute` run. This file is a snapshot of your project, containing the path, command, dependencies, and SQL content of every file.

The `--differ` flag uses this file to determine what has changed, enabling intelligent, partial deployments.

Using `--no-local` or `--local` helps you to compile the plan and see how it's deployed locally or remotely. You can even execute commands in the destination environment (remote), but ideally you should not have create access to the destination environment.

### Dependency Management (DAG)

You can define dependencies between your SQL files to ensure they are created in the correct order. `vdsnow` uses this information to build a Directed Acyclic Graph (DAG) and generate a valid execution plan.

To declare a dependency, add a specially formatted comment to your SQL file. The path is **relative to the file you are in**.

*Example: `snowflake_structure/analytics/views/my_view.sql`*
```sql
-- This view depends on a table in the 'base' schema.
-- The path is relative to this file's location.
-- vdsnow_depends_on: ../base/tables/my_table.sql

CREATE OR REPLACE VIEW analytics.my_view AS
SELECT * FROM base.my_table;
```

---

## Example Workflow

1.  **Initialize your project:**
    ```bash
    uv run vdsnow setup init
    ```

2.  **Initialize your connection:**
    ```bash
    uv run vdsnow connection setup
    ```

3.  **Add your SQL files** to the `snowflake_structure/` directory.

4.  **Declare dependencies** in your SQL files using `-- vdsnow_depends_on: ...`.

5.  **Refresh the setup scripts** to wire everything together:
    ```bash
    uv run vdsnow setup refresh-scripts
    ```

6.  **Plan your deployment** to see what will happen:
    ```bash
    uv run vdsnow sql plan
    ```

7.  **Execute the local deployment:**
    ```bash
    uv run vdsnow sql execute -f ./setup/setup.sql
    ```

8.  **Make a change** to one of your SQL files.

9.  **Plan and execute the change** using `--differ`:
    ```bash
    uv run vdsnow sql plan --differ
    uv run vdsnow sql execute -f ./setup/setup.sql --differ
    ```

10. **Add a new schema**
    ```bash
    uv run vdsnow setup add-schema db_raw_new --schema schema_new
    ```

11. **Define new objects in the new schema**

12. **Validate your folder structure**
    ```bash
    uv run vdsnow check folder-structure
    ```

13. **Create CI folder once ready**
    ```bash
    uv run vdsnow setup create-ci
    ```
