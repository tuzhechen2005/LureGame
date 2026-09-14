param([string]$GameExe = 'D:\LureGame\Release\Encounter-20260914\Windows\LureGame\Binaries\Win64\LureGame.exe')
$ErrorActionPreference = 'Stop'
if (!(Test-Path -LiteralPath $GameExe)) { throw "Packaged game missing: $GameExe" }
foreach ($test in @('LureEncounterTest','LureSmokeTest','LureInputTest','LureSessionTest')) {
    $logPath = "D:\LureGame\Saved\Logs\EncounterPackaged-$test.log"
    $gameProcess = Start-Process -FilePath $gameExe -ArgumentList "-$test -nullrhi -nosound -unattended -abslog=$logPath" -WindowStyle Hidden -Wait -PassThru
    if ($gameProcess.ExitCode -ne 0) { throw "$test process failed: $($gameProcess.ExitCode)" }
    if (!(Test-Path -LiteralPath $logPath)) { throw "$test produced no log" }
    $results = Select-String -LiteralPath $logPath -Pattern '(LURE|ENCOUNTER)_.*(PASS|FAIL|COMPLETE)'
    $results | ForEach-Object { $_.Line }
    if (Select-String -LiteralPath $logPath -Pattern '(LURE|ENCOUNTER)_.*\bFAIL\b') { throw "$test assertion failed" }
    if (!(Select-String -LiteralPath $logPath -Pattern '(LURE|ENCOUNTER)_.*COMPLETE failures=0')) { throw "$test did not complete successfully" }
}
