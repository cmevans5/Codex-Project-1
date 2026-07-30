# Implementation Roadmap

## Completed — Domain MVP

- Governing rules reconciled with the original six-day plan.
- Typed member, event, signup, ship, ledger, assignment, and audit models.
- Exact 7 cannon / 1 driver / 12 ship role constraints.
- Lifetime-first lexicographic fairness ranking, recent anti-streak checks, and deterministic rotation.
- One-credit-per-member-per-event spending behavior.
- Idempotent CSV attendance import preview and apply flow.
- Automated acceptance tests without external dependencies.

## Next — Persistence and policy hardening

- Store members, events, signups, immutable historical outcome/ledger entries, assignments, and policy versions.
- Materialize lifetime and recent fairness totals from the complete ledger and verify them by replay.
- Make scheduling and credit spending one atomic transaction.
- Add explicit withdrawal, cancellation, no-show, and substitution transitions.
- Define leadership readiness flags and undersubscribed-role reassignment policy.
- Expand tests for multi-role volunteers, substitutions, corrections, and concurrency.

## Next — Discord workflow

- Create Sunday-through-Friday signup events.
- Present role controls and ship choices with compatible NOL options only.
- Lock submissions at the configured deadline.
- Publish the 20-person roster, unfilled seats, and ordered waitlists.
- Promote waitlisted candidates when a selected member withdraws.

## Next — Leadership and member views

- Preview Excel/CSV imports before applying ledger entries.
- Require reasons for attendance corrections and roster overrides.
- Display credit balances and complete ledger histories.
- Display selection explanations and policy versions.
- Export roster, attendance, and audit records.

## Rollout

1. Replay historical attendance through the importer.
2. Run the scheduler in shadow mode beside Raid Helper.
3. Compare outcomes and review edge cases with leadership.
4. Freeze policy version 1.0.
5. Switch roster publication authority after a successful pilot.

## Definition of done

The system is ready for guild use when it can persist, publish, substitute, record
attendance, and reconstruct every Sunday-through-Friday result without routine
manual roster rearrangement.
