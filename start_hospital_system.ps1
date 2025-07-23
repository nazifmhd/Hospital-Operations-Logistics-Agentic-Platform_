#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Professional Hospital Operations System Startup Script
.DESCRIPTION
    Launches the complete hospital operations agentic platform
.EXAMPLE
    .\start_hospital_system.ps1
#>

Write-Host "🏥 HOSPITAL OPERATIONS AGENTIC PLATFORM" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Set location to multi_agent_system
Set-Location "multi_agent_system"

Write-Host "🔍 Running system verification..." -ForegroundColor Yellow
python system_verification.py

Write-Host "`n🚀 Starting Professional Hospital Operations Server..." -ForegroundColor Green
Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Health Endpoint: http://localhost:8000/health" -ForegroundColor Green
Write-Host "`nPress Ctrl+C to stop the server" -ForegroundColor Yellow

# Start the professional server
python professional_main.py
