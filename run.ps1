# =====================================================================
# Nexdemy — Smart Academic & Student Management Portal Launcher
# =====================================================================

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  Nexdemy — Smart Academic & Student Management Portal" -ForegroundColor Cyan
Write-Host "  MySQL Engine: root / 2006 (nexdemy_db)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[+] Working Directory: $ScriptDir" -ForegroundColor Gray

# Check for Python
$PythonCmd = Get-Command python -ErrorAction SilentlyContinue

if ($PythonCmd) {
    Write-Host "[+] Launching Nexdemy backend server and opening browser..." -ForegroundColor Green
    & python "$ScriptDir\run.py"
} else {
    $PyCmd = Get-Command py -ErrorAction SilentlyContinue
    if ($PyCmd) {
        Write-Host "[+] Launching via py launcher..." -ForegroundColor Green
        & py "$ScriptDir\run.py"
    } else {
        Write-Host "[!] Python not detected. Opening Nexdemy directly in browser..." -ForegroundColor Yellow
        Start-Process "$ScriptDir\index.html"
    }
}
