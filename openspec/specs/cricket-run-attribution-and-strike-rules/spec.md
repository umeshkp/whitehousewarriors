# cricket-run-attribution-and-strike-rules Specification

## Purpose
TBD - created by archiving change streamlit-cricket-scoring-ui. Update Purpose after archive.
## Requirements
### Requirement: Extras shall not be attributed to batter runs
The system SHALL attribute batter runs only from the batter-run input field and SHALL keep extra runs as a separate tally component.

#### Scenario: Wide adds extras without batter runs
- **WHEN** a delivery is marked as `wide` with one extra run and zero batter runs
- **THEN** the total score increases by one and the striker's batter-run tally does not increase

### Requirement: Legal ball counting with wide and no-ball handling
The system SHALL increment legal ball count only for legal deliveries and SHALL not increment legal ball count for deliveries marked as `wide` or `no-ball`.

#### Scenario: No-ball does not consume legal ball
- **WHEN** a delivery is recorded as `no-ball` with one batter run
- **THEN** the score increases by two, the legal ball count remains unchanged, and the over number is not advanced

### Requirement: Strike rotation based on batter runs parity
The system SHALL retain strike for even batter runs and swap strike for odd batter runs after each delivery event.

#### Scenario: Odd batter runs swap strike
- **WHEN** the striker scores one batter run on a delivery
- **THEN** the striker and non-striker are swapped for the next delivery

### Requirement: End-of-over strike swap after six legal balls
The system SHALL complete an over after six legal deliveries and SHALL swap strike at over end in addition to per-ball run parity outcomes.

#### Scenario: Over completion swaps strike
- **WHEN** the sixth legal delivery of an over is recorded
- **THEN** the over counter advances and strike is swapped for the start of the next over

### Requirement: New over shall be opened automatically after six legal balls
The system SHALL automatically create the next over state immediately after six legal balls and SHALL carry forward innings totals while resetting legal ball count for the new over.

#### Scenario: Over state resets for next over
- **WHEN** the innings receives the sixth legal ball of over N
- **THEN** over N+1 is opened with legal ball count set to zero and previous totals preserved

