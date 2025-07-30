from pathlib import Path

import yaml


def print_history():
    snapshot_dir = Path(".datatrack/snapshots")
    if not snapshot_dir.exists():
        print("No snapshot directory found.")
        return

    snapshots = sorted(snapshot_dir.glob("*.yaml"), reverse=True)

    if not snapshots:
        print("No snapshots found.")
        return

    print("\nSnapshot History (latest first):\n")
    print(f"{'Timestamp':<25} | {'Tables':<7} | Filename")
    print("-" * 60)

    for snap_file in snapshots:
        timestamp = snap_file.stem  # filename without .yaml
        try:
            snap_data = yaml.safe_load(open(snap_file))
            table_count = len(snap_data.get("tables", []))
        except Exception:
            table_count = "ERR"

        print(f"{timestamp:<25} | {table_count:<7} | {snap_file.name}")
