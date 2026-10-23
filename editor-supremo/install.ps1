# Editor Supremo installer for Windows PowerShell.
# Usage:  powershell -ExecutionPolicy Bypass -File .\install.ps1 -Target C:\ruta\a\OpenMontage
param(
  [Parameter(Mandatory = $true)][string]$Target
)
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not (Test-Path (Join-Path $Target "AGENT_GUIDE.md")) -or -not (Test-Path (Join-Path $Target "pipeline_defs"))) {
  Write-Error "Target must be the OpenMontage folder that contains AGENT_GUIDE.md"
}

Copy-Item -Path (Join-Path $Here "overlay\*") -Destination $Target -Recurse -Force

$Begin = "<!-- EDITOR-SUPREMO:BEGIN -->"
$End = "<!-- EDITOR-SUPREMO:END -->"
$Block = @"
$Begin
## CHANNEL MODE (Editor Supremo — local overlay, highest priority)
If the request involves **Hard Times Heritage**, **Sumerian Vault** or **Beneath America**
(or the codes HTH / SV / BA, or a project id starting with hth- / sv- / ba-), read
[``CHANNELS.md``](CHANNELS.md) FIRST and follow it before any other routing in this repo.
$End
"@

foreach ($name in @("CLAUDE.md", "AGENTS.md", "AGENT_GUIDE.md", "CODEX.md", "CURSOR.md", "COPILOT.md")) {
  $file = Join-Path $Target $name
  if (-not (Test-Path $file)) { continue }
  $text = [System.IO.File]::ReadAllText($file)
  $pattern = [regex]::Escape($Begin) + "(?s).*?" + [regex]::Escape($End) + "\s*"
  $text = [regex]::Replace($text, $pattern, "")
  $nl = $text.IndexOf("`n")
  if ($text.StartsWith("# ") -and $nl -gt 0) {
    $text = $text.Substring(0, $nl) + "`n`n" + $Block + "`n`n" + $text.Substring($nl + 1).TrimStart("`r", "`n")
  } else {
    $text = $Block + "`n`n" + $text
  }
  [System.IO.File]::WriteAllText($file, $text, (New-Object System.Text.UTF8Encoding($false)))
  Write-Host "patched $name"
}

Write-Host "Validating..."
Push-Location $Target
try {
  $py = if (Test-Path ".venv\Scripts\python.exe") { ".venv\Scripts\python.exe" } else { "python" }
  & $py -c "import sys; sys.path.insert(0,'.'); from styles.playbook_loader import load_playbook; from lib.pipeline_loader import load_pipeline; [load_playbook(n) for n in ('hard-times-heritage','sumerian-vault','beneath-america')]; load_pipeline('channel-documentary'); print('  OK playbooks + pipeline')"
} finally {
  Pop-Location
}
Write-Host "Editor Supremo installed in $Target"
