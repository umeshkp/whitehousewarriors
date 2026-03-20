## MODIFIED Requirements

### Requirement: Popup-style Google account chooser login entry
The system SHALL present a "Continue with Google" login action that launches Google authentication with account-selection behavior, and SHALL expose required OAuth configuration inputs when Google login is not yet configured.

#### Scenario: User starts Google popup login after configuration
- **WHEN** an unauthenticated user provides valid OAuth settings and clicks "Continue with Google"
- **THEN** the system initiates OAuth authorization with parameters that require account selection

#### Scenario: User needs a different Google account
- **WHEN** the Google account chooser popup is shown
- **THEN** the user can choose an existing account or continue with Google's "Use another account" flow

#### Scenario: Google login prerequisites are missing
- **WHEN** OAuth settings are not configured
- **THEN** the system shows configuration inputs and does not present an actionable Google login URL until settings are valid

### Requirement: User-recoverable login failure handling
The system SHALL provide actionable error messages and retry capability for popup cancellation, OAuth exchange failures, and invalid OAuth configuration input.

#### Scenario: Popup flow is cancelled
- **WHEN** the user closes or cancels Google account selection before login completes
- **THEN** the system keeps the user unauthenticated and displays a retry option

#### Scenario: OAuth configuration input is invalid
- **WHEN** a user enters invalid OAuth client JSON or redirect URI
- **THEN** the system surfaces a validation error and guidance to correct the input before retrying login

## ADDED Requirements

### Requirement: Google credentials SHALL be entered on Google-hosted pages only
The system SHALL delegate Google credential entry (email/password) to Google's hosted authentication pages and SHALL not collect Google passwords in the app UI.

#### Scenario: Login button is clicked
- **WHEN** the user clicks "Continue with Google"
- **THEN** the app redirects to Google-hosted sign-in screens for account and password entry
