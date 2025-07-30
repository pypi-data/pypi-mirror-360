from pathlib import Path
import typer

from datatrack.linter import lint_schema, load_latest_snapshot as load_lint_snapshot
from datatrack.tracker import snapshot
from datatrack.verifier import load_latest_snapshot as load_ver_snapshot, load_rules, verify_schema
from datatrack.diff import load_snapshots, diff_schemas
from datatrack.exporter import export_snapshot, export_diff

app = typer.Typer()

@app.command("run")
def run_pipeline(
    source: str = typer.Option(..., help="Database source URI"),
    export_dir: str = typer.Option(".pipeline_output", help="Where to save outputs"),
    verbose: bool = typer.Option(True, help="Print detailed output")
):
    print("=" * 50)
    print("           Running DataTrack Pipeline")
    print("=" * 50)

    # Linting
    print("\n[1] Linting schema...")
    try:
        linted = load_lint_snapshot()
        lint_warnings = lint_schema(linted)
        if lint_warnings:
            print("Warnings:")
            for warn in lint_warnings:
                print(f"  - {warn}")
        else:
            print("No linting issues found.")
    except Exception as e:
        print(f"Error during linting: {e}")

    # Snapshot
    print("\n[2] Taking snapshot...")
    try:
        snapshot(source)
        print("Snapshot saved successfully.")
    except Exception as e:
        print(f"Snapshot error: {e}")
        return

    # Verify
    print("\n[3] Verifying schema...")
    try:
        schema = load_ver_snapshot()
        rules = load_rules()
        violations = verify_schema(schema, rules)
        if violations:
            print("Verification failed:")
            for v in violations:
                print(f"  - {v}")
        else:
            print("Schema verification passed.")
    except Exception as e:
        print(f"Verification error: {e}")

    # Diff
    print("\n[4] Computing schema diff...")
    try:
        old, new = load_snapshots()
        diff_schemas(old, new)
    except Exception as e:
        print(f"Diff skipped: {e}")

    # Export
    print("\n[5] Exporting snapshot and diff...")
    try:
        export_snapshot(f"{export_dir}/latest_snapshot.json", "json")
        export_diff(f"{export_dir}/latest_diff.json", "json")
        print(f"Exported to directory: {export_dir}")
    except Exception as e:
        print(f"Export failed: {e}")

    print("\nPipeline completed successfully.")
    print("=" * 50)