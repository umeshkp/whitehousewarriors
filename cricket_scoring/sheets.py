from __future__ import annotations

import re
from dataclasses import asdict
from typing import Any, Protocol

from cricket_scoring.models import DeliveryRecord, ValidationError

REQUIRED_COLUMNS = [
    "match_id",
    "innings_no",
    "over_no",
    "ball_in_over_legal",
    "delivery_seq",
    "batting_team",
    "bowling_team",
    "striker",
    "non_striker",
    "bowler",
    "batter_runs",
    "extra_type",
    "extra_runs",
    "total_runs_on_ball",
    "is_legal_ball",
    "over_completed",
    "team_total_runs",
    "team_total_wickets",
    "timestamp_utc",
]

SHEET_ID_RE = re.compile(r"/spreadsheets/d/([a-zA-Z0-9-_]+)")


class WorksheetLike(Protocol):
    def row_values(self, index: int) -> list[str]: ...

    def update(self, range_name: str, values: list[list[str]]) -> None: ...

    def append_row(self, values: list[object], value_input_option: str = "RAW") -> None: ...


class SheetsServiceError(Exception):
    """Raised for google sheet validation and write issues."""


def extract_sheet_id(url: str) -> str:
    match = SHEET_ID_RE.search(url)
    if not match:
        raise SheetsServiceError("Invalid Google Sheet URL.")
    return match.group(1)


def ensure_header_row(worksheet: WorksheetLike) -> None:
    current = worksheet.row_values(1)
    if current != REQUIRED_COLUMNS:
        worksheet.update("A1", [REQUIRED_COLUMNS])


def delivery_to_row(record: DeliveryRecord) -> list[object]:
    data = asdict(record)
    return [data[key] for key in REQUIRED_COLUMNS]


class GSpreadSheetsService:
    def __init__(self, credentials: Any):
        try:
            import gspread
        except ImportError as exc:  # pragma: no cover - dependency boundary
            raise SheetsServiceError("gspread is not installed. Add dependencies from requirements.txt.") from exc
        self._client = gspread.authorize(credentials)

    def _get_worksheet(self, sheet_url: str):
        extract_sheet_id(sheet_url)
        spreadsheet = self._client.open_by_url(sheet_url)
        return spreadsheet.sheet1

    def validate_sheet(self, sheet_url: str) -> None:
        try:
            worksheet = self._get_worksheet(sheet_url)
            ensure_header_row(worksheet)
        except Exception as exc:  # pragma: no cover - integration boundary
            raise SheetsServiceError(f"Unable to access Google Sheet: {exc}") from exc

    def append_delivery(self, sheet_url: str, record: DeliveryRecord) -> None:
        try:
            worksheet = self._get_worksheet(sheet_url)
            ensure_header_row(worksheet)
            worksheet.append_row(delivery_to_row(record), value_input_option="RAW")
        except Exception as exc:  # pragma: no cover - integration boundary
            raise SheetsServiceError(f"Failed to append delivery to Google Sheet: {exc}") from exc


class InMemorySheetsService:
    """Test double used by unit/integration tests."""

    def __init__(self):
        self.valid_urls: set[str] = set()
        self.headers_by_url: dict[str, list[str]] = {}
        self.rows_by_url: dict[str, list[list[object]]] = {}

    def allow_url(self, url: str) -> None:
        self.valid_urls.add(url)

    def validate_sheet(self, sheet_url: str) -> None:
        if sheet_url not in self.valid_urls:
            raise SheetsServiceError("Unable to access Google Sheet: URL not allowed in test double")
        self.headers_by_url[sheet_url] = list(REQUIRED_COLUMNS)
        self.rows_by_url.setdefault(sheet_url, [])

    def append_delivery(self, sheet_url: str, record: DeliveryRecord) -> None:
        if sheet_url not in self.valid_urls:
            raise SheetsServiceError("Failed to append delivery to Google Sheet: URL not allowed in test double")
        if self.headers_by_url.get(sheet_url) != REQUIRED_COLUMNS:
            raise ValidationError("Missing required headers for persistence.")
        self.rows_by_url[sheet_url].append(delivery_to_row(record))
