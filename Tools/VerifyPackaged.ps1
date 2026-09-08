$ErrorActionPreference = 'Stop'
$gameExe = 'D:\LureGame\Release\Windows\LureGame\Binaries\Win64\LureGame.exe'
foreach ($test in @('LureSmokeTest','LureInputTest','LureSessionTest')) {
    $logPath = "D:\LureGame\Saved\Logs\RealisticPackaged$test.log"
    $gameProcess = Start-Process -FilePath $gameExe -ArgumentList "-$test -nullrhi -nosound -unattended -abslog=$logPath" -WindowStyle Hidden -Wait -PassThru
    if ($gameProcess.ExitCode -ne 0) { throw "$test process failed: $($gameProcess.ExitCode)" }
    if (!(Test-Path -LiteralPath $logPath)) { throw "$test produced no log" }
    $results = Select-String -LiteralPath $logPath -Pattern 'LURE_.*(PASS|FAIL|complete)'
    $results | ForEach-Object { $_.Line }
    if (Select-String -LiteralPath $logPath -Pattern 'LURE_.*\bFAIL\b') { throw "$test assertion failed" }
    if (!(Select-String -LiteralPath $logPath -Pattern 'LURE_.*COMPLETE failures=0')) { throw "$test did not complete successfully" }
}
