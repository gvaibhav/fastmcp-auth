# Time MCP Server - Quick Start Script
# Run this to start the simplified server (no OAuth required)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Time MCP Server - Quick Start" -ForegroundColor Cyan
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

# Run the simplified server
Write-Host "Starting Time MCP Server (Simplified - No Auth)..." -ForegroundColor Green
Write-Host ""
python simplified_server.py
