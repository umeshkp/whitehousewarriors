from cricket_scoring.models import DeliveryRecord
from cricket_scoring.sheets import (
    InMemorySheetsService,
    REQUIRED_COLUMNS,
    SheetsServiceError,
    delivery_to_row,
    ensure_header_row,
    extract_sheet_id,
)


class FakeWorksheet:
    def __init__(self, headers):
        self._headers = headers
        self.updated = None

    def row_values(self, index: int):
        assert index == 1
        return self._headers

    def update(self, range_name: str, values):
        self.updated = (range_name, values)
        self._headers = values[0]



def test_extract_sheet_id_from_valid_url():
    url = "https://docs.google.com/spreadsheets/d/abcDEF123/edit#gid=0"
    assert extract_sheet_id(url) == "abcDEF123"



def test_extract_sheet_id_raises_for_invalid_url():
    try:
        extract_sheet_id("https://example.com/not-a-sheet")
        assert False, "expected SheetsServiceError"
    except SheetsServiceError:
        pass



def test_ensure_header_row_updates_when_mismatch():
    worksheet = FakeWorksheet(headers=["wrong"])
    ensure_header_row(worksheet)
    assert worksheet.updated == ("A1", [REQUIRED_COLUMNS])



def test_delivery_to_row_uses_required_column_order():
    record = DeliveryRecord(
        match_id="m1",
        innings_no=1,
        over_no=1,
        ball_in_over_legal=1,
        delivery_seq=1,
        batting_team="Team-1",
        bowling_team="Team-2",
        striker="p1",
        non_striker="p2",
        bowler="p4",
        batter_runs=1,
        extra_type="none",
        extra_runs=0,
        total_runs_on_ball=1,
        is_legal_ball=True,
        over_completed=False,
        team_total_runs=1,
        team_total_wickets=0,
        timestamp_utc="2026-01-01T00:00:00+00:00",
    )

    row = delivery_to_row(record)
    assert len(row) == len(REQUIRED_COLUMNS)
    assert row[0] == "m1"
    assert row[9] == "p4"



def test_in_memory_sheet_service_success_and_failures():
    service = InMemorySheetsService()
    url = "https://docs.google.com/spreadsheets/d/abcDEF123/edit#gid=0"

    try:
        service.validate_sheet(url)
        assert False, "expected failure for URL not allowed"
    except SheetsServiceError:
        pass

    service.allow_url(url)
    service.validate_sheet(url)

    record = DeliveryRecord(
        match_id="m1",
        innings_no=1,
        over_no=1,
        ball_in_over_legal=1,
        delivery_seq=1,
        batting_team="Team-1",
        bowling_team="Team-2",
        striker="p1",
        non_striker="p2",
        bowler="p4",
        batter_runs=1,
        extra_type="none",
        extra_runs=0,
        total_runs_on_ball=1,
        is_legal_ball=True,
        over_completed=False,
        team_total_runs=1,
        team_total_wickets=0,
        timestamp_utc="2026-01-01T00:00:00+00:00",
    )
    service.append_delivery(url, record)
    assert len(service.rows_by_url[url]) == 1
