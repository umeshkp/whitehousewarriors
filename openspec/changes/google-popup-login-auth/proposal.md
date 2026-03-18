## Why

The current interface does not provide a polished account-selection login experience for Google authentication, and it also lacks a resilient fallback when authentication is skipped or unavailable. We need optional Google sign-in plus local CSV persistence so scoring can continue uninterrupted and remain downloadable at match end.

## What Changes

- Add a popup-style Google login entry point in the UI (similar to “Continue with Google” flows) that lets users pick an existing Google account.
- Make Google authentication optional; users can continue scoring without login.
- Complete OAuth authentication and persist authenticated session state in Streamlit so the app recognizes logged-in users when login is used.
- Fetch authenticated profile information from Google identity data and expose text identity display using user name.
- Persist authenticated login state across browser refresh and UI restarts.
- Allow all Google accounts (no domain restriction) for login.
- If Google auth is not used/available, persist scoring in a local CSV-backed flow that survives browser refresh.
- Provide a match-end action to download the locally maintained CSV file to the user's local downloads folder via browser download behavior.
- Display login state in the UI while allowing scoring in either authenticated (Google-backed) or unauthenticated (local CSV) mode.
- Add robust auth error handling for popup cancellation, OAuth state mismatch, and token exchange failures.

## Capabilities

### New Capabilities
- `google-popup-account-login`: Popup-based Google account selection and OAuth sign-in user flow for the Streamlit interface.
- `authenticated-profile-ingestion`: Retrieval and durable session storage of authenticated Google user profile information.
- `optional-auth-scoring-mode`: UI behaviors that support both authenticated and unauthenticated scoring paths.
- `local-csv-scoring-persistence`: Local CSV persistence and match-end browser download workflow when Google auth/storage is not used.

### Modified Capabilities
- None.

## Impact

- Affected code: Streamlit auth UI components, OAuth flow manager, durable auth session handling, scoring mode selection, and local CSV persistence/download workflow.
- External dependencies/APIs: Google OAuth endpoints and token/userinfo handling via Google auth libraries.
- Data impact: Introduces local CSV storage path for offline/unauthenticated scoring continuity.
- Security impact: Preserves strong identity assurance when Google login is used while enabling non-auth fallback operation.
- User experience impact: Reduces login friction and prevents scoring interruption by allowing immediate local scoring fallback.
