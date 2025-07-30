from datetime import datetime
from pathlib import Path

import yaml
from sqlalchemy import create_engine, inspect

SNAPSHORT_DIR = Path(".datatrack/snapshots")


def save_schema_snapshot(schema: dict):
    """
    Save the given schema dict into a timestamped YAML file.
    """
    SNAPSHORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_file = SNAPSHORT_DIR / f"snapshot_{timestamp}.yaml"

    with open(snapshot_file, "w") as f:
        yaml.dump(schema, f)

    return snapshot_file


def snapshot(source: str):
    """
    Connect to the given database source and extract schema details.
    Save the schema snapshot to a timestamped file.
    """
    engine = create_engine(source)
    insp = inspect(engine)

    schema_data = {"tables": []}

    for table_name in insp.get_table_names():
        columns = insp.get_columns(table_name)
        schema_data["tables"].append(
            {
                "name": table_name,
                "columns": [
                    {"name": col["name"], "type": str(col["type"])} for col in columns
                ],
            }
        )

    file_path = save_schema_snapshot(schema_data)
    return file_path
