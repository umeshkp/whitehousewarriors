from __future__ import annotations

from dataclasses import replace

from cricket_scoring.models import DeliveryInput, DeliveryRecord, InningsState, ValidationError, utc_now_iso


def _is_legal_ball(extra_type: str) -> bool:
    return extra_type not in {"wide", "no-ball"}


def _validate_delivery(state: InningsState, delivery: DeliveryInput) -> None:
    if delivery.striker == delivery.non_striker:
        raise ValidationError("Striker and non-striker must be different.")
    if delivery.striker not in state.match.batting_team.players or delivery.non_striker not in state.match.batting_team.players:
        raise ValidationError("Striker and non-striker must belong to batting team roster.")
    if delivery.bowler not in state.match.bowling_team.players:
        raise ValidationError("Bowler must belong to bowling team roster.")
    if state.requires_bowler_selection and not delivery.bowler:
        raise ValidationError("Select a bowler before submitting the first ball of the over.")
    if state.current_bowler and delivery.bowler != state.current_bowler and not state.requires_bowler_selection:
        raise ValidationError("Current over bowler cannot change mid-over.")
    if delivery.batter_runs < 0 or delivery.batter_runs > 6:
        raise ValidationError("Batter runs must be between 0 and 6.")
    if delivery.extra_runs < 0:
        raise ValidationError("Extra runs cannot be negative.")
    if delivery.extra_type not in {"none", "wide", "no-ball"}:
        raise ValidationError("Extra type must be one of: none, wide, no-ball.")
    if delivery.extra_type == "none" and delivery.extra_runs != 0:
        raise ValidationError("Extra runs must be zero when extra type is none.")


def apply_delivery(state: InningsState, delivery: DeliveryInput) -> tuple[InningsState, DeliveryRecord]:
    _validate_delivery(state, delivery)

    bowler = delivery.bowler if state.requires_bowler_selection else state.current_bowler or delivery.bowler
    legal_ball = _is_legal_ball(delivery.extra_type)
    new_legal_balls = state.legal_balls_in_over + (1 if legal_ball else 0)
    total_runs_on_ball = delivery.batter_runs + delivery.extra_runs
    new_total_runs = state.total_runs + total_runs_on_ball
    new_total_wickets = state.total_wickets + (1 if delivery.is_wicket else 0)

    striker = delivery.striker
    non_striker = delivery.non_striker

    # Run-parity strike logic applies to batter runs only.
    if delivery.batter_runs % 2 == 1:
        striker, non_striker = non_striker, striker

    over_completed = new_legal_balls == 6
    next_over_no = state.over_no
    next_legal_balls = new_legal_balls
    next_requires_bowler = False
    next_current_bowler = bowler

    if over_completed:
        striker, non_striker = non_striker, striker
        next_over_no = state.over_no + 1
        next_legal_balls = 0
        next_requires_bowler = True
        next_current_bowler = None

    batter_runs = dict(state.batter_runs)
    batter_runs[delivery.striker] = batter_runs.get(delivery.striker, 0) + delivery.batter_runs
    next_delivery_seq = state.delivery_seq + 1

    record = DeliveryRecord(
        match_id=state.match.match_id,
        innings_no=state.match.innings_no,
        over_no=state.over_no,
        ball_in_over_legal=new_legal_balls if legal_ball else state.legal_balls_in_over,
        delivery_seq=next_delivery_seq,
        batting_team=state.match.batting_team.name,
        bowling_team=state.match.bowling_team.name,
        striker=delivery.striker,
        non_striker=delivery.non_striker,
        bowler=bowler,
        batter_runs=delivery.batter_runs,
        extra_type=delivery.extra_type,
        extra_runs=delivery.extra_runs,
        total_runs_on_ball=total_runs_on_ball,
        is_legal_ball=legal_ball,
        over_completed=over_completed,
        team_total_runs=new_total_runs,
        team_total_wickets=new_total_wickets,
        timestamp_utc=utc_now_iso(),
    )

    new_state = replace(
        state,
        striker=striker,
        non_striker=non_striker,
        current_bowler=next_current_bowler,
        over_no=next_over_no,
        legal_balls_in_over=next_legal_balls,
        delivery_seq=next_delivery_seq,
        total_runs=new_total_runs,
        total_wickets=new_total_wickets,
        batter_runs=batter_runs,
        requires_bowler_selection=next_requires_bowler,
    )
    return new_state, record
