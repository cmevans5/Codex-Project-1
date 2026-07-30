# Implementation Roadmap

## Milestone 1 — Scheduling engine

- Define typed member, event, signup, ledger, and assignment models.
- Implement role-constrained ranking.
- Implement the one-credit-per-day ledger rules.
- Add deterministic rotation and unit tests for every acceptance criterion.

## Milestone 2 — Attendance import

- Validate CSV headings and dates.
- Make imports idempotent.
- Produce a preview showing accepted, duplicate, and rejected rows.
- Require confirmation before writing ledger corrections.

## Milestone 3 — Discord workflow

- Create daily signup posts.
- Allow role and ship selection.
- Publish roster and waitlists.
- Send substitutions when a selected member withdraws.

## Milestone 4 — Leadership dashboard

- Review explanations and ledger history.
- Correct attendance with mandatory reasons.
- Configure deadlines, rolling window, and role readiness.
- Export roster, attendance, and audit data.

## Definition of done

The system is ready for guild use when all acceptance tests pass, the Discord workflow can fill and substitute a complete 20-member roster, and every selection can be reconstructed from stored inputs.
