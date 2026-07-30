# Scheduling Specification

## 1. Objective

Select the fairest eligible 20-member roster for each Blue Battlefield date without rewarding low latency, fast hardware, or repeated signup-button spam.

## 2. Daily roster

| Assignment | Slots |
|---|---:|
| Guild Galley Cannon | 7 |
| Guild Galley Driver | 1 |
| Player Ship | 12 |
| **Total** | **20** |

A signup may list multiple acceptable assignments, but a member can receive only one assignment on a date.

## 3. Attendance credits

Attendance credits represent daily priority units.

- One eligible absence earns one unit.
- One unit can be applied to one signup date.
- No more than one unit can be spent by a member on a date.
- Applying a unit increases priority for that date only.
- A spent unit is deducted only when the member receives a confirmed roster slot.
- A waitlisted or cancelled signup does not consume a unit.
- A member cannot earn and spend a unit for the same date.
- Leadership corrections must be logged with actor, timestamp, reason, and before/after values.
- Imported historical absences must be date-based so duplicate rows cannot mint duplicate units.

## 4. Eligibility

A candidate is eligible only when all are true:

1. The signup was submitted before the deadline.
2. The member is not already assigned on that date.
3. The member selected the role or owns an accepted ship for the role.
4. Any leadership-defined readiness requirement is met.
5. The account is active and not suspended from signup.

Signup timestamp never contributes points. It is retained only for audit and deadline enforcement.

## 5. Selection order

Selection is role-constrained rather than one global top-20 list:

1. Rank eligible Guild Galley Driver volunteers; select 1.
2. Rank eligible Guild Galley Cannon volunteers; select 7.
3. Rank eligible Ship volunteers; select 12.
4. Put remaining eligible volunteers into an ordered waitlist for the assignment.
5. If an assignment lacks candidates, apply the published reassignment policy and rerun validation.

## 6. Priority model

Version 1 uses lexicographic ranking to keep guarantees and fairness interpretable:

1. **Applied attendance credit:** applied first; maximum one.
2. **Recent selection deficit:** fewer confirmed appearances in the rolling window ranks higher.
3. **Recent waitlist history:** more recent valid waitlists rank higher.
4. **Rotation value:** deterministic rotating tiebreak derived from member ID and event date.

This is intentionally not a hidden weighted sum. A lower-level factor cannot silently overpower an applied attendance credit.

Suggested initial rolling window: 14 completed battlefield dates. This remains configurable and must be displayed alongside every published ranking.

## 7. Ship types

Accepted signup values:

- Carrack: Balance
- Carrack: Balance with NOL
- Carrack: Advance
- Carrack: Advance with NOL
- Carrack: Valor
- Carrack: Valor with NOL
- Carrack: Volante
- Carrack: Volante with NOL
- Panokseon
- Panokseon with NOL
- Epheria Star
- Epheria Star with NOL

No other ship type is eligible for a Ship position. In particular, the scheduler must reject Improved Sailboat, Improved Frigate, Caravel, Galleass, and free-form or leadership-approved “other” ships.

The data model stores the base ship type, Carrack variant when applicable, and NOL status as separate fields. The signup interface displays both the standard and `with NOL` choice for every accepted ship and Carrack variant. It must not assume that all eligible ship types are equivalent for future composition rules.

## 8. Required records

### Member

- immutable member ID
- Discord ID
- family/display name
- active status
- eligible roles
- owned ship types
- readiness flags

### Event

- event date
- signup open/deadline timestamps
- status
- scoring-policy version

### Signup

- member ID
- event date
- acceptable roles
- ship offered
- attendance-credit requested
- submitted timestamp
- status

### Attendance ledger

- member ID
- source event date
- entry type: earned, spent, correction, expired
- units
- reason
- related signup/event
- actor and timestamp

### Assignment

- event date
- member ID
- assignment type
- selection rank
- score components
- confirmed/attended/no-show status

## 9. Audit output

Every scheduled member and waitlisted member receives an explanation containing:

- assignment considered
- whether a credit was applied
- rolling confirmed appearances
- recent valid waitlists
- rotation value
- eligibility failures, if any
- policy version

## 10. Acceptance tests

1. Twenty slots are produced only as 7 cannon, 1 driver, and 12 ship assignments.
2. No member appears twice on one date.
3. Two imports of the same absence row create only one earned unit.
4. Two absences produce two units, but only one can be applied per future date.
5. A waitlisted signup never spends its requested unit.
6. A selected signup spends exactly one requested unit.
7. Signup timestamp does not alter rank among on-time signups.
8. Identical candidates resolve deterministically and rotate over time.
9. A member cannot be assigned to an ineligible role or unaccepted ship.
10. Every accepted ship and Carrack variant has both standard and with-NOL choices.
11. Improved Sailboat, Improved Frigate, Caravel, Galleass, and “other” ships are rejected.
12. Every outcome exposes its score components and policy version.
