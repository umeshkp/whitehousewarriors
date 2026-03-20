from cricket_scoring.engine import apply_delivery
from cricket_scoring.models import DeliveryInput, ValidationError, create_initial_state


def _state():
    return create_initial_state(
        batting_team_name="Team-1",
        batting_players=["player-1", "player-2", "player-3"],
        bowling_team_name="Team-2",
        bowling_players=["player-4", "player-5", "player-6"],
        striker="player-1",
        non_striker="player-2",
    )


def test_wide_counts_as_extra_not_legal_ball():
    state = _state()
    next_state, record = apply_delivery(
        state,
        DeliveryInput(
            striker="player-1",
            non_striker="player-2",
            bowler="player-4",
            batter_runs=0,
            extra_type="wide",
            extra_runs=1,
            is_wicket=False,
        ),
    )

    assert record.team_total_runs == 1
    assert record.batter_runs == 0
    assert record.is_legal_ball is False
    assert next_state.legal_balls_in_over == 0


def test_no_ball_with_batter_run_adds_two_without_consuming_ball():
    state = _state()
    next_state, record = apply_delivery(
        state,
        DeliveryInput(
            striker="player-1",
            non_striker="player-2",
            bowler="player-4",
            batter_runs=1,
            extra_type="no-ball",
            extra_runs=1,
            is_wicket=False,
        ),
    )

    assert record.team_total_runs == 2
    assert record.is_legal_ball is False
    assert next_state.legal_balls_in_over == 0


def test_odd_batter_runs_swaps_strike():
    state = _state()
    next_state, _ = apply_delivery(
        state,
        DeliveryInput(
            striker="player-1",
            non_striker="player-2",
            bowler="player-4",
            batter_runs=1,
            extra_type="none",
            extra_runs=0,
            is_wicket=False,
        ),
    )

    assert next_state.striker == "player-2"
    assert next_state.non_striker == "player-1"


def test_even_batter_runs_keeps_strike():
    state = _state()
    next_state, _ = apply_delivery(
        state,
        DeliveryInput(
            striker="player-1",
            non_striker="player-2",
            bowler="player-4",
            batter_runs=2,
            extra_type="none",
            extra_runs=0,
            is_wicket=False,
        ),
    )

    assert next_state.striker == "player-1"
    assert next_state.non_striker == "player-2"


def test_over_rollover_after_six_legal_balls_requires_new_bowler():
    state = _state()
    for _ in range(6):
        state, _ = apply_delivery(
            state,
            DeliveryInput(
                striker=state.striker,
                non_striker=state.non_striker,
                bowler="player-4",
                batter_runs=0,
                extra_type="none",
                extra_runs=0,
                is_wicket=False,
            ),
        )

    assert state.over_no == 2
    assert state.legal_balls_in_over == 0
    assert state.current_bowler is None
    assert state.requires_bowler_selection is True


def test_reject_bowler_not_in_bowling_roster():
    state = _state()
    try:
        apply_delivery(
            state,
            DeliveryInput(
                striker="player-1",
                non_striker="player-2",
                bowler="player-1",
                batter_runs=0,
                extra_type="none",
                extra_runs=0,
                is_wicket=False,
            ),
        )
        assert False, "expected ValidationError"
    except ValidationError as exc:
        assert "Bowler must belong" in str(exc)


def test_reject_mid_over_bowler_change():
    state = _state()
    state, _ = apply_delivery(
        state,
        DeliveryInput(
            striker="player-1",
            non_striker="player-2",
            bowler="player-4",
            batter_runs=0,
            extra_type="none",
            extra_runs=0,
            is_wicket=False,
        ),
    )

    try:
        apply_delivery(
            state,
            DeliveryInput(
                striker=state.striker,
                non_striker=state.non_striker,
                bowler="player-5",
                batter_runs=0,
                extra_type="none",
                extra_runs=0,
                is_wicket=False,
            ),
        )
        assert False, "expected ValidationError"
    except ValidationError as exc:
        assert "cannot change mid-over" in str(exc)


def test_new_over_without_bowler_is_blocked():
    state = _state()
    for _ in range(6):
        state, _ = apply_delivery(
            state,
            DeliveryInput(
                striker=state.striker,
                non_striker=state.non_striker,
                bowler="player-4",
                batter_runs=0,
                extra_type="none",
                extra_runs=0,
                is_wicket=False,
            ),
        )

    try:
        apply_delivery(
            state,
            DeliveryInput(
                striker=state.striker,
                non_striker=state.non_striker,
                bowler="",
                batter_runs=0,
                extra_type="none",
                extra_runs=0,
                is_wicket=False,
            ),
        )
        assert False, "expected ValidationError"
    except ValidationError as exc:
        assert "Bowler must belong" in str(exc) or "Select a bowler" in str(exc)


def test_create_initial_state_requires_two_batting_players():
    try:
        create_initial_state(
            batting_team_name="Team-1",
            batting_players=["player-1"],
            bowling_team_name="Team-2",
            bowling_players=["player-4", "player-5"],
            striker="player-1",
            non_striker="player-2",
        )
        assert False, "expected ValidationError"
    except ValidationError as exc:
        assert "at least 2 players" in str(exc)


def test_create_initial_state_normalizes_player_input():
    state = create_initial_state(
        batting_team_name=" Team-1 ",
        batting_players=[" player-1 ", "player-2", "player-2", "  "],
        bowling_team_name=" Team-2 ",
        bowling_players=[" player-4 ", "player-4", "player-5"],
        striker=" player-1 ",
        non_striker="player-2",
    )

    assert state.match.batting_team.name == "Team-1"
    assert state.match.batting_team.players == ["player-1", "player-2"]
    assert state.match.bowling_team.players == ["player-4", "player-5"]
    assert state.striker == "player-1"
    assert state.non_striker == "player-2"
