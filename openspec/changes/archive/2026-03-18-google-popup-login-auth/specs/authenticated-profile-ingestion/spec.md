## ADDED Requirements

### Requirement: Normalize authenticated Google profile fields
The system SHALL extract and normalize authenticated identity fields from Google tokens/userinfo including `sub`, `email`, and `name`.

#### Scenario: Successful profile extraction
- **WHEN** OAuth token exchange succeeds
- **THEN** the system stores normalized profile fields in session and marks user authenticated

### Requirement: Profile availability for downstream UI
The system SHALL make normalized authenticated profile information available to UI components that display signed-in identity state.

#### Scenario: Signed-in identity is displayed
- **WHEN** the user is authenticated
- **THEN** the UI can access profile fields and render account identity details

### Requirement: Signed-in identity display shall be name-only text
The system SHALL display authenticated identity in UI using text-based user `name` only and SHALL not require avatar/profile picture rendering.

#### Scenario: Name-only identity rendering
- **WHEN** the user is authenticated and profile fields are available
- **THEN** the interface renders user name as text and does not depend on `picture` for login-state display

### Requirement: Guard against incomplete identity payloads
The system SHALL fail authentication when required identity fields are missing and SHALL not persist partial auth state.

#### Scenario: Missing required identity field
- **WHEN** Google response does not include required identity keys such as `sub` or `email`
- **THEN** the system rejects login completion and prompts user to retry authentication
