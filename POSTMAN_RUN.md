## Running the Time MCP Postman collection

This file shows how to run the runnable Postman collection included in this repo.

Important:
- Mock OAuth server runs on http://localhost:8000
- MCP server runs on http://localhost:3000
- Activate the repository virtualenv before starting Python servers using the exact command below:

```bash
source './.venv/bin/activate'
```

## Start the servers (two terminals)

Terminal 1 (mock OAuth server):

```bash
# activate venv (only if not already active)
source './.venv/bin/activate'
python mock_oauth_server.py
```

Terminal 2 (MCP server):

```bash
source './.venv/bin/activate'
python time_mcp_server.py
```

Both servers must be running for the collection to succeed.

## Reset mock OAuth server state (optional but recommended before automated runs)

The mock OAuth server exposes a small admin endpoint that clears in-memory state used for authorization codes and tokens. Run this before a fresh collection run:

```bash
curl -X POST http://localhost:8000/__admin/reset
```

Expect a small JSON response confirming the reset.

## Postman (GUI) - quick steps

1. Open Postman.
2. Import `postman_collection.json` from the repository root.
3. (Optional) Import `reports/newman-env.json` as an Environment, or create an environment with the following variables: `client_id`, `redirect_uri`, `scope`, `code_verifier`, `code_challenge`, `authorization_code`, `access_token`, `refresh_token`.
4. Ensure `client_id`, `redirect_uri` and `scope` match the values the mock OAuth server expects (the repository tests use defaults; `reports/newman-env.json` is a good starting point).
5. Run the collection (Runner). The collection includes tests that assert discovery endpoints, the authorize→token flow, and protected `/tools/*` requests.

## Newman (CLI) - macOS zsh commands

The repository includes a runnable collection at `postman_collection.json` (updated to the fixed runnable version) and an environment file at `reports/newman-env.json` created during prior runs. To run via newman (no global install required) use npx:

```bash
# reset server state first (recommended)
curl -X POST http://localhost:8000/__admin/reset

# run collection with npx/newman
npx -y newman run postman_collection.json -e reports/newman-env.json \
  --env-var 'authorization_code=' --env-var 'access_token=' --env-var 'refresh_token=' \
  --reporters cli,json --reporter-json-export reports/newman-report.json
```

Notes:
- The extra `--env-var` flags clear pre-populated authorization_code / access_token / refresh_token values so the authorize→token exchange runs during the collection.
- The run outputs a CLI summary and creates `reports/newman-report.json` (JSON reporter). You can add other reporters as needed.

## Troubleshooting

- If the collection fails at the Authorize step, check the mock OAuth server logs and that `/oauth/authorize` is reachable. Use the `curl` reset and restart servers.
- If token exchange returns 400, ensure `authorization_code` is blank (single-use codes) and that `code_verifier`/`code_challenge` are set in the environment. `reports/newman-env.json` contains a working example.
- If `/tools/*` endpoints return 401, ensure the MCP server is running the updated code that calls the introspection endpoint and that the access token in the environment is freshly generated.

## Files of interest

- `postman_collection.json` — runnable collection (authorized and form-encoded token exchange).
- `reports/collection-run.json` — original runnable collection preserved under `reports` (identical to the committed root collection).
- `reports/newman-env.json` — example environment with PKCE values and tokens (useful as a template).
- `reports/newman-report.json` — JSON output produced by the example newman command above.

## Next steps (optional)

- Install a newman HTML reporter (npm package) if you want an HTML report: `npm i -g newman-reporter-html` and add `--reporters html` / `--reporter-html-export reports/newman-report.html` to the newman command.
- Add a CI GitHub Actions workflow to run the collection automatically. Ensure the action starts both Python servers or uses containers that run them.


