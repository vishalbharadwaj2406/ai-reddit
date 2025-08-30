# =============================================================================
# AI Social BFF (Backend for Frontend) Complete Setup & Run Script
# =============================================================================
# This script does EVERYTHING needed to run the AI Social platform:
# 1. Cleans previous builds
# 2. Builds frontend static files
# 3. Starts the FastAPI backend server (serves both API + frontend)
# 4. Access everything at http://localhost:8000
# =============================================================================

param(
    [switch]$SkipBuild,  # Use -SkipBuild to only start server without rebuilding
    [switch]$DevMode     # Use -DevMode for development with auto-reload
)

Write-Host "🚀 AI Social BFF Setup & Launch Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$frontendPath = Join-Path $projectRoot "frontend\website"
$backendPath = Join-Path $projectRoot "backend"

# =============================================================================
# STEP 1: FRONTEND BUILD (unless skipped)
# =============================================================================

if (-not $SkipBuild) {
    Write-Host "🔧 STEP 1: Building Frontend" -ForegroundColor Yellow
    Write-Host "----------------------------" -ForegroundColor Yellow
    
    Set-Location $frontendPath
    
    # Clean previous builds
    Write-Host "🧹 Cleaning previous builds..." -ForegroundColor Blue
    if (Test-Path ".next") {
        Remove-Item -Recurse -Force .next -ErrorAction SilentlyContinue
        Write-Host "   ✅ Removed .next directory" -ForegroundColor Green
    }
    
    if (Test-Path "dist") {
        Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
        Write-Host "   ✅ Removed dist directory" -ForegroundColor Green
    }
    
    if (Test-Path "out") {
        Remove-Item -Recurse -Force out -ErrorAction SilentlyContinue
        Write-Host "   ✅ Removed out directory" -ForegroundColor Green
    }
    
    # Clean node_modules cache
    if (Test-Path "node_modules\.cache") {
        Remove-Item -Recurse -Force "node_modules\.cache" -ErrorAction SilentlyContinue
        Write-Host "   ✅ Cleaned node_modules cache" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "📦 Building Next.js application..." -ForegroundColor Blue
    
    # Build the Next.js application
    npm run build
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Frontend build failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "   ✅ Next.js build completed" -ForegroundColor Green
    Write-Host ""
    
    # =============================================================================
    # STEP 2: VERIFY BUILD OUTPUT
    # =============================================================================
    
    Write-Host "📁 Verifying Next.js build output..." -ForegroundColor Blue
    
    # Verify .next directory exists (standard Next.js build)
    if (Test-Path ".next") {
        Write-Host "   ✅ Next.js build completed successfully" -ForegroundColor Green
        Write-Host "   📂 Using .next directory for serving" -ForegroundColor Cyan
    } else {
        Write-Host "   ❌ Next.js build failed - .next directory not found" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "🎉 Frontend build completed successfully!" -ForegroundColor Green
    Write-Host "📂 Next.js build ready in .next/ directory for FastAPI serving" -ForegroundColor Cyan
    Write-Host ""
    
} else {
    Write-Host "⏭️  STEP 1: Skipping frontend build (using existing .next/)" -ForegroundColor Yellow
    Write-Host ""
}

# =============================================================================
# STEP 3: START BACKEND SERVER
# =============================================================================

Write-Host "🔥 STEP 2: Starting Backend Server" -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Yellow

Set-Location $backendPath

# Check if .next directory exists
$nextPath = Join-Path $frontendPath ".next"
if (!(Test-Path $nextPath)) {
    Write-Host "❌ Next.js build directory not found: $nextPath" -ForegroundColor Red
    Write-Host "   Run without -SkipBuild to build the frontend first" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Next.js build directory found" -ForegroundColor Green
Write-Host ""

# Start the FastAPI server
Write-Host "🚀 Starting FastAPI server..." -ForegroundColor Blue
Write-Host ""
Write-Host "🌐 Server will be available at:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:8000/" -ForegroundColor White
Write-Host "   API:      http://localhost:8000/api/v1/" -ForegroundColor White
Write-Host "   Docs:     http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Health:   http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

if ($DevMode) {
    # Development mode with auto-reload
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
} else {
    # Production mode
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
}

# =============================================================================
# CLEANUP & INSTRUCTIONS
# =============================================================================

Write-Host ""
Write-Host "👋 Server stopped" -ForegroundColor Yellow
Write-Host ""
Write-Host "📖 Usage Examples:" -ForegroundColor Cyan
Write-Host "   .\run-bff.ps1                # Full build + start server"
Write-Host "   .\run-bff.ps1 -SkipBuild    # Start server only (skip build)"
Write-Host "   .\run-bff.ps1 -DevMode      # Development mode with auto-reload"
Write-Host ""
