$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = Join-Path $root 'src'
& (Join-Path $root 'venv\Scripts\python.exe') -m pa_milky @args
