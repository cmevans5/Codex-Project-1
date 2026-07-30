# Scheduling Specification

## 1. Objective

Select the fairest eligible 20-member roster for each Blue Battlefield date
without rewarding low latency, fast hardware, or signup-button spam.

## 2. Event calendar and roster

Blue Battlefield signup events run on six days each week: Sunday through Friday.
Saturday is the guild off day and the scheduler must reject Saturday events.

| Assignment | Slots |
|---|---:|
| Guild Galley Cannon | 7 |
| Guild Galley Driver | 1 |
| Player Ship | 12 |
| **Total** | **20** |

A signup may list multiple acceptable assignments, but a member can receive only
one assignment on a date.

## 3. Attendance credits

- One eligible daily absence earns one unit.
- One unit applies to one future event date.
- A member can request and spend at most one unit on a date.
- An absence never guarantees multiple days.
- An available requested unit is the first ranking factor for an eligible role.
- A unit is deducted only when the member receives a confirmed assignment.
- A waitlisted, rejected, withdrawn, or cancelled signup does not consume a unit.
- A member cannot earn and spend a unit for the same event date.
- Imported absences are unique by member ID and source event date.
- Corrections must record actor, timestamp, reason, and before/after value.

“Guaranteed” means the unit outranks candidates without an applied unit. It does
not bypass role eligibility, deadline, active-status, duplicate-assignment, or
capacity rules. If more credited eligible candidates request a role than it has
seats, the remaining fairness factors order those credited candidates.

## 4. Eligibility

A candidate is eligible only when all are true:

1. The signup was submitted by the deadline.
2. The member is active and not suspended.
3. The member selected an eligible role.
4. A ship volunteer selected an accepted ship.
5. A NOL flag is used only on a NOL-compatible ship.
6. The member is not already assigned on that date.
7. Any published leadership readiness requirement is met.

Signup timestamp is retained for audit and deadline enforcement only.

## 5. Selection

The scheduler fills roles independently:

1. Rank Guild Galley Driver volunteers and select up to 1.
2. Exclude assigned members, rank Guild Galley Cannon volunteers, and select up to 7.
3. Exclude assigned members, rank Player Ship volunteers, and select up to 12.
4. Publish remaining eligible volunteers as ordered per-role waitlists.

An undersubscribed role remains visibly unfilled until a published substitution
or reassignment policy is configured. The engine must not silently change the
7/1/12 composition.

## 6. Ranking policy

Version 1 uses lexicographic ranking:

1. Requested and available attendance credit earned in the same calendar month
2. Fewer confirmed appearances earlier in that calendar month
3. More valid waitlists earlier in that calendar month
4. Deterministic rotating value derived from member ID, event date, and role

The fairness cycle is one calendar month in the guild's configured timezone. At
00:00 on the first day of a month, selection counts, waitlist counts, and
spendable attendance-credit balances begin at zero. Prior-month records remain
permanently available for audit and reports but never affect the new month's
ranking. Only events before the schedule being generated may be counted.
Ship class, ship tier, Carrack variant, NOL ownership, and signup timestamp never
contribute priority.

## 7. Ship eligibility

Standard and NOL options:

- Carrack: Balance
- Carrack: Advance
- Carrack: Valor
- Carrack: Volante
- Panokseon

Standard option only:

- Improved Epheria Sailboat
- Improved Epheria Frigate
- Epheria Caravel
- Epheria Galleass
- Epheria Star

The model stores base ship/variant and NOL capability separately. It must not
invent NOL choices for ships that do not generally have one. Every accepted ship
is equally eligible for one of the 12 Player Ship positions.

## 8. Required records

### Member

- immutable member ID
- Discord ID
- family/display name
- active/suspended status
- eligible roles
- owned ships and capabilities
- readiness flags

### Event

- event date
- signup-open and deadline timestamps
- status
- policy version

### Signup

- member ID and event date
- acceptable roles
- offered ship and NOL flag
- attendance-credit request
- submitted timestamp and status

### Attendance ledger

The ledger is append-only and retains every historical BBF outcome needed to
reconstruct each monthly fairness cycle. Corrections supersede prior entries;
they do not delete history. Credits are keyed to the calendar month in which the
eligible absence occurred and cannot be spent in a later month.

- member ID and source event date
- entry type: earned, spent, correction, expired
- units, reason, related event/signup
- actor and timestamp

### Assignment

- event date, member ID, role
- role rank and score components
- confirmed/attended/no-show status

## 9. Audit output

Each considered candidate receives:

- role considered
- selection/waitlist/rejection result and rank
- whether a credit was requested, available, and spent
- current-month confirmed appearances and valid waitlists
- monthly cycle identifier
- deterministic rotation value
- eligibility failure reasons
- policy version

## 10. Acceptance criteria

1. Events are available Sunday through Friday and reject Saturday.
2. A complete roster is exactly 7 cannon, 1 driver, and 12 ship assignments.
3. No member appears twice on one date.
4. Duplicate absence imports create only one unit per member/source date.
5. Multiple absences create multiple units, but at most one is spent per future date.
6. Waitlisted or rejected candidates do not spend requested credits.
7. A selected candidate with an available requested credit spends exactly one.
8. Signup time cannot alter ranking among on-time signups.
9. Identical inputs produce identical results; tie ordering rotates by event date.
10. Ineligible roles, ships, NOL combinations, and late signups are rejected.
11. All listed ships remain eligible, with NOL only where specified.
12. Ship tier, variant, and NOL never change ranking.
13. Every selection and waitlist outcome exposes ranking factors and policy version.
14. Earlier attendance in the same month affects ranking regardless of its age within that month.
15. Prior-month attendance and unused credits do not affect a new month's ranking.
16. Replaying the complete ledger reproduces the same monthly totals and selection result.
