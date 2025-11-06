````markdown
# Copilot / AI Agent Instructions for fastmcp-auth

These instructions help an AI coding agent become productive quickly in this repository. Keep responses actionable and repository-specific.

1. Big picture
   - This project provides a Time MCP server (FastMCP) with OAuth2 PKCE auth and a mock OAuth server for testing. Main servers:
     - `time_mcp_server.py` — OAuth-ready SSE MCP server (port 3000 by default)
     - `simplified_server.py` — lightweight server without OAuth
     - `mock_oauth_server.py` — mock authorization server (port 8000)
   - Data flow: client → OAuth (mock at :8000) → MCP server (:3000) → tools (`get_current_time`, `convert_time`). Tests expect this topology.

2. Key developer workflows (explicit commands)
    - Create venv, install deps, and always activate the project's venv before running scripts:
       - `python -m venv .venv` then
       - `source './.venv/bin/activate'`  # ALWAYS activate using this exact command in this repo
       - `pip install -r requirements.txt`
     - `pip install -r requirements.txt`
   - Run mock OAuth + MCP server for integration: start `mock_oauth_server.py` (terminal 1) and `time_mcp_server.py` (terminal 2).
   - Run unit tests: `python test_server.py` (this script assembles unittest TestCases and reports a coverage-style summary).
   - Run OAuth flow smoke: `python test_oauth_flow.py` (requires mock OAuth running).
   - Test discovery endpoints: `python test_wellknown_endpoints.py` (requires both servers).

3. Project-specific conventions & patterns
   - Async helpers exposed as coroutine functions: `get_current_time(...)` and `convert_time(...)` are async and tests call them with an asyncio loop (see `test_server.py`). When generating or editing, preserve async signatures.
   - Timezones use IANA names (zoneinfo). Use Python 3.9+ and `zoneinfo.ZoneInfo` for tz handling.
   - PKCE flow code (generation & verification) follows standard code_challenge `S256` usage — see `test_oauth_flow.py` and `mock_oauth_server.py` for examples.
   - Long-lived SSE endpoints: ephemeral HTTP clients (curl) may trigger harmless TypeError logs; avoid changing this behavior unless adding better client checks (see README troubleshooting).

4. Tests and stability cues
   - Tests validate both structure and error messages (look for assertions that check exception text like "Invalid timezone" or "Invalid time format"). Keep those exact messages when modifying validation logic.
   - The test suite constructs loops directly (new_event_loop) — when adding tests/mock tasks follow the same pattern.

5. Integration points & external dependencies
   - External ports: mock OAuth (8000) and MCP server (3000). Hardcoded in tests and discovery docs — updating ports requires updating tests and `.env` if present.
   - Postman collection (`postman_collection.json`) and `.well-known` endpoints follow RFCs 8414 / 9728 — maintain response field names used in `test_wellknown_endpoints.py` (e.g. `issuer`, `authorization_endpoint`, `token_endpoint`, `resource`, `authorization_servers`).

6. When changing behavior, do this first
   - Run `python test_server.py` and `python test_wellknown_endpoints.py` locally with the appropriate servers running. Fix tests before proposing PRs.
   - If you change validation messages or API field names, update corresponding tests immediately.

7. Files to inspect for context when implementing a change
   - `time_mcp_server.py` (main behavior & tool implementations)
   - `mock_oauth_server.py` (authorization flows & discovery endpoints)
   - `test_server.py`, `test_oauth_flow.py`, `test_wellknown_endpoints.py` (expected behavior and exact strings)
   - `WELLKNOWN_ENDPOINTS.md`, `README.md` (architectural notes and run instructions)

8. Examples to follow (copyable patterns)
   - PKCE generation: see `test_oauth_flow.py::generate_pkce_pair()` for base64-url encoding and `S256` challenge.
   - Async test invocation: tests call `loop.run_until_complete(get_current_time(...))` — follow this when invoking coroutines in tests.

9. Strict no-change rules for AI edits
   - Do not change test assertions' literal strings (error messages, expected JSON field names) without updating tests.
   - Do not change the default ports (8000/3000) without updating all tests and `.env` references.

10. If you get stuck or need clarification
    - Open a short issue with: minimal repro, failing test name, and server logs (include stack trace). Use `test_wellknown_endpoints.py`/`test_oauth_flow.py` to demonstrate expected endpoints.

Keep instructions concise and update this file when repository conventions or test expectations change.
````
