from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from io import TextIOBase

from .scheduler import AttendanceLedger


REQUIRED_COLUMNS = {
    "member_id",
    "event_date",
    "attendance_status",
    "eligible_absence",
}


@dataclass(frozen=True)
class ImportPreview:
    accepted: tuple[tuple[str, date], ...]
    duplicates: tuple[tuple[str, date], ...]
    rejected: tuple[tuple[int, str], ...]


def preview_attendance_csv(source: TextIOBase, ledger: AttendanceLedger) -> ImportPreview:
    reader = csv.DictReader(source)
    missing = REQUIRED_COLUMNS - set(reader.fieldnames or ())
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    accepted: list[tuple[str, date]] = []
    duplicates: list[tuple[str, date]] = []
    rejected: list[tuple[int, str]] = []
    seen = {key: set(value) for key, value in ledger.earned_sources.items()}

    for line_number, row in enumerate(reader, start=2):
        try:
            member_id = row["member_id"].strip()
            event_date = date.fromisoformat(row["event_date"].strip())
            is_absent = row["attendance_status"].strip().lower() == "absent"
            eligible = row["eligible_absence"].strip().lower() in {"true", "1", "yes"}
            if not member_id or not is_absent or not eligible:
                raise ValueError("row is not an eligible absence")
        except (KeyError, ValueError) as exc:
            rejected.append((line_number, str(exc)))
            continue

        known = seen.setdefault(member_id, set())
        item = (member_id, event_date)
        if event_date in known:
            duplicates.append(item)
        else:
            accepted.append(item)
            known.add(event_date)

    return ImportPreview(tuple(accepted), tuple(duplicates), tuple(rejected))


def apply_import(preview: ImportPreview, ledger: AttendanceLedger) -> int:
    return sum(ledger.earn(member_id, event_date) for member_id, event_date in preview.accepted)
