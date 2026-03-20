## MODIFIED Requirements

### Requirement: Popup-style Google account chooser login entry
The system SHALL present a “Continue with Google” login action that launches Google authentication with account-selection behavior.

#### Scenario: User starts Google popup login
- **WHEN** an unauthenticated user clicks “Continue with Google”
- **THEN** the system initiates OAuth authorization with parameters that require account selection

### Requirement: User-recoverable login failure handling
The system SHALL provide actionable error messages and retry capability for popup cancellation, OAuth exchange failures, and Gmail verification failures.

#### Scenario: Popup flow is cancelled
- **WHEN** the user closes or cancels Google account selection before login completes
- **THEN** the system keeps the user unauthenticated and displays a retry option

### Requirement: Google login shall be optional
The system SHALL provide a “continue without login” path that skips Google authentication without blocking scoring workflow.

#### Scenario: User continues without authentication
- **WHEN** a user selects continue without login
- **THEN** the app proceeds in unauthenticated local scoring mode

## REMOVED Requirements

### Requirement: OAuth callback completion with state validation
**Reason**: Authentication acceptance now uses Gmail-account verification requirements rather than OAuth callback state-validation requirements.
**Migration**: Replace callback state-mismatch behavioral tests with Gmail acceptance/rejection tests and ensure login failures keep local scoring mode available.

### Requirement: Login shall allow all Google accounts
**Reason**: Authenticated mode now requires Gmail-domain verification and no longer accepts every valid Google account.
**Migration**: Update auth-completion checks to require `@gmail.com` and show Gmail-required guidance for non-Gmail accounts.
