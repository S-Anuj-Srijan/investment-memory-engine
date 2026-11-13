# Current Level 3 application launcher. Legacy Streamlit script is archived in legacy/.
param([switch]$Build)
& (Join-Path $PSScriptRoot 'start_project.ps1') -Build:$Build
