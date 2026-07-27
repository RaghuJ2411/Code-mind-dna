# Phase 3 execution architecture

## What changed
- Added a provider abstraction under backend/app/services/execution to isolate code execution from the FastAPI app process.
- Added run and submit APIs for student users.
- Added submission persistence, coding sessions, and coding-event foundation tables.
- Wired the student coding arena and problem bank to run, submit, and display submission history.

## Supported languages
- python
- javascript
- java

## Environment variables
- CODE_EXECUTION_PROVIDER=local
- CODE_EXECUTION_BASE_URL=
- CODE_EXECUTION_API_KEY=
- CODE_EXECUTION_TIMEOUT_SECONDS=10

## Security notes
- Untrusted student code should only run in an isolated execution environment.
- The current local provider is a development-safe placeholder and should be replaced with a hosted sandbox for production use.
