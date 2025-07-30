from pathlib import Path

import yaml


def load_snapshots():
    """
    Load the two most recent snapshots from the disk.
    """
    snap_dir = Path(".datatrack/snapshots")
    snapshots = sorted(snap_dir.glob("*.yaml"), reverse=True)

    if len(snapshots) < 2:
        raise FileNotFoundError("Need at least 2 snapshots to run a diff.")

    with open(snapshots[0], "r") as f1, open(snapshots[1], "r") as f2:
        newer = yaml.safe_load(f1)
        older = yaml.safe_load(f2)

    return older, newer


def diff_schemas(old, new):
    """
    Print diff of tables and columns between two schema snapshots.
    """

    old_tables = {t["name"]: t for t in old["tables"]}
    new_tables = {t["name"]: t for t in new["tables"]}

    # Table-level diff
    old_set = set(old_tables)
    new_set = set(new_tables)

    added_tables = new_set - old_set
    removed_tables = old_set - new_set
    common_tables = old_set & new_set

    table_changes = []
    column_changes = []

    print("\nTables Changes:")
    for t in added_tables:
        line = f"  + Added table: {t}"
        print(line)
        table_changes.append(line)
    for t in removed_tables:
        line = f"  - Removed table: {t}"
        print(line)
        table_changes.append(line)
    if not table_changes:
        print("\tNo tables added or removed.")

    # Column-level diff for unchanged tables
    print("\nColumn Changes:")
    for table in common_tables:
        old_cols = {col["name"]: col["type"] for col in old_tables[table]["columns"]}
        new_cols = {col["name"]: col["type"] for col in new_tables[table]["columns"]}

        old_col_set = set(old_cols)
        new_col_set = set(new_cols)

        added_cols = new_col_set - old_col_set
        removed_cols = old_col_set - new_col_set
        common_cols = old_col_set & new_col_set

        for col in added_cols:
            line = f"+ Added column: {col} ({new_cols[col]})"
            print(line)
            column_changes.append(line)
        for col in removed_cols:
            line = f"- Removed column: {col} ({old_cols[col]})"
            print(line)
            column_changes.append(line)
        for col in common_cols:
            if old_cols[col] != new_cols[col]:
                line = f"~ Changed column: {col} ({old_cols[col]} -> {new_cols[col]})"
                print(line)
                column_changes.append(line)
    if not column_changes:
        print("\tNo columns added, removed or changed in common tables.")

    if not table_changes and not column_changes:
        print("\nNo schema changes detected between the snapshots.\n")
