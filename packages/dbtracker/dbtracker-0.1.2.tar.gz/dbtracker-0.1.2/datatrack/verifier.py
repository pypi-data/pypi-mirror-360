# datatrack/verifier.py

import re
from pathlib import Path

import yaml

DEFAULT_RULES = {
    "enforce_snake_case": True,
    "reserved_keywords": {
        "select",
        "from",
        "table",
        "drop",
        "insert",
        "update",
        "delete",
        "create",
        "alter",
        "rename",
        "join",
        "where",
        "group",
        "by",
        "having",
        "order",
        "limit",
        "offset",
        "union",
        "intersect",
        "except",
        "as",
        "on",
        "in",
        "not",
        "is",
        "null",
        "and",
        "or",
        "like",
        "between",
        "exists",
    },
}


def load_latest_snapshot():
    snap_dir = Path(".datatrack/snapshots")
    snapshots = sorted(snap_dir.glob("*.yaml"), reverse=True)
    if not snapshots:
        raise ValueError("❗ No snapshots found to verify.")
    with open(snapshots[0]) as f:
        return yaml.safe_load(f)


def load_rules():
    rules_path = Path("schema_rules.yaml")  # 🔄 Now loading from root
    if rules_path.exists():
        with open(rules_path) as f:
            config = yaml.safe_load(f)
            return {
                "enforce_snake_case": config["rules"].get("enforce_snake_case", True),
                "reserved_keywords": set(config["rules"].get("reserved_keywords", [])),
            }
    return DEFAULT_RULES


def is_snake_case(name: str) -> bool:
    return bool(re.match(r"^[a-z0-9_]+$", name))


def verify_schema(schema: dict, rules: dict) -> list[str]:
    violations = []

    enforce_snake = rules.get("enforce_snake_case", True)
    reserved = rules.get("reserved_keywords", set())

    for table in schema["tables"]:
        table_name = table["name"]

        if enforce_snake and not is_snake_case(table_name):
            violations.append(f"Table name not snake_case: {table_name}")

        if table_name in reserved:
            violations.append(f"Table name uses reserved word: {table_name}")

        for col in table["columns"]:
            col_name = col["name"]

            if enforce_snake and not is_snake_case(col_name):
                violations.append(f"{table_name}.{col_name} not snake_case")

            if col_name in reserved:
                violations.append(f"{table_name}.{col_name} uses reserved word")

    return violations
