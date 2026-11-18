
$ErrorActionPreference = "Stop"

$OutputFile = "C:\KeyloggerLab\windows_events.jsonl"

$AllowedProcesses = @(
    "cmd.exe",
    "powershell.exe",
    "pwsh.exe",
    "whoami.exe",
    "ipconfig.exe",
    "ping.exe",
    "tracert.exe",
    "chrome.exe",
    "msedge.exe",
    "firefox.exe"
)

$Events = Get-WinEvent -FilterHashtable @{
    LogName = "Security"
    Id      = 4688
} -MaxEvents 200

$Records = foreach ($Event in $Events) {
    $Xml = [xml]$Event.ToXml()
    $Data = @{}

    foreach ($Item in $Xml.Event.EventData.Data) {
        $Data[[string]$Item.Name] = [string]$Item.'#text'
    }

    $ProcessPath = $Data["NewProcessName"]
    $ProcessName = [System.IO.Path]::GetFileName($ProcessPath)

    if ($AllowedProcesses -contains $ProcessName) {
        [PSCustomObject]@{
            timestamp    = $Event.TimeCreated.ToString("o")
            event_id     = 4688
            process_name = $ProcessName
            process_path = $ProcessPath
            parent_path  = $Data["ParentProcessName"]
            username     = $Data["SubjectUserName"]
        }
    }
}

$Records |
    ConvertTo-Json -Compress -Depth 3 |
    Set-Content -Encoding utf8 $OutputFile

Write-Host "Collected $(@($Records).Count) matching event(s)."
Write-Host "Output file: $OutputFile"
