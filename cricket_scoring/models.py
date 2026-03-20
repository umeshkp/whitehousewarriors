from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

ExtraType = Literal["none", "wide", "no-ball"]


class ValidationError(Exception):
    """Domain validation error for invalid scoring inputs."""


@dataclass(frozen=True)
class TeamRoster:
    name: str
    players: list[str]


@dataclass(frozen=True)
class MatchSetup:
    match_id: str
    innings_no: int
    batting_team: TeamRoster
    bowling_team: TeamRoster


@dataclass(frozen=True)
class DeliveryInput:
    striker: str
    non_striker: str
    bowler: str
    batter_runs: int
    extra_type: ExtraType
    extra_runs: int
    is_wicket: bool


@dataclass(frozen=True)
class DeliveryRecord:
    match_id: str
    innings_no: int
    over_no: int
    ball_in_over_legal: int
    delivery_seq: int
    batting_team: str
    bowling_team: str
    striker: str
    non_striker: str
    bowler: str
    batter_runs: int
    extra_type: str
    extra_runs: int
    total_runs_on_ball: int
    is_legal_ball: bool
    over_completed: bool
    team_total_runs: int
    team_total_wickets: int
    timestamp_utc: str


@dataclass(frozen=True)
class InningsState:
    match: MatchSetup
    striker: str
    non_striker: str
    current_bowler: str | None = None
    over_no: int = 1
    legal_balls_in_over: int = 0
    delivery_seq: int = 0
    total_runs: int = 0
    total_wickets: int = 0
    batter_runs: dict[str, int] = field(default_factory=dict)
    requires_bowler_selection: bool = True


def _normalize_players(players: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for player in players:
        value = player.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


def create_initial_state(
    batting_team_name: str,
    batting_players: list[str],
    bowling_team_name: str,
    bowling_players: list[str],
    striker: str,
    non_striker: str,
    innings_no: int = 1,
) -> InningsState:
    batting_name = batting_team_name.strip()
    bowling_name = bowling_team_name.strip()
    normalized_batting_players = _normalize_players(batting_players)
    normalized_bowling_players = _normalize_players(bowling_players)
    striker_name = striker.strip()
    non_striker_name = non_striker.strip()

    if not batting_name:
        raise ValidationError("Batting team name cannot be empty.")
    if not bowling_name:
        raise ValidationError("Bowling team name cannot be empty.")
    if not normalized_batting_players:
        raise ValidationError("Batting team roster cannot be empty.")
    if not normalized_bowling_players:
        raise ValidationError("Bowling team roster cannot be empty.")
    if len(normalized_batting_players) < 2:
        raise ValidationError("Batting team roster must contain at least 2 players.")
    if striker_name == non_striker_name:
        raise ValidationError("Striker and non-striker must be different players.")
    if striker_name not in normalized_batting_players or non_striker_name not in normalized_batting_players:
        raise ValidationError("Striker and non-striker must belong to batting team.")

    batting_team = TeamRoster(name=batting_name, players=normalized_batting_players)
    bowling_team = TeamRoster(name=bowling_name, players=normalized_bowling_players)
    match = MatchSetup(match_id=str(uuid4()), innings_no=innings_no, batting_team=batting_team, bowling_team=bowling_team)

    player_runs = {player: 0 for player in batting_team.players}
    return InningsState(match=match, striker=striker_name, non_striker=non_striker_name, batter_runs=player_runs)


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()
