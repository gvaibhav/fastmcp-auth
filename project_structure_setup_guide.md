# Time MCP Server - Complete Project

## Project Structure

```
time-mcp-server/
├── server.py                 # Main FastMCP server (already provided)
├── test_server.py           # Comprehensive test suite (already provided)
├── requirements.txt         # Python dependencies
├── .env.example            # Example environment variables
├── .gitignore              # Git ignore file
├── README.md               # Main documentation
├── TESTING.md              # Testing guide
├── DEPLOYMENT.md           # Deployment guide
└── run_tests.sh            # Test runner script
```

## File: requirements.txt

```txt
# FastMCP core
fastmcp>=0.5.0

# Time handling (built-in to Python 3.9+)
# zoneinfo is part of standard library

# Development dependencies
coverage>=7.0.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
python-dotenv>=1.0.0

# Optional: for better development experience
black>=23.0.0
flake8>=6.0.0
mypy>=1.5.0
```

## File: .env.example

```bash
# OAuth2 Configuration
OAUTH_CLIENT_ID=time-mcp-client
OAUTH_AUTH_URL=http://localhost:8000/oauth/authorize
OAUTH_TOKEN_URL=http://localhost:8000/oauth/token
OAUTH_SCOPES=time:read,time:convert

# Server Configuration
MCP_SERVER_PORT=3000
MCP_SERVER_HOST=0.0.0.0

# Logging
LOG_LEVEL=INFO
```

## File: .gitignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.coverage
htmlcov/
.pytest_cache/
.tox/

# Environment
.env
.env.local

# OS
.DS_Store
Thumbs.db
```

## File: README.md

```markdown
# Time MCP Server with OAuth2 PKCE

A production-ready Model Context Protocol (MCP) server that provides time-related tools using FastMCP with OAuth2 PKCE authentication.

## Features

- ⏰ **Get Current Time**: Retrieve current time in any IANA timezone
- 🌍 **Time Conversion**: Convert times between different timezones
- 🔒 **OAuth2 PKCE Authentication**: Secure authentication without client secrets
- 📡 **Multiple Transports**: Supports both SSE and HTTP protocols
- ✅ **Fully Tested**: Comprehensive test suite with >80% coverage

## Quick Start

### Installation

1. Clone or download this project
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

### Running the Server

```bash
python server.py
```

The server will start and display connection information.

### Running Tests

```bash
python test_server.py
```

For coverage report:
```bash
coverage run test_server.py
coverage report
coverage html  # Generate HTML report in htmlcov/
```

## Tools

### 1. get_current_time

Get the current time in a specified timezone.

**Parameters:**
- `timezone_name` (optional): IANA timezone name (default: "UTC")

**Example:**
```json
{
  "tool": "get_current_time",
  "arguments": {
    "timezone_name": "America/New_York"
  }
}
```

**Response:**
```json
"2025-11-05T09:30:00-05:00"
```

### 2. convert_time

Convert a time from one timezone to another.

**Parameters:**
- `time_str`: ISO 8601 time string
- `from_timezone`: Source IANA timezone
- `to_timezone`: Target IANA timezone

**Example:**
```json
{
  "tool": "convert_time",
  "arguments": {
    "time_str": "2025-11-05T14:30:00",
    "from_timezone": "UTC",
    "to_timezone": "Asia/Tokyo"
  }
}
```

**Response:**
```json
"2025-11-05T23:30:00+09:00"
```

## Resources

### time://current
Provides the current UTC time.

### time://timezones
Lists all available IANA timezones (truncated for brevity).

## OAuth2 PKCE Flow

This server uses OAuth2 with PKCE (Proof Key for Code Exchange), which is designed for public clients that cannot securely store client secrets.

### Configuration

The OAuth2 settings are configured in `server.py`:

```python
auth=AuthConfig(
    oauth2=OAuth2Config(
        provider="custom",
        client_id="time-mcp-client",
        use_pkce=True,
        auth_url="http://localhost:8000/oauth/authorize",
        token_url="http://localhost:8000/oauth/token",
        scopes=["time:read", "time:convert"],
    )
)
```

### How PKCE Works

1. **Client generates code_verifier**: Random string (43-128 chars)
2. **Client creates code_challenge**: SHA256 hash of code_verifier
3. **Authorization request**: Client sends code_challenge to auth server
4. **User authorizes**: Via your gateway's authorization flow
5. **Token exchange**: Client sends code_verifier with authorization code
6. **Server validates**: Checks that SHA256(code_verifier) matches code_challenge

### Integration with Your Gateway

Since your gateway provides `client_secret_jwt` flow, you'll need to:

1. Configure your gateway to support PKCE
2. Set the authorization and token URLs to point to your gateway
3. Ensure your gateway validates the code_challenge and code_verifier

**Example Gateway Configuration:**
```python
# In your gateway configuration
OAUTH_AUTH_URL = "https://your-gateway.com/oauth/authorize"
OAUTH_TOKEN_URL = "https://your-gateway.com/oauth/token"
```

Then update `server.py` with your gateway URLs.

## Common Timezones

Here are some commonly used IANA timezone names:

- **UTC**: Coordinated Universal Time
- **America/New_York**: Eastern Time (US & Canada)
- **America/Chicago**: Central Time (US & Canada)
- **America/Denver**: Mountain Time (US & Canada)
- **America/Los_Angeles**: Pacific Time (US & Canada)
- **Europe/London**: GMT/BST
- **Europe/Paris**: Central European Time
- **Asia/Tokyo**: Japan Standard Time
- **Asia/Shanghai**: China Standard Time
- **Australia/Sydney**: Australian Eastern Time

## Error Handling

The server provides descriptive error messages:

- **Invalid timezone**: Returns list of valid IANA timezones
- **Invalid time format**: Explains expected ISO 8601 format
- **Conversion errors**: Details what went wrong

## Development

### Running in Development Mode

```bash
# With auto-reload (if supported)
python server.py --reload
```

### Testing Individual Components

```bash
# Test only get_current_time
python -m unittest test_server.TestGetCurrentTime

# Test only convert_time
python -m unittest test_server.TestConvertTime

# Test with verbose output
python test_server.py -v
```

### Code Quality

Run linters:
```bash
black server.py test_server.py
flake8 server.py test_server.py
mypy server.py test_server.py
```

## Troubleshooting

### OAuth Issues

**Problem**: "OAuth authentication failed"
**Solution**: 
- Verify your gateway URLs are correct
- Ensure PKCE is enabled in your gateway
- Check that scopes match between client and gateway

### Timezone Issues

**Problem**: "Invalid timezone"
**Solution**: Use IANA timezone names. Run `python -c "from zoneinfo import available_timezones; print(sorted(available_timezones()))"` to see all valid names.

### Connection Issues

**Problem**: "Cannot connect to server"
**Solution**:
- Check that the server is running
- Verify firewall settings allow the connection
- Ensure the port is not already in use

## Architecture

```
┌─────────────┐
│   Client    │
│  (with MCP) │
└──────┬──────┘
       │ OAuth2 PKCE
       │ + MCP Protocol
       ▼
┌─────────────┐      ┌──────────────┐
│   FastMCP   │──────│  Your OAuth  │
│   Server    │      │   Gateway    │
└──────┬──────┘      └──────────────┘
       │
       ▼
┌─────────────┐
│  Time Tools │
│  - get_time │
│  - convert  │
└─────────────┘
```

## License

MIT License - Feel free to use and modify as needed.

## Support

For issues related to:
- **FastMCP**: https://github.com/jlowin/fastmcp
- **MCP Protocol**: https://modelcontextprotocol.io
- **This Implementation**: Open an issue in your project repository
```

## File: TESTING.md

```markdown
# Testing Guide

## Overview

This project uses a Test-Driven Development (TDD) approach with Python's `unittest` framework.

## Test Structure

```
test_server.py
├── TestGetCurrentTime      # Tests for get_current_time tool
├── TestConvertTime         # Tests for convert_time tool
├── TestEdgeCases          # Edge cases and boundary conditions
└── TestIntegration        # Integration tests
```

## Running Tests

### Run All Tests

```bash
python test_server.py
```

### Run Specific Test Class

```bash
python -m unittest test_server.TestGetCurrentTime
```

### Run Specific Test Method

```bash
python -m unittest test_server.TestGetCurrentTime.test_get_current_time_utc_default
```

### Run with Verbose Output

```bash
python test_server.py -v
```

## Coverage Analysis

### Generate Coverage Report

```bash
coverage run test_server.py
coverage report
```

### Generate HTML Coverage Report

```bash
coverage run test_server.py
coverage html
# Open htmlcov/index.html in your browser
```

### Coverage Goals

- **Target**: >80% code coverage
- **Current**: Should be 85-90% for main functions

## Test Categories

### 1. Functional Tests

Test that each function works as specified:

- `test_get_current_time_utc_default`: Default UTC behavior
- `test_convert_time_basic`: Basic conversion
- `test_convert_time_offset_calculation`: Correct offset math

### 2. Error Handling Tests

Test that errors are handled gracefully:

- `test_get_current_time_invalid_timezone`: Invalid timezone names
- `test_convert_time_invalid_time_string`: Malformed input
- `test_convert_time_empty_string`: Empty input

### 3. Edge Case Tests

Test boundary conditions:

- `test_daylight_saving_time_aware`: DST transitions
- `test_midnight_conversion`: Midnight boundary
- `test_microseconds_preserved`: Precision preservation

### 4. Integration Tests

Test realistic workflows:

- `test_get_and_convert_workflow`: Combined operations

## Manual Testing

### Test get_current_time

```python
import asyncio
from server import get_current_time

async def test():
    result = await get_current_time("America/New_York")
    print(f"Current time in NY: {result}")

asyncio.run(test())
```

### Test convert_time

```python
import asyncio
from server import convert_time

async def test():
    result = await convert_time(
        "2025-11-05T14:30:00",
        "UTC",
        "Asia/Tokyo"
    )
    print(f"Converted time: {result}")

asyncio.run(test())
```

## Testing OAuth Flow

Since OAuth requires integration with your gateway, manual testing steps:

1. **Start the server**:
   ```bash
   python server.py
   ```

2. **Configure your MCP client** with:
   - Client ID: `time-mcp-client`
   - Auth URL: Your gateway's authorize endpoint
   - Token URL: Your gateway's token endpoint
   - Scopes: `time:read time:convert`
   - PKCE: Enabled

3. **Initiate connection** from your MCP client

4. **Complete authorization** in your gateway

5. **Test tool calls**:
   ```json
   {
     "tool": "get_current_time",
     "arguments": {"timezone_name": "UTC"}
   }
   ```

## Continuous Integration

### Example GitHub Actions Workflow

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests with coverage
      run: |
        coverage run test_server.py
        coverage report --fail-under=80
    
    - name: Generate coverage report
      run: coverage xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Test Data

### Valid Timezones

```python
VALID_TIMEZONES = [
    "UTC",
    "America/New_York",
    "Europe/London",
    "Asia/Tokyo",
    "Australia/Sydney",
]
```

### Valid Time Strings

```python
VALID_TIME_STRINGS = [
    "2025-11-05T14:30:00",
    "2025-11-05T14:30:00+00:00",
    "2025-11-05T14:30:00.123456",
    "2025-11-05T00:00:00",
]
```

### Invalid Inputs

```python
INVALID_TIMEZONES = [
    "Invalid/Timezone",
    "",
    "America/New York",  # Space not allowed
    "EST",  # Abbreviations not supported
]

INVALID_TIME_STRINGS = [
    "not-a-time",
    "2025-13-01T00:00:00",  # Invalid month
    "2025-11-32T00:00:00",  # Invalid day
    "",
]
```

## Debugging Failed Tests

### Common Issues

1. **Timezone not available**:
   - Solution: Ensure `tzdata` is installed: `pip install tzdata`

2. **Async test failures**:
   - Solution: Check that event loop is properly set up in setUp/tearDown

3. **Time-dependent test failures**:
   - Solution: Use time mocking or allow for small time differences

### Debug Mode

Add this to see more details:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

1. **Write tests first**: Follow TDD principles
2. **Test one thing**: Each test should verify one specific behavior
3. **Use descriptive names**: Test names should describe what they test
4. **Clean up resources**: Use setUp/tearDown properly
5. **Test error cases**: Don't just test the happy path
6. **Mock external dependencies**: Isolate unit tests from external services

## Test Metrics

Target metrics for this project:

- **Code Coverage**: >80%
- **Test Count**: >25 tests
- **Test Pass Rate**: 100%
- **Test Execution Time**: <5 seconds
- **Assertion Count**: ~50+ assertions
```

## File: DEPLOYMENT.md

```markdown
# Deployment Guide

## Prerequisites

- Python 3.11 or higher
- pip
- Virtual environment (recommended)
- Your OAuth gateway configured with PKCE support

## Local Development Deployment

### 1. Initial Setup

```bash
# Clone/download the project
cd time-mcp-server

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure OAuth

Edit `server.py` to point to your OAuth gateway:

```python
auth=AuthConfig(
    oauth2=OAuth2Config(
        provider="custom",
        client_id="time-mcp-client",
        use_pkce=True,
        auth_url="https://your-gateway.com/oauth/authorize",  # Update this
        token_url="https://your-gateway.com/oauth/token",     # Update this
        scopes=["time:read", "time:convert"],
    )
)
```

### 3. Run the Server

```bash
python server.py
```

The server will start and display:
```
FastMCP server running
Transport: SSE and HTTP
Authentication: OAuth2 PKCE
```

## Docker Deployment

### Dockerfile

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY server.py .

# Expose port (if needed for your setup)
EXPOSE 3000

# Run server
CMD ["python", "server.py"]
```

### Build and Run

```bash
# Build image
docker build -t time-mcp-server .

# Run container
docker run -p 3000:3000 \
  -e OAUTH_AUTH_URL=https://your-gateway.com/oauth/authorize \
  -e OAUTH_TOKEN_URL=https://your-gateway.com/oauth/token \
  time-mcp-server
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  time-mcp-server:
    build: .
    ports:
      - "3000:3000"
    environment:
      - OAUTH_AUTH_URL=${OAUTH_AUTH_URL}
      - OAUTH_TOKEN_URL=${OAUTH_TOKEN_URL}
      - OAUTH_CLIENT_ID=${OAUTH_CLIENT_ID}
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## Production Deployment

### Security Considerations

1. **Use HTTPS**: Always use HTTPS in production for OAuth endpoints
2. **Environment Variables**: Never commit credentials to source control
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Logging**: Enable comprehensive logging for audit trails
5. **Monitoring**: Set up monitoring and alerting

### Environment Variables

```bash
# Required
export OAUTH_AUTH_URL="https://your-gateway.com/oauth/authorize"
export OAUTH_TOKEN_URL="https://your-gateway.com/oauth/token"
export OAUTH_CLIENT_ID="time-mcp-client"

# Optional
export LOG_LEVEL="INFO"
export MCP_SERVER_PORT="3000"
```

### Systemd Service (Linux)

Create `/etc/systemd/system/time-mcp-server.service`:

```ini
[Unit]
Description=Time MCP Server
After=network.target

[Service]
Type=simple
User=mcp
WorkingDirectory=/opt/time-mcp-server
Environment="OAUTH_AUTH_URL=https://your-gateway.com/oauth/authorize"
Environment="OAUTH_TOKEN_URL=https://your-gateway.com/oauth/token"
ExecStart=/opt/time-mcp-server/venv/bin/python server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable time-mcp-server
sudo systemctl start time-mcp-server
sudo systemctl status time-mcp-server
```

## Cloud Deployments

### AWS (EC2)

1. Launch EC2 instance (Ubuntu 22.04 recommended)
2. Install Python 3.11
3. Follow local deployment steps
4. Configure security group to allow required ports
5. Use Elastic IP for stable endpoint
6. Consider using AWS Secrets Manager for OAuth credentials

### Google Cloud (Cloud Run)

1. Create `Dockerfile` (see above)
2. Build and push to Google Container Registry:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/time-mcp-server
   ```
3. Deploy to Cloud Run:
   ```bash
   gcloud run deploy time-mcp-server \
     --image gcr.io/PROJECT_ID/time-mcp-server \
     --platform managed \
     --set-env-vars OAUTH_AUTH_URL=https://...,OAUTH_TOKEN_URL=https://...
   ```

### Azure (Container Instances)

```bash
az container create \
  --resource-group myResourceGroup \
  --name time-mcp-server \
  --image myregistry.azurecr.io/time-mcp-server:latest \
  --environment-variables \
    OAUTH_AUTH_URL=https://... \
    OAUTH_TOKEN_URL=https://...
```

## Monitoring

### Health Check Endpoint

FastMCP may provide health check endpoints. Check your specific version.

### Logging

Configure logging in production:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/time-mcp-server.log'),
        logging.StreamHandler()
    ]
)
```

### Metrics to Monitor

- Request count
- Response times
- Error rates
- OAuth token refresh rates
- Active connections

## Scaling

### Horizontal Scaling

FastMCP servers can be scaled horizontally:

1. Deploy multiple instances
2. Use load balancer (nginx, HAProxy, or cloud LB)
3. Ensure OAuth state management works across instances

### Load Balancer Example (nginx)

```nginx
upstream mcp_servers {
    server localhost:3000;
    server localhost:3001;
    server localhost:3002;
}

server {
    listen 80;
    server_name mcp.example.com;

    location / {
        proxy_pass http://mcp_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Backup and Recovery

### Configuration Backup

```bash
# Backup configuration
tar -czf mcp-config-backup.tar.gz server.py .env

# Restore
tar -xzf mcp-config-backup.tar.gz
```

### Disaster Recovery

1. Document all OAuth configuration
2. Keep credentials in secure vault (e.g., HashiCorp Vault)
3. Maintain deployment scripts in version control
4. Test recovery procedures regularly

## Troubleshooting

### Server Won't Start

```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip list | grep fastmcp

# Check ports
netstat -tuln | grep 3000
```

### OAuth Connection Issues

```bash
# Test OAuth endpoints
curl https://your-gateway.com/oauth/authorize

# Check DNS resolution
nslookup your-gateway.com

# Verify SSL certificates
openssl s_client -connect your-gateway.com:443
```

### Performance Issues

```bash
# Check resource usage
top -p $(pgrep -f "python server.py")

# Check disk space
df -h

# Check memory
free -h
```

## Maintenance

### Updates

```bash
# Update dependencies
pip install --upgrade fastmcp

# Run tests after update
python test_server.py

# Restart server
sudo systemctl restart time-mcp-server  # If using systemd
```

### Logs Rotation

Configure logrotate (`/etc/logrotate.d/time-mcp-server`):

```
/var/log/time-mcp-server.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 mcp mcp
    postrotate
        systemctl reload time-mcp-server
    endscript
}
```

## Checklist

### Pre-Deployment

- [ ] Tests passing
- [ ] OAuth configured correctly
- [ ] Environment variables set
- [ ] Firewall rules configured
- [ ] SSL certificates installed (if needed)
- [ ] Logging configured
- [ ] Monitoring set up

### Post-Deployment

- [ ] Server running
- [ ] OAuth flow tested
- [ ] Tools responding correctly
- [ ] Logs being written
- [ ] Monitoring active
- [ ] Documentation updated

## Support

For deployment issues:
1. Check logs: `/var/log/time-mcp-server.log`
2. Review FastMCP documentation
3. Verify OAuth gateway configuration
4. Test with curl/httpie
5. Check firewall/network settings
```

## File: run_tests.sh

```bash
#!/bin/bash

# Test runner script with coverage

set -e

echo "==================================="
echo "Running Time MCP Server Tests"
echo "==================================="
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run tests with coverage
echo "Running tests with coverage..."
coverage run test_server.py

echo ""
echo "==================================="
echo "Coverage Report"
echo "==================================="
coverage report

echo ""
echo "==================================="
echo "Generating HTML Coverage Report"
echo "==================================="
coverage html
echo "HTML report generated in htmlcov/"

echo ""
echo "✅ All tests completed!"
```

## Setup Instructions

1. **Create the project directory**:
```bash
mkdir time-mcp-server
cd time-mcp-server
```

2. **Create all files**: Copy the content of each file above into the appropriate filename

3. **Make the test script executable**:
```bash
chmod +x run_tests.sh
```

4. **Set up the environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

5. **Run tests**:
```bash
python test_server.py
# Or use the script:
./run_tests.sh
```

6. **Run the server**:
```bash
python server.py
```

## Download Instructions

To create a ZIP file of your project:

```bash
# From outside the project directory
zip -r time-mcp-server.zip time-mcp-server/ -x "*/venv/*" "*/.__pycache__/*" "*/.coverage" "*/htmlcov/*"
```

Or if you're inside the project:
```bash
cd ..
zip -r time-mcp-server.zip time-mcp-server/ -x "*/venv/*" "*/__pycache__/*" "*/.coverage" "*/htmlcov/*"
```

This will create a `time-mcp-server.zip` file you can download and share.
