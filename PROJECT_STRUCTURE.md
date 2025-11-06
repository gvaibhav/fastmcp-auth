# Project Structure

## Core Files

### Server Files
- `time_mcp_server.py` - Main OAuth-ready MCP server (SSE mode)
- `simplified_server.py` - Simple MCP server without OAuth (for testing)
- `mock_oauth_server.py` - OAuth2 PKCE mock server for testing

### Test Files
- `test_server.py` - Unit tests for MCP tools (24 tests)
- `test_oauth_flow.py` - OAuth2 PKCE flow tests
- `test_integration.py` - Integration tests

### Configuration
- `.env` - OAuth configuration settings
- `.gitignore` - Git ignore rules
- `requirements.txt` - Python dependencies

### Quick Start Scripts
- `run_server.ps1` - Quick start for simplified server
- `run_sse_server.ps1` - Quick start for SSE server

### Documentation
- `README.md` - Complete project documentation

## Quick Commands

```powershell
# Setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run simple server (no auth)
python simplified_server.py

# Run OAuth server (2 terminals needed)
python mock_oauth_server.py    # Terminal 1
python time_mcp_server.py       # Terminal 2

# Run tests
python test_server.py           # Unit tests
python test_oauth_flow.py       # OAuth tests
python test_integration.py      # Integration tests
```

## File Count
- **Core servers**: 3
- **Test files**: 3
- **Config files**: 3
- **Scripts**: 2
- **Documentation**: 1

**Total**: 12 files (clean and organized)
