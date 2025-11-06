# Time MCP Server - SSE Mode with OAuth
# Run this to start the secured server in SSE mode

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Time MCP Server - SSE Mode" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
if (-Not (Test-Path ".\venv")) {
    Write-Host "Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup first." -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1

# Run the secured server in SSE mode
Write-Host "Starting Time MCP Server in SSE Mode..." -ForegroundColor Green
Write-Host "Server will be available at: http://localhost:3000/sse" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""
python time_mcp_server.py
