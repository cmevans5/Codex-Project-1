from datetime import date, datetime, timedelta
import unittest

from blue_battlefield.importer import apply_import, preview_attendance_csv
from blue_battlefield.scheduler import (
    AttendanceHistory,
    AttendanceLedger,
    Event,
    Member,
    NOL_COMPATIBLE_SHIPS,
    Role,
    Scheduler,
    Ship,
    Signup,
)
from io import StringIO


DEADLINE = datetime(2026, 7, 30, 18, 0)
EVENT = Event(date(2026, 7, 30), DEADLINE)


def member(number: int, roles: frozenset[Role]) -> Member:
    return Member(f"m{number:02}", f"Member {number}", roles)


def signup(number: int, role: Role, **kwargs) -> Signup:
    ship = Ship.CARAVEL if role is Role.SHIP else None
    return Signup(f"m{number:02}", (role,), DEADLINE - timedelta(hours=number), ship=ship, **kwargs)


class SchedulerTests(unittest.TestCase):
    def test_exact_roster_shape(self) -> None:
        members = (
            [member(0, frozenset({Role.DRIVER}))]
            + [member(i, frozenset({Role.CANNON})) for i in range(1, 8)]
            + [member(i, frozenset({Role.SHIP})) for i in range(8, 20)]
        )
        signups = (
            [signup(0, Role.DRIVER)]
            + [signup(i, Role.CANNON) for i in range(1, 8)]
            + [signup(i, Role.SHIP) for i in range(8, 20)]
        )
        result = Scheduler().schedule(EVENT, members, signups, AttendanceLedger())
        counts = {role: sum(a.role is role for a in result.assignments) for role in Role}
        self.assertEqual(counts, {Role.DRIVER: 1, Role.CANNON: 7, Role.SHIP: 12})

    def test_credit_beats_other_factors_and_only_spends_when_selected(self) -> None:
        members = [member(i, frozenset({Role.DRIVER})) for i in range(2)]
        ledger = AttendanceLedger()
        ledger.earn("m01", date(2026, 7, 29))
        signups = [signup(0, Role.DRIVER), signup(1, Role.DRIVER, request_credit=True)]
        history = {"m01": AttendanceHistory(confirmed_dates=frozenset({date(2026, 7, 28)}))}
        result = Scheduler().schedule(EVENT, members, signups, ledger, history)
        self.assertEqual(result.assignments[0].member_id, "m01")
        self.assertEqual(ledger.balance("m01"), 0)

    def test_waitlisted_credit_is_not_spent(self) -> None:
        members = [member(i, frozenset({Role.DRIVER})) for i in range(2)]
        ledger = AttendanceLedger()
        for member_id in ("m00", "m01"):
            ledger.earn(member_id, date(2026, 7, 29))
        result = Scheduler().schedule(
            EVENT,
            members,
            [signup(0, Role.DRIVER, request_credit=True), signup(1, Role.DRIVER, request_credit=True)],
            ledger,
        )
        waitlisted = result.waitlists[Role.DRIVER][0]
        self.assertEqual(ledger.balance(waitlisted), 1)

    def test_signup_time_does_not_control_ranking(self) -> None:
        members = [member(i, frozenset({Role.DRIVER})) for i in range(2)]
        first = [
            Signup("m00", (Role.DRIVER,), DEADLINE - timedelta(hours=5)),
            Signup("m01", (Role.DRIVER,), DEADLINE - timedelta(hours=1)),
        ]
        second = [
            Signup("m00", (Role.DRIVER,), DEADLINE - timedelta(hours=1)),
            Signup("m01", (Role.DRIVER,), DEADLINE - timedelta(hours=5)),
        ]
        first_result = Scheduler().schedule(EVENT, members, first, AttendanceLedger())
        second_result = Scheduler().schedule(EVENT, members, second, AttendanceLedger())
        self.assertEqual(first_result.assignments[0].member_id, second_result.assignments[0].member_id)

    def test_ship_tier_and_nol_do_not_change_rank(self) -> None:
        members = [member(i, frozenset({Role.SHIP})) for i in range(13)]
        base = [
            Signup(f"m{i:02}", (Role.SHIP,), DEADLINE, ship=Ship.CARAVEL)
            for i in range(13)
        ]
        modified = list(base)
        modified[0] = Signup("m00", (Role.SHIP,), DEADLINE, ship=Ship.VALOR, has_nol=True)
        one = Scheduler().schedule(EVENT, members, base, AttendanceLedger())
        two = Scheduler().schedule(EVENT, members, modified, AttendanceLedger())
        self.assertEqual(
            [a.member_id for a in one.assignments], [a.member_id for a in two.assignments]
        )

    def test_nol_is_restricted_but_lower_tier_ships_remain_eligible(self) -> None:
        self.assertNotIn(Ship.CARAVEL, NOL_COMPATIBLE_SHIPS)
        Signup("m00", (Role.SHIP,), DEADLINE, ship=Ship.CARAVEL)
        with self.assertRaises(ValueError):
            Signup("m00", (Role.SHIP,), DEADLINE, ship=Ship.CARAVEL, has_nol=True)

    def test_every_listed_ship_is_eligible_and_only_compatible_ships_accept_nol(self) -> None:
        for ship_type in Ship:
            Signup("m00", (Role.SHIP,), DEADLINE, ship=ship_type)
            if ship_type in NOL_COMPATIBLE_SHIPS:
                Signup("m00", (Role.SHIP,), DEADLINE, ship=ship_type, has_nol=True)
            else:
                with self.assertRaises(ValueError):
                    Signup("m00", (Role.SHIP,), DEADLINE, ship=ship_type, has_nol=True)

    def test_multi_role_member_is_never_assigned_twice(self) -> None:
        flexible = Member("m00", "Flexible", frozenset(Role))
        members = [flexible] + [
            member(i, frozenset({Role.CANNON})) for i in range(1, 8)
        ]
        signups = [
            Signup(
                "m00",
                (Role.DRIVER, Role.CANNON, Role.SHIP),
                DEADLINE,
                ship=Ship.EPHERIA_STAR,
            )
        ] + [signup(i, Role.CANNON) for i in range(1, 8)]
        result = Scheduler().schedule(EVENT, members, signups, AttendanceLedger())
        self.assertEqual(
            sum(assignment.member_id == "m00" for assignment in result.assignments), 1
        )

    def test_attendance_outside_recent_window_still_affects_lifetime_fairness(self) -> None:
        members = [member(i, frozenset({Role.DRIVER})) for i in range(2)]
        old_date = EVENT.event_date - timedelta(days=90)
        history = {"m00": AttendanceHistory(confirmed_dates=frozenset({old_date}))}
        result = Scheduler(rolling_window_days=14).schedule(
            EVENT,
            members,
            [signup(0, Role.DRIVER), signup(1, Role.DRIVER)],
            AttendanceLedger(),
            history,
        )
        self.assertEqual(result.assignments[0].member_id, "m01")
        explanation = next(
            item for item in result.explanations if item.member_id == "m00"
        )
        self.assertEqual(explanation.total_confirmed, 1)
        self.assertEqual(explanation.confirmed_in_window, 0)

    def test_future_history_never_affects_current_ranking(self) -> None:
        members = [member(i, frozenset({Role.DRIVER})) for i in range(2)]
        future_date = EVENT.event_date + timedelta(days=1)
        history = {"m00": AttendanceHistory(confirmed_dates=frozenset({future_date}))}
        baseline = Scheduler().schedule(
            EVENT, members, [signup(0, Role.DRIVER), signup(1, Role.DRIVER)], AttendanceLedger()
        )
        with_future = Scheduler().schedule(
            EVENT, members, [signup(0, Role.DRIVER), signup(1, Role.DRIVER)], AttendanceLedger(), history
        )
        self.assertEqual(baseline.assignments[0].member_id, with_future.assignments[0].member_id)

    def test_saturday_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Event(date(2026, 8, 1), DEADLINE)

    def test_duplicate_absence_import_is_idempotent(self) -> None:
        csv_text = (
            "member_id,event_date,attendance_status,eligible_absence\n"
            "m00,2026-07-29,absent,true\n"
            "m00,2026-07-29,absent,true\n"
        )
        ledger = AttendanceLedger()
        preview = preview_attendance_csv(StringIO(csv_text), ledger)
        self.assertEqual(len(preview.accepted), 1)
        self.assertEqual(len(preview.duplicates), 1)
        self.assertEqual(apply_import(preview, ledger), 1)
        self.assertEqual(ledger.balance("m00"), 1)


if __name__ == "__main__":
    unittest.main()
