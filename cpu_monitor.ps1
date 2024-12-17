# Define the output file
$outputFile = "cpu_usage_log.txt"

# Get the current date and time
"==== CPU UTILIZATION REPORT: $(Get-Date) ====" | Out-File -FilePath $outputFile

# Get overall CPU utilization
"Overall CPU Utilization:" | Out-File -FilePath $outputFile -Append
Get-Counter '\Processor(_Total)\% Processor Time' | ForEach-Object {
    "CPU Load: {0}%" -f [math]::Round($_.CounterSamples.CookedValue, 2)
} | Out-File -FilePath $outputFile -Append

# Get the top 5 processes by CPU usage
"`nTop 5 Processes by CPU Usage:" | Out-File -FilePath $outputFile -Append
Get-Process | Sort-Object CPU -Descending | Select-Object -First 5 `
    | Format-Table -Property Id, ProcessName, CPU -AutoSize `
    | Out-File -FilePath $outputFile -Append

# Confirm the script execution
Write-Output "CPU usage and top 5 processes have been saved to $outputFile"
