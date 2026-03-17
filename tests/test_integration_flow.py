from cricket_scoring.engine import apply_delivery
from cricket_scoring.models import DeliveryInput, create_initial_state
from cricket_scoring.sheets import InMemorySheetsService


def test_happy_path_with_extras_and_persistence():
    state = create_initial_state(
        batting_team_name="Team-1",
        batting_players=["player-1", "player-2", "player-3"],
        bowling_team_name="Team-2",
        bowling_players=["player-4", "player-5", "player-6"],
        striker="player-1",
        non_striker="player-2",
    )

    sheet_url = "https://docs.google.com/spreadsheets/d/abcDEF123/edit#gid=0"
    sheets = InMemorySheetsService()
    sheets.allow_url(sheet_url)
    sheets.validate_sheet(sheet_url)

    deliveries = [
        DeliveryInput("player-1", "player-2", "player-4", 1, "none", 0, False),
        DeliveryInput("player-2", "player-1", "player-4", 0, "wide", 1, False),
        DeliveryInput("player-2", "player-1", "player-4", 2, "none", 0, False),
        DeliveryInput("player-2", "player-1", "player-4", 1, "no-ball", 1, False),
        DeliveryInput("player-1", "player-2", "player-4", 0, "none", 0, False),
        DeliveryInput("player-1", "player-2", "player-4", 0, "none", 0, False),
        DeliveryInput("player-1", "player-2", "player-4", 0, "none", 0, False),
        DeliveryInput("player-1", "player-2", "player-4", 0, "none", 0, False),
        DeliveryInput("player-1", "player-2", "player-4", 0, "none", 0, False),
    ]

    for delivery in deliveries:
        state, record = apply_delivery(state, delivery)
        sheets.append_delivery(sheet_url, record)

    assert state.total_runs == 6
    assert state.over_no == 2
    assert state.legal_balls_in_over == 0
    assert state.requires_bowler_selection is True
    assert len(sheets.rows_by_url[sheet_url]) == len(deliveries)
