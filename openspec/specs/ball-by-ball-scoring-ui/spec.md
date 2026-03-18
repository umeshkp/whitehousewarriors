# ball-by-ball-scoring-ui Specification

## Purpose
TBD - created by archiving change streamlit-cricket-scoring-ui. Update Purpose after archive.
## Requirements
### Requirement: Delivery entry form for over-wise scoring
The system SHALL provide a Streamlit delivery entry form that captures over progression inputs including bowler, striker, non-striker, batter runs, extra type, extra runs, and wicket indicator for each ball event.

#### Scenario: Scorer enters a standard legal delivery
- **WHEN** the scorer submits a delivery with no extra type and batter runs between 0 and 6
- **THEN** the system records one delivery event and updates the over-wise score display

### Requirement: Live score and over display
The system SHALL display the current over, legal ball number in the over, total score, and current striker/non-striker after each submitted delivery.

#### Scenario: UI refreshes score after each submission
- **WHEN** a delivery is saved successfully
- **THEN** the system updates the live scoreboard in the same session without requiring a manual page reload

### Requirement: Input validation for scoring actions
The system SHALL validate delivery inputs and reject invalid combinations before state mutation.

#### Scenario: Invalid extra selection is rejected
- **WHEN** the scorer submits both `wide` and `no-ball` for a single delivery
- **THEN** the system blocks submission and shows a validation error

