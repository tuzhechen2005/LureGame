@echo off
call "D:\epic\UE_5.8\Engine\Build\BatchFiles\Build.bat" LureGameEditor Win64 Development "-Project=%~dp0LureGame.uproject" -WaitMutex
if errorlevel 1 exit /b 1
"D:\epic\UE_5.8\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "%~dp0LureGame.uproject" -game -nullrhi -nosound -unattended -LureSmokeTest
exit /b %errorlevel%
