# UI and Discord interaction specification

## Product principle

The interface must feel native in Discord while providing a responsive web
dashboard for tasks that exceed Discord component limits. Discord and web are
two clients for the same weekly-plan, roster, attendance, and audit services.
Neither client owns separate scheduling logic.

## Member lifecycle

1. A single persistent Discord message announces the next Sunday–Friday week.
2. `Plan My Week` opens a private Discord interaction.
3. The member selects available dates. If Discord component limits make the
   remaining form cumbersome, `Finish Weekly Plan` opens a short-lived,
   Discord-authenticated web session at the same draft.
4. For each date, the member ranks acceptable roles and optionally agrees to be
   a precommitted standby.
5. Ship selection appears only when Player Ship is selected.
6. NOL appears only for Carrack Balance, Advance, Valor, Volante, and Panokseon.
7. The member may request at most one available credit per date.
8. The member acknowledges the commitment and submits all six dates together.
9. Edits before the deadline do not change priority. After the deadline, late
   availability cannot displace the published roster or an on-time standby.

## Discord component map

### Public weekly event message

- Week dates and fixed signup deadline
- Number of members submitted; never display signup order
- `Plan My Week`
- `View My Plan`
- `View Published Rosters`
- Leadership-only `Manage Week`

### Private plan interaction

- Date multi-select: Sunday through Friday
- Per-date role preference select: Cannon, Driver, Player Ship
- Conditional ship select
- Conditional NOL toggle
- Precommitted standby toggle
- Attendance-credit toggle with private balance
- `Previous`, `Next`, `Save Draft`, and `Submit Week`

### Published roster message

- One message/thread per date
- Exact 7 Cannon, 1 Driver, and 12 Player Ship sections
- Compatible ordered standby sections
- `My Fairness Explanation` returns an ephemeral/private response
- `Withdraw` records the withdrawal and starts promotion from only the
  precommitted compatible standby pool

## Web views

- My Week: bulk six-day availability and preferences
- Published Rosters: final assignments and precommitted standbys
- My Fairness: private monthly factors and permanent historical ledger
- Leadership Week Dashboard: coverage gaps, roster generation, imports,
  attendance outcomes, corrections, overrides, and audit snapshots

## Accessibility and responsive rules

- All controls have labels and keyboard access.
- Status never depends only on color.
- Mobile layout is usable at 320 CSS pixels.
- Discord interactions use plain language and fit within current select, button,
  modal, and message limits.
- Member attendance counts and credit balances are private.
- Public surfaces show the roster and standby order, not personal fairness data.

## Shared API boundary

The production clients should use these service operations:

- `GET/PUT /weeks/{week}/members/{discord_user_id}/plan`
- `POST /weeks/{week}/members/{discord_user_id}/submit`
- `POST /weeks/{week}/generate`
- `GET /events/{date}/roster`
- `POST /events/{date}/withdraw`
- `POST /events/{date}/promotions/{promotion_id}/accept`
- `GET /events/{date}/members/{discord_user_id}/explanation`
- `POST /events/{date}/attendance`
- `POST /attendance/imports/preview`
- `POST /attendance/imports/{import_id}/commit`

Every mutation must be idempotent and authorized through a Discord guild
membership and role check. Roster generation must snapshot the policy version,
deadline, normalized candidate pool, ledger state, and resulting assignments.

## Prototype

Open `ui/index.html` in a browser. It is a dependency-free interactive product
prototype for validating the information architecture before connecting
persistence and Discord OAuth.
