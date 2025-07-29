# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from pathlib import Path
from typing import List

from polaris.utils.testing.model_comparison.compare_tables import compare_tables
from polaris.utils.testing.model_comparison.get_csv_table import get_table_from_disk


def compare_table_dumps(old_path: Path, new_path: Path) -> List[str]:

    npath = Path(new_path)
    opath = Path(old_path)

    new_files = [x.stem for x in npath.glob("*.csv")] + [x.stem for x in npath.glob("*.parquet")]
    old_files = [x.stem for x in opath.glob("*.csv")] + [x.stem for x in opath.glob("*.parquet")]
    report = []

    dropped_files = [x for x in old_files if x not in new_files]
    if dropped_files:
        report.extend(["**Dropped tables**:\n", f"{', '.join(dropped_files)}\n"])
    else:
        report.append("**No dropped tables**\n")

    added_files = [x for x in new_files if x not in old_files]
    if added_files:
        report.extend(["**New tables**:\n", f"{', '.join(added_files)}\n"])
    else:
        report.append("**No new tables**\n")

    # Compares one table at a time
    no_change = []
    table_changes = []
    for table in new_files:
        if table not in old_files:
            continue
        print(f"Comparing: {table}")
        old_table = opath / f"{table}.csv" if (opath / f"{table}.csv").exists() else opath / f"{table}.parquet"
        new_table = npath / f"{table}.csv" if (npath / f"{table}.csv").exists() else npath / f"{table}.parquet"
        table_report = compare_tables(get_table_from_disk(old_table), get_table_from_disk(new_table))
        if len(table_report):
            table_changes.append(f"\n * {table}:\n")
            table_changes.extend(table_report)
        else:
            no_change.append(table)

    if no_change:
        report.extend(["**Tables with no changes**:\n", f"{', '.join(no_change)}\n"])

    if table_changes:
        report.append("\n\n**Tables with changes**:")
        report.extend(table_changes)

    return report
