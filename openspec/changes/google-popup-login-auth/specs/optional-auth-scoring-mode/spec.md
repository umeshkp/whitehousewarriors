## ADDED Requirements

### Requirement: Scoring shall be available without Google authentication
The system SHALL allow users to start and continue scoring even when Google login is skipped, cancelled, or unavailable.

#### Scenario: User skips login and continues scoring
- **WHEN** a user chooses not to authenticate with Google
- **THEN** scoring inputs and match progression remain enabled

### Requirement: Dual-mode identity state indicator
The system SHALL display current scoring mode as either authenticated Google mode or unauthenticated local mode.

#### Scenario: Local scoring mode is shown
- **WHEN** the user is not authenticated
- **THEN** the interface shows local scoring mode status and does not block scoring actions

### Requirement: Logout transitions to local scoring mode
The system SHALL transition authenticated sessions to local scoring mode after logout without interrupting scoring capability.

#### Scenario: User logs out mid-session
- **WHEN** an authenticated user triggers logout
- **THEN** the app clears auth state and continues scoring in local mode
