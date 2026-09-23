$ErrorActionPreference = 'Stop'
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'Project virtual environment not found. Run the installation steps in README.md first.'
}
$projectParent = Split-Path -Parent $PSScriptRoot
& $python -m PyInstaller --noconfirm --clean --onefile --windowed --name UniversalIPMIPaste --paths $projectParent main.py
Write-Host "Built: dist\UniversalIPMIPaste.exe"
