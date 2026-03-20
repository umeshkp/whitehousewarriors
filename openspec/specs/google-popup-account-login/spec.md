# google-popup-account-login Specification

## Purpose
TBD - created by archiving change google-popup-login-auth. Update Purpose after archive.
## Requirements
### Requirement: Popup-style Google account chooser login entry
The system SHALL present a "Continue with Google" login action that launches Google authentication with account-selection behavior, and SHALL expose required Google sign-in configuration inputs when Google login is not yet configured.

#### Scenario: User starts Google popup login after configuration
- **WHEN** an unauthenticated user provides valid Google sign-in settings and clicks "Continue with Google"
- **THEN** the system initiates Google account authorization with parameters that require account selection

#### Scenario: User needs a different Google account
- **WHEN** the Google account chooser popup is shown
- **THEN** the user can choose an existing account or continue with Google's "Use another account" flow

#### Scenario: Google login prerequisites are missing
- **WHEN** Google sign-in settings are not configured
- **THEN** the system shows configuration inputs and does not present an actionable Google login URL until settings are valid

### Requirement: User-recoverable login failure handling
The system SHALL provide actionable error messages and retry capability for popup cancellation, Google sign-in exchange failures, and invalid Google sign-in configuration input.

#### Scenario: Popup flow is cancelled
- **WHEN** the user closes or cancels Google account selection before login completes
- **THEN** the system keeps the user unauthenticated and displays a retry option

#### Scenario: Google sign-in configuration input is invalid
- **WHEN** a user enters invalid Google client JSON or redirect URI
- **THEN** the system surfaces a validation error and guidance to correct the input before retrying login

### Requirement: Google login shall be optional
The system SHALL provide a “continue without login” path that skips Google authentication without blocking scoring workflow.

#### Scenario: User continues without authentication
- **WHEN** a user selects continue without login
- **THEN** the app proceeds in unauthenticated local scoring mode

### Requirement: Google credentials SHALL be entered on Google-hosted pages only
The system SHALL delegate Google credential entry (email/password) to Google's hosted authentication pages and SHALL not collect Google passwords in the app UI.

#### Scenario: Login button is clicked
- **WHEN** the user clicks "Continue with Google"
- **THEN** the app redirects to Google-hosted sign-in screens for account and password entry
