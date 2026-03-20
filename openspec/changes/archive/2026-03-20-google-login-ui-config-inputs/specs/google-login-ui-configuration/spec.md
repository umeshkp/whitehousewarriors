## ADDED Requirements

### Requirement: UI SHALL collect Google OAuth configuration inputs
The system SHALL provide an in-app login configuration section where users can enter OAuth client configuration JSON and redirect URI needed for Google sign-in.

#### Scenario: User provides OAuth inputs in login panel
- **WHEN** Google OAuth settings are not available from environment/runtime state
- **THEN** the login panel shows input controls for OAuth client config JSON and redirect URI

### Requirement: OAuth input validation SHALL run before enabling Google sign-in
The system SHALL validate OAuth input structure and redirect URI format before exposing an actionable Google login entry.

#### Scenario: Invalid OAuth JSON is rejected
- **WHEN** a user saves malformed OAuth JSON or JSON missing `web`/`installed` objects
- **THEN** the system rejects the save, keeps Google sign-in disabled, and shows a corrective validation message

### Requirement: Valid OAuth inputs SHALL enable popup Google login in-session
The system SHALL use validated UI-provided OAuth values for authorization URL creation in the current app session.

#### Scenario: Valid runtime OAuth config enables login button
- **WHEN** a user saves valid OAuth JSON and redirect URI
- **THEN** the system enables the "Continue with Google" login action without requiring app restart
