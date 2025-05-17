@echo off
setlocal EnableDelayedExpansion

set HOST_NAME=com.example.nativehost
set REG_PATH=HKCU\Software\Google\Chrome\NativeMessagingHosts\%HOST_NAME%
set JSON_SRC=%~dp0\..\native\host.json
set JSON_DST=%LOCALAPPDATA%\Google\Chrome\User Data\NativeMessagingHosts\%HOST_NAME%.json

REM Create directory if it doesn't exist
if not exist "%LOCALAPPDATA%\Google\Chrome\User Data\NativeMessagingHosts" (
    mkdir "%LOCALAPPDATA%\Google\Chrome\User Data\NativeMessagingHosts"
)

REM Replace placeholder with actual path to main.py
set "MAIN_PATH=%~dp0\..\native\main.py"
set "MAIN_PATH=!MAIN_PATH:\=\\!"

powershell -Command "(Get-Content '%JSON_SRC%') -replace '__REPLACED_BY_INSTALL_SCRIPT__', '!MAIN_PATH!' | Set-Content '%JSON_DST%'"

REM Register the JSON file in registry
reg add "%REG_PATH%" /ve /t REG_SZ /d "%JSON_DST%" /f

echo 등록 완료: %JSON_DST%
pause
