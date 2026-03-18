# team-roster-and-role-selection Specification

## Purpose
TBD - created by archiving change streamlit-cricket-scoring-ui. Update Purpose after archive.
## Requirements
### Requirement: Two-team roster setup
The system SHALL require match setup with exactly two teams, and each team SHALL have a user-maintained player list before score entry is enabled.

#### Scenario: Team rosters are configured
- **WHEN** the user enters Team 1 and Team 2 details with player names for both teams
- **THEN** the system saves both rosters and enables player-role selection for scoring

### Requirement: Batters must be selected from batting team roster
The system SHALL allow striker and non-striker selection only from the batting team's player list.

#### Scenario: Batter selection excludes bowling roster players
- **WHEN** Team 1 is batting and the scorer opens striker/non-striker selectors
- **THEN** the selectable players include only Team 1 roster members

### Requirement: Bowler must be selected from bowling team roster
The system SHALL allow bowler selection only from the bowling team's player list.

#### Scenario: Bowler selection excludes batting roster players
- **WHEN** Team 2 is bowling and the scorer opens bowler selector
- **THEN** the selectable players include only Team 2 roster members

### Requirement: Over start requires bowler selection
The system SHALL require an active bowler selection at the start of each over before any delivery in that over can be submitted.

#### Scenario: New over blocks delivery until bowler selected
- **WHEN** a new over is opened after six legal balls and no bowler is selected for that over
- **THEN** the system disables delivery submission and prompts the scorer to pick a bowler from the bowling team roster

### Requirement: Delivery submission requires valid role-team mapping
The system SHALL reject delivery submission if the selected striker/non-striker or bowler is not valid for the current batting/bowling team assignment.

#### Scenario: Invalid role assignment is blocked
- **WHEN** a scorer attempts to submit a delivery where bowler belongs to batting team
- **THEN** the system blocks submission and shows a validation error

