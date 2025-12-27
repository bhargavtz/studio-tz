# Quick Restart Script for NCD INAI Frontend
# Run this after adding your Clerk keys to .env.local

Write-Host "🔄 Restarting Next.js Development Server..." -ForegroundColor Cyan

# Kill any existing Next.js dev server on port 3000
Write-Host "📍 Checking for processes on port 3000..." -ForegroundColor Yellow
$process = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique

if ($process) {
    Write-Host "⚠️  Found process $process on port 3000. Stopping it..." -ForegroundColor Yellow
    Stop-Process -Id $process -Force
    Start-Sleep -Seconds 2
    Write-Host "✅ Process stopped!" -ForegroundColor Green
} else {
    Write-Host "✅ Port 3000 is free!" -ForegroundColor Green
}

# Start the dev server
Write-Host "🚀 Starting Next.js dev server..." -ForegroundColor Cyan
npm run dev
