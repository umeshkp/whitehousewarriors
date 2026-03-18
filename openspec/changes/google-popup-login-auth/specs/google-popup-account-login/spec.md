## ADDED Requirements

### Requirement: Popup-style Google account chooser login entry
The system SHALL present a “Continue with Google” login action that launches Google authentication with account-selection behavior.

#### Scenario: User starts Google popup login
- **WHEN** an unauthenticated user clicks “Continue with Google”
- **THEN** the system initiates OAuth authorization with parameters that require account selection

### Requirement: OAuth callback completion with state validation
The system SHALL validate OAuth state and complete token exchange only when callback state matches the stored login state nonce.

#### Scenario: State mismatch is rejected
- **WHEN** OAuth callback returns with a state value different from the stored login state
- **THEN** the system rejects the callback, does not authenticate the session, and shows an auth error

### Requirement: User-recoverable login failure handling
The system SHALL provide actionable error messages and retry capability for popup cancellation and OAuth exchange failures.

#### Scenario: Popup flow is cancelled
- **WHEN** the user closes or cancels Google account selection before login completes
- **THEN** the system keeps the user unauthenticated and displays a retry option

### Requirement: Google login shall be optional
The system SHALL provide a “continue without login” path that skips Google authentication without blocking scoring workflow.

#### Scenario: User continues without authentication
- **WHEN** a user selects continue without login
- **THEN** the app proceeds in unauthenticated local scoring mode

### Requirement: Login shall allow all Google accounts
The system SHALL permit authentication for any valid Google account and SHALL not enforce email-domain restrictions.

#### Scenario: Consumer Google account login is accepted
- **WHEN** a user authenticates with a non-Workspace Google account
- **THEN** the system completes authentication and treats the account as valid
