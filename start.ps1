<#Ice_fly's PowerShell Discord Bot Script#>
$host.ui.RawUI.WindowTitle = "ERPLDiscordBot"
Write-Host "Starting Bot" -ForegroundColor Cyan
python -m erplbot
Start-Sleep -s 25
exit 0