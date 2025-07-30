import os
from pathlib import Path

import typer
import yaml

from datatrack import diff as diff_module
from datatrack import exporter, history, linter, pipeline, tracker, verifier

app = typer.Typer(help="Datatrack: Schema tracking CLI")

CONFIG_DIR = ".datatrack"
CONFIG_FILE = "config.yaml"


@app.command()
def init():
    """
    Initialize Datatrack in the current directory.
    """
    config_path = Path(CONFIG_DIR)
    if config_path.exists():
        typer.echo("Datatrack is already initialized.")
        raise typer.Exit()

    # Create .datatrack directory
    config_path.mkdir(parents=True, exist_ok=True)

    # Default config contents
    default_config = {
        "project_name": "my-datatrack-project",
        "created_by": os.getenv("USER") or "unknown",
        "version": "0.1",
        "sources": [],
    }

    with open(config_path / CONFIG_FILE, "w") as f:
        yaml.dump(default_config, f)

    typer.echo("Datatrack initialized in .datatrack/")


@app.command()
def snapshot(source: str = typer.Option(..., help="Database source URI")):
    """
    Capture the current schema state from a real database and save a snapshot.
    """
    typer.echo("\nCapturing schema snapshot from source...")

    try:
        tracker.snapshot(source)
        typer.echo("Snapshot successfully captured and saved.\n")
    except Exception as e:
        typer.echo(f"Error capturing snapshot: {e}")


@app.command()
def diff():
    """
    Compare latest two snapshots and show schema differences.
    """
    try:
        old, new = diff_module.load_snapshots()
        diff_module.diff_schemas(old, new)
    except Exception as e:
        typer.secho(f"{str(e)}", fg=typer.colors.RED)


@app.command()
def verify():
    """
    Check schema against configured rules (e.g. snake_case, reserved words).
    """
    typer.echo("\nVerifying schema...\n")

    try:
        schema = verifier.load_latest_snapshot()
        rules = verifier.load_rules()
        violations = verifier.verify_schema(schema, rules)

        if not violations:
            typer.secho("All schema rules passed!\n", fg=typer.colors.GREEN)
        else:
            for v in violations:
                typer.secho(v, fg=typer.colors.RED)
            raise typer.Exit(code=1)

    except Exception as e:
        typer.secho(f"Error during verification: {str(e)}\n", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("history")
def history_command():
    """View schema snapshot history timeline"""
    history.print_history()
    print()


@app.command()
def export(
    type: str = typer.Option(..., help="snapshot or diff"),
    format: str = typer.Option("json", help="Output format: json or yaml"),
    output: str = typer.Option(..., help="Output file path"),
):
    """
    Export latest snapshot or diff as JSON/YAML.
    """
    typer.echo(f"\nExporting {type} as {format}...\n")

    try:
        if type == "snapshot":
            exporter.export_snapshot(output, format)
        elif type == "diff":
            exporter.export_diff(output, format)
        else:
            typer.echo("Invalid export type. Use 'snapshot' or 'diff'.")
            raise typer.Exit(code=1)

        typer.secho(f"Exported to {output}", fg=typer.colors.GREEN)

    except Exception as e:
        typer.secho(f"Export failed: {str(e)}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    print()


@app.command()
def lint():
    """
    Run non-blocking schema quality checks (naming,types, etc).
    """
    typer.echo("\n Running schema linter...\n")

    try:
        schema = linter.load_latest_snapshot()
        warnings = linter.lint_schema(schema)

        if not warnings:
            typer.secho("No linting issues found!\n", fg=typer.colors.GREEN)
        else:
            for w in warnings:
                typer.secho(w, fg=typer.colors.YELLOW)
            raise typer.Exit(code=1)

    except Exception as e:
        typer.secho(f"Error during linting: {str(e)}\n", fg=typer.colors.RED)
        raise typer.Exit(code=1)


app.add_typer(pipeline.app, name="pipeline")

if __name__ == "__main__":
    app()
