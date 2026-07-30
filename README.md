# Blue Battlefield Attendance Scheduler

A fair, auditable signup and roster-selection system for **Black Desert Online Blue Battlefield** guild attendance.

This project replaces first-click-wins Raid Helper selection with a weighted system that rewards members who have missed eligible days while still filling required battlefield roles.

## Core rules

- Blue Battlefield occurs daily.
- A member earns **one attendance-credit unit for each eligible day they are absent**.
- A member may spend **at most one unit on one future day**; an absence never guarantees multiple days.
- Credits raise priority for a day but do not override role eligibility or duplicate-booking rules.
- Each roster contains exactly 20 positions:
  - 7 Guild Galley Cannon positions
  - 1 Guild Galley Driver position
  - 12 Ship positions
- Ship signup choices include:
  - Balance
  - Balance with Nol
  - Advance
  - Advance with Nol
  - Improved Sailboat
  - Improved Frigate
  - Caravel
  - Galleass
  - Valor
  - Volante
  - Panokseon
  - Other leadership-approved ship
- All rankings must be explainable: leadership and members can see the factors that produced selection, waitlist order, and credit use.
- Ties use a deterministic rotating tiebreaker, not signup speed.

## Planned workflow

1. Leadership imports the attendance CSV.
2. Members sign up for a specific date and eligible role(s).
3. The scheduler validates roles and calculates priority.
4. It publishes the 20-person roster plus ordered waitlists.
5. Attendance is recorded after the event.
6. Credits are earned or consumed according to the rules in [docs/SCHEDULING_SPEC.md](docs/SCHEDULING_SPEC.md).

## Repository status

This initial commit establishes the product rules, data contract, scoring design, and acceptance criteria. Implementation work will proceed against those written rules so the project remains testable and auditable.

## Files

- [Scheduling specification](docs/SCHEDULING_SPEC.md)
- [Attendance import template](data/attendance-template.csv)
- [Implementation roadmap](docs/ROADMAP.md)

## Project name

The current GitHub repository is named `Codex-Project-1`. The intended product name is **Blue Battlefield Attendance Scheduler**.
