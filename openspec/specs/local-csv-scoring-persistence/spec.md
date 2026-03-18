# local-csv-scoring-persistence Specification

## Purpose
TBD - created by archiving change google-popup-login-auth. Update Purpose after archive.
## Requirements
### Requirement: Local CSV persistence when auth is unavailable
The system SHALL persist scoring records to a local CSV-backed store when Google authentication/storage is not used.

#### Scenario: Local CSV write on delivery submission
- **WHEN** the app is in unauthenticated local mode and a delivery is submitted
- **THEN** the system appends scoring data to a local CSV record set

### Requirement: Local scoring data survives browser refresh
The system SHALL restore local-mode scoring data after browser refresh and UI restart for the same ongoing match context.

#### Scenario: Refresh restores local scoring state
- **WHEN** the user refreshes the browser during local-mode scoring
- **THEN** prior local CSV-backed scoring state is reloaded and visible

### Requirement: Match-end CSV download action
The system SHALL provide a button at match end to download the local CSV scoring file through browser download behavior.

#### Scenario: User downloads local scoring CSV
- **WHEN** local-mode scoring session reaches match end and user clicks download
- **THEN** the browser downloads the generated CSV file to local storage

