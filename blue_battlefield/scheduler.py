from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
import hashlib
from typing import Iterable


class Role(str, Enum):
    DRIVER = "guild_galley_driver"
    CANNON = "guild_galley_cannon"
    SHIP = "player_ship"


ROLE_CAPACITY = {Role.DRIVER: 1, Role.CANNON: 7, Role.SHIP: 12}


class Ship(str, Enum):
    BALANCE = "carrack_balance"
    ADVANCE = "carrack_advance"
    VALOR = "carrack_valor"
    VOLANTE = "carrack_volante"
    PANOKSEON = "panokseon"
    IMPROVED_SAILBOAT = "improved_epheria_sailboat"
    IMPROVED_FRIGATE = "improved_epheria_frigate"
    CARAVEL = "epheria_caravel"
    GALLEASS = "epheria_galleass"
    EPHERIA_STAR = "epheria_star"


NOL_COMPATIBLE_SHIPS = {
    Ship.BALANCE,
    Ship.ADVANCE,
    Ship.VALOR,
    Ship.VOLANTE,
    Ship.PANOKSEON,
}


@dataclass(frozen=True)
class Member:
    member_id: str
    display_name: str
    eligible_roles: frozenset[Role]
    active: bool = True


@dataclass(frozen=True)
class Event:
    event_date: date
    signup_deadline: datetime
    policy_version: str = "1.0"

    def __post_init__(self) -> None:
        if self.event_date.weekday() == 5:
            raise ValueError("Saturday is the guild's off day")


@dataclass(frozen=True)
class Signup:
    member_id: str
    acceptable_roles: tuple[Role, ...]
    submitted_at: datetime
    ship: Ship | None = None
    has_nol: bool = False
    request_credit: bool = False

    def __post_init__(self) -> None:
        if Role.SHIP in self.acceptable_roles and self.ship is None:
            raise ValueError("Ship volunteers must identify an eligible ship")
        if self.ship is not None and Role.SHIP not in self.acceptable_roles:
            raise ValueError("A ship can only be offered for the player-ship role")
        if self.has_nol and self.ship not in NOL_COMPATIBLE_SHIPS:
            raise ValueError(f"{self.ship.value} does not support a NOL signup option")


@dataclass(frozen=True)
class AttendanceHistory:
    confirmed_dates: frozenset[date] = frozenset()
    waitlisted_dates: frozenset[date] = frozenset()


@dataclass
class AttendanceLedger:
    earned_sources: dict[str, set[date]] = field(default_factory=dict)
    spent_events: dict[str, set[date]] = field(default_factory=dict)

    def earn(self, member_id: str, source_date: date) -> bool:
        sources = self.earned_sources.setdefault(member_id, set())
        before = len(sources)
        sources.add(source_date)
        return len(sources) != before

    def balance(self, member_id: str) -> int:
        return len(self.earned_sources.get(member_id, set())) - len(
            self.spent_events.get(member_id, set())
        )

    def spend(self, member_id: str, event_date: date) -> None:
        if event_date in self.spent_events.get(member_id, set()):
            raise ValueError("A member may spend at most one credit per event date")
        if self.balance(member_id) < 1:
            raise ValueError("Member has no attendance credit available")
        self.spent_events.setdefault(member_id, set()).add(event_date)


@dataclass(frozen=True)
class CandidateExplanation:
    member_id: str
    role: Role
    selected: bool
    rank: int
    credit_applied: bool
    confirmed_in_month: int
    waitlists_in_month: int
    fairness_cycle: str
    rotation_value: int
    policy_version: str
    reason: str


@dataclass(frozen=True)
class Assignment:
    member_id: str
    role: Role
    rank: int
    credit_spent: bool


@dataclass(frozen=True)
class ScheduleResult:
    assignments: tuple[Assignment, ...]
    waitlists: dict[Role, tuple[str, ...]]
    explanations: tuple[CandidateExplanation, ...]
    rejected: dict[str, tuple[str, ...]]


class Scheduler:
    """Deterministic, role-constrained roster selector.

    Ranking is lexicographic within one calendar month: requested available
    current-month credit, fewer confirmed appearances, more waitlists, then a
    rotating deterministic tiebreak. Older months remain auditable but do not rank.
    Signup time is used only to enforce the deadline.
    """

    def __init__(self, rolling_window_days: int | None = None) -> None:
        # Kept as a compatibility argument; fairness now resets by calendar month.
        self.rolling_window_days = rolling_window_days

    def schedule(
        self,
        event: Event,
        members: Iterable[Member],
        signups: Iterable[Signup],
        ledger: AttendanceLedger,
        history: dict[str, AttendanceHistory] | None = None,
    ) -> ScheduleResult:
        member_map = {member.member_id: member for member in members}
        history = history or {}
        rejected: dict[str, list[str]] = {}
        valid: list[Signup] = []

        for signup in signups:
            reasons: list[str] = []
            member = member_map.get(signup.member_id)
            if member is None:
                reasons.append("unknown member")
            elif not member.active:
                reasons.append("inactive member")
            if signup.submitted_at > event.signup_deadline:
                reasons.append("submitted after deadline")
            if member and not set(signup.acceptable_roles).issubset(member.eligible_roles):
                reasons.append("ineligible role requested")
            if reasons:
                rejected.setdefault(signup.member_id, []).extend(reasons)
            else:
                valid.append(signup)

        assigned_members: set[str] = set()
        assignments: list[Assignment] = []
        explanations: list[CandidateExplanation] = []
        waitlists: dict[Role, tuple[str, ...]] = {}

        for role in (Role.DRIVER, Role.CANNON, Role.SHIP):
            candidates = [
                signup
                for signup in valid
                if role in signup.acceptable_roles and signup.member_id not in assigned_members
            ]
            ranked = sorted(
                candidates,
                key=lambda signup: self._rank_key(
                    signup, role, event, ledger, history.get(signup.member_id)
                ),
            )
            capacity = ROLE_CAPACITY[role]
            selected = ranked[:capacity]
            selected_ids = {signup.member_id for signup in selected}
            waitlists[role] = tuple(
                signup.member_id for signup in ranked if signup.member_id not in selected_ids
            )

            for rank, signup in enumerate(ranked, start=1):
                stats = self._stats(signup.member_id, event, history.get(signup.member_id))
                credit = signup.request_credit and ledger.balance(signup.member_id) > 0
                is_selected = signup.member_id in selected_ids
                explanations.append(
                    CandidateExplanation(
                        member_id=signup.member_id,
                        role=role,
                        selected=is_selected,
                        rank=rank,
                        credit_applied=credit and is_selected,
                        confirmed_in_month=stats[0],
                        waitlists_in_month=stats[1],
                        fairness_cycle=event.event_date.strftime("%Y-%m"),
                        rotation_value=self._rotation(signup.member_id, event.event_date, role),
                        policy_version=event.policy_version,
                        reason="selected" if is_selected else "capacity reached",
                    )
                )

            for rank, signup in enumerate(selected, start=1):
                credit = signup.request_credit and ledger.balance(signup.member_id) > 0
                if credit:
                    ledger.spend(signup.member_id, event.event_date)
                assignments.append(Assignment(signup.member_id, role, rank, credit))
                assigned_members.add(signup.member_id)

        frozen_rejected = {key: tuple(value) for key, value in rejected.items()}
        return ScheduleResult(
            tuple(assignments), waitlists, tuple(explanations), frozen_rejected
        )

    def _stats(
        self, member_id: str, event: Event, history: AttendanceHistory | None
    ) -> tuple[int, int]:
        if not history:
            return (0, 0)
        same_cycle = lambda day: (
            day < event.event_date
            and day.year == event.event_date.year
            and day.month == event.event_date.month
        )
        confirmed = sum(same_cycle(day) for day in history.confirmed_dates)
        waitlisted = sum(same_cycle(day) for day in history.waitlisted_dates)
        return confirmed, waitlisted

    def _rank_key(
        self,
        signup: Signup,
        role: Role,
        event: Event,
        ledger: AttendanceLedger,
        history: AttendanceHistory | None,
    ) -> tuple[int, int, int, int]:
        confirmed, waitlisted = self._stats(signup.member_id, event, history)
        has_credit = signup.request_credit and ledger.balance(signup.member_id) > 0
        return (
            0 if has_credit else 1,
            confirmed,
            -waitlisted,
            self._rotation(signup.member_id, event.event_date, role),
        )

    @staticmethod
    def _rotation(member_id: str, event_date: date, role: Role) -> int:
        payload = f"{member_id}|{event_date.isoformat()}|{role.value}".encode()
        return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")
