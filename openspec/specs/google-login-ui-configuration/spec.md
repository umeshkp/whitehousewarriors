# google-login-ui-configuration Specification

## Purpose
TBD - created by archiving change google-login-ui-config-inputs. Update Purpose after archive.
## Requirements
### Requirement: UI SHALL collect Google sign-in configuration inputs
The system SHALL provide an in-app login configuration section where users can enter Google client configuration JSON and redirect URI needed for Google sign-in.

#### Scenario: User provides sign-in inputs in login panel
- **WHEN** Google sign-in settings are not available from environment/runtime state
- **THEN** the login panel shows input controls for Google client config JSON and redirect URI

### Requirement: Sign-in input validation SHALL run before enabling Google login
The system SHALL validate Google sign-in input structure and redirect URI format before exposing an actionable Google login entry.

#### Scenario: Invalid Google client JSON is rejected
- **WHEN** a user saves malformed Google client JSON or JSON missing `web`/`installed` objects
- **THEN** the system rejects the save, keeps Google sign-in disabled, and shows a corrective validation message

### Requirement: Valid sign-in inputs SHALL enable popup Google login in-session
The system SHALL use validated UI-provided Google sign-in values for authorization URL creation in the current app session.

#### Scenario: Valid runtime sign-in config enables login button
- **WHEN** a user saves valid Google client JSON and redirect URI
- **THEN** the system enables the "Continue with Google" login action without requiring app restart
