param(
    [string]$GameExe = 'D:\epic\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe',
    [switch]$Packaged
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$logRoot = Join-Path $projectRoot 'Saved\Logs'
if (!(Test-Path -LiteralPath $GameExe)) { throw "Executable missing: $GameExe" }
$markers = @{
    LureEncounterTest = 'ENCOUNTER_TEST'; LureSmokeTest = 'LURE_TEST'
    LureInputTest = 'LURE_INPUT'; LureSessionTest = 'LURE_SESSION'
    LurePopulationTest = 'LURE_POPULATION_TEST'; LureShoreTest = 'LURE_SHORE_TEST'
}
foreach ($test in @('LureEncounterTest','LureSmokeTest','LureInputTest','LureSessionTest','LurePopulationTest','LureShoreTest')) {
    $prefix = if ($Packaged) { 'ShorePackaged' } else { 'ShoreEditor' }
    $logPath = Join-Path $logRoot "$prefix-$test.log"
    if (Test-Path -LiteralPath $logPath) { Remove-Item -LiteralPath $logPath }
    $testArgs = "-$test -nullrhi -nosound -unattended -nosplash -nop4 -abslog=`"$logPath`""
    if (!$Packaged) { $testArgs = "`"$projectRoot\LureGame.uproject`" -game $testArgs" }
    $proc = Start-Process -FilePath $GameExe -ArgumentList $testArgs -WindowStyle Hidden -PassThru
    if (!$proc.WaitForExit(180000)) { Stop-Process -Id $proc.Id; throw "$test exceeded three minutes" }
    if ($proc.ExitCode -ne 0) { throw "$test exited $($proc.ExitCode), see $logPath" }
    if (!(Test-Path -LiteralPath $logPath)) { throw "$test did not write a log" }
    $failures = Select-String -LiteralPath $logPath -Pattern '(LURE|ENCOUNTER)_.*\bFAIL\b'
    if ($failures) { $failures | ForEach-Object { $_.Line }; throw "$test assertions failed" }
    $complete = Select-String -LiteralPath $logPath -Pattern "$($markers[$test]) COMPLETE failures=0\s*$"
    if (!$complete) { throw "$test did not finish its assertions" }
    $complete | ForEach-Object { $_.Line }
}
