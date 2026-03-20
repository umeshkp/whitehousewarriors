# gmail-account-verification Specification

## Purpose
Define Gmail-domain acceptance rules for authenticated mode and local-mode fallback on non-Gmail login attempts.
## Requirements
### Requirement: Gmail account is required for authenticated mode
The system SHALL complete authenticated-mode login only when the normalized authenticated identity email ends with `@gmail.com`.

#### Scenario: Gmail account is accepted
- **WHEN** login returns an authenticated profile with email `player@gmail.com`
- **THEN** the system marks the session as authenticated Google mode

### Requirement: Non-Gmail account is rejected for authenticated mode
The system SHALL reject authenticated-mode login when the authenticated identity email does not end with `@gmail.com`.

#### Scenario: Workspace account is rejected
- **WHEN** login returns an authenticated profile with email `player@company.com`
- **THEN** the system does not enter authenticated Google mode and shows a Gmail-required error

### Requirement: Gmail verification failures preserve scoring continuity
The system SHALL keep scoring available in local mode when Gmail verification fails.

#### Scenario: Verification failure falls back to local mode
- **WHEN** login completes but Gmail verification fails
- **THEN** the system keeps or switches to local scoring mode with scoring actions enabled
