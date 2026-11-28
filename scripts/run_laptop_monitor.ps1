$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot
$env:OSLAB_DEMO = '0'
& py -3.13 app.py
