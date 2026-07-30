# Blue Battlefield Attendance Scheduler

A fair, auditable signup and roster-selection system for **Black Desert Online
Blue Battlefield** guild attendance. It replaces first-click-wins Raid Helper
selection with deterministic, role-constrained ranking.

## Implemented MVP

The repository now includes a dependency-free Python scheduling engine and tests.
It produces assignments, ordered role waitlists, rejection reasons, and auditable
score explanations.

Run the tests:

```bash
python -m unittest discover -s tests -v
```

## Governing rules

- Events run Sunday through Friday; Saturday is the guild off day.
- Each event has exactly 20 available positions:
  - 7 Guild Galley Cannon positions
  - 1 Guild Galley Driver position
  - 12 Player Ship positions
- One eligible absence earns one attendance-credit unit.
- A member can request and spend at most one unit for one future event date.
- A unit is spent only if the member is selected, never while waitlisted.
- Signup time enforces the deadline but never improves ranking.
- All eligible ships rank equally. Ship tier, Carrack variant, and NOL ownership
  add no selection weight.
- Every completed attendance and waitlist outcome is retained permanently and influences future fairness.
- Recent history is used only after lifetime totals, preventing both long-term imbalance and short-term streaks.
- Ties use a deterministic rotating value, not signup speed.

## Eligible player ships

These ships are eligible with standard and NOL signup options:

- Carrack: Balance
- Carrack: Advance
- Carrack: Valor
- Carrack: Volante
- Panokseon

These ships are eligible without a NOL signup option:

- Improved Epheria Sailboat
- Improved Epheria Frigate
- Epheria Caravel
- Epheria Galleass
- Epheria Star

## Selection order

Each role is filled independently:

1. Requested available attendance credit
2. Fewer confirmed appearances across all completed historical dates
3. Fewer confirmed appearances in the recent rolling window
4. More valid historical waitlists
5. More valid waitlists in the recent rolling window
6. Deterministic rotating tiebreak

Members may volunteer for multiple roles but can receive only one assignment on
an event date.

## Repository map

- [`blue_battlefield/scheduler.py`](blue_battlefield/scheduler.py): models,
  validation, ranking, assignment, waitlists, and explanations
- [`blue_battlefield/importer.py`](blue_battlefield/importer.py): safe CSV preview
  and idempotent attendance-credit import
- [`tests/test_scheduler.py`](tests/test_scheduler.py): automated acceptance tests
- [`docs/SCHEDULING_SPEC.md`](docs/SCHEDULING_SPEC.md): governing specification
- [`docs/ACTION_PLAN.md`](docs/ACTION_PLAN.md): phased iteration plan
- [`docs/ROADMAP.md`](docs/ROADMAP.md): next integration milestones
- [`data/attendance-template.csv`](data/attendance-template.csv): Excel-compatible
  attendance import template

## Current boundary

This release implements and tests the domain engine. Persistence, Discord
components, leadership controls, and live roster publication remain the next
integration phase.
