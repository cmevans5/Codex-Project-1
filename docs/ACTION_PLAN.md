# Iteration Action Plan

## Goal

Deliver a fair, auditable six-day Blue Battlefield scheduler that replaces
first-click-wins selection and minimizes manual leadership intervention.

## Phase 1 — Restore the governing rules

- Keep exactly 20 daily positions: 7 galley cannon, 1 galley driver, 12 ships.
- Open events Sunday through Friday; Saturday is the guild off day.
- Preserve one eligible absence as one attendance-credit unit.
- Permit at most one unit to be used by a member on one future event date.
- Keep all eligible ships equal in priority; ship tier and NOL never add weight.
- Offer NOL only for Carrack variants and Panokseon.
- Keep Improved Epheria Sailboat, Improved Epheria Frigate, Epheria Caravel,
  Epheria Galleass, and Epheria Star eligible without NOL variants.

Success criterion: specification and acceptance tests contain no conflicting ship
or attendance rules.

## Phase 2 — Build the scheduling core

- Define typed member, event, signup, role, ship, assignment, and ledger records.
- Validate deadlines, active status, roles, ships, NOL compatibility, and Saturday.
- Select independently by role in driver, cannon, then ship order.
- Rank lexicographically by requested available current-month credit, fewer
  current-month selections, more current-month waitlists, and deterministic rotation.
- Reset all ranking totals and spendable credits on the first of each calendar month.
- Retain prior-month outcomes permanently for audit, reporting, and policy review,
  while excluding them from the new monthly fairness cycle.
- Ignore signup time after deadline validation.
- Emit selected assignments, ordered waitlists, rejections, and score explanations.

Success criterion: the same inputs always reproduce the same explained roster.

## Phase 3 — Make attendance imports safe

- Parse an Excel-exported CSV using stable member IDs and event dates.
- Preview accepted, duplicate, and rejected rows.
- Deduplicate eligible absences by member and source event date.
- Apply only confirmed preview rows.

Success criterion: repeated imports cannot mint repeated attendance credits.

## Phase 4 — Verify the original design

- Test exact roster capacity and no duplicate daily assignments.
- Test credit priority and one-unit-per-day spending.
- Test that waitlisted candidates retain their requested credit.
- Test signup-speed neutrality and deterministic rotation.
- Test that every earlier date in the same month changes monthly priority.
- Test that prior-month attendance and unused credits cannot affect the new month.
- Test full-ledger replay and correction history produce reproducible monthly totals.
- Test every eligible ship and NOL compatibility rule.
- Test six-day scheduling by rejecting Saturdays.

Success criterion: the automated test suite passes without external dependencies.

## Phase 5 — Integrate the guild workflow

- Add persistent storage and transactional roster publication.
- Build daily Discord signup controls for role and compatible ship options.
- Add leadership import preview, correction reasons, and substitution controls.
- Publish member-visible roster explanations and ordered waitlists.
- Pilot in shadow mode beside Raid Helper before switching roster authority.

Success criterion: leadership can import, schedule, substitute, record attendance,
and reconstruct a result without manually rearranging a full roster.
