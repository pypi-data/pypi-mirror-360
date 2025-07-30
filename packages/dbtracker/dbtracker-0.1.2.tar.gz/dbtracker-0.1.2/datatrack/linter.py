from pathlib import Path

import yaml

AMBIGUOUS_NAMES = {
    "data",
    "value",
    "info",
    "details",
    "record",
    "item",
    "object",
    "entity",
    "metadata",
}
GENERIC_TYPES = {
    "string",
    "integer",
    "float",
    "boolean",
    "date",
    "datetime",
    "text",
    "json",
}
MAX_NAME_LENGTH = 30


def load_latest_snapshot():
    snap_dir = Path(".datatrack/snapshots")
    snapshots = sorted(snap_dir.glob("*.yaml"), reverse=True)
    if not snapshots:
        raise ValueError("No snapshots found to verify.")
    with open(snapshots[0]) as f:
        return yaml.safe_load(f)


def lint_schema(schema):
    warnings = []

    for table in schema["tables"]:
        table_name = table["name"]

        if len(table_name) > MAX_NAME_LENGTH:
            warnings.append(
                f"Table name '{table_name}' exceeds max length of {MAX_NAME_LENGTH} characters."
            )

        for col in table["columns"]:
            col_name = col["name"]
            col_type = col["type"]

            if col_name in AMBIGUOUS_NAMES:
                warnings.append(
                    f"Column '{col_name}' in table '{table_name}' has an ambiguous name."
                )

            if col_type in GENERIC_TYPES:
                warnings.append(
                    f"Column '{col_name}' in table '{table_name}' uses a generic type: {col_type}. Consider using a more specific type."
                )

    return warnings
