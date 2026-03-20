## MODIFIED Requirements

### Requirement: Dual-mode identity state indicator
The system SHALL display current scoring mode as either authenticated Google mode or unauthenticated local mode, and SHALL distinguish between "Google not configured" and "Google login failed" states while keeping local mode available.

#### Scenario: Local mode shown when Google is not configured
- **WHEN** OAuth settings are unavailable or invalid
- **THEN** the interface shows local scoring mode status with guidance to configure Google login and does not block scoring actions

#### Scenario: Local mode shown after login failure
- **WHEN** OAuth callback/token exchange fails
- **THEN** the interface remains in local scoring mode and surfaces a recoverable retry message for Google login
