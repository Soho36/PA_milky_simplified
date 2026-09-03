$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = Join-Path $root 'src'
Push-Location $root
try { & (Join-Path $root 'venv\Scripts\python.exe') -m unittest discover -s tests -t . }
finally { Pop-Location }
