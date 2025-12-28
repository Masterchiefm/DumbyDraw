@echo off
setlocal

>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system" || (
    echo Requesting administrative privileges...
    goto UACPrompt
)
goto gotAdmin

:UACPrompt
echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
"%temp%\getadmin.vbs"
exit /B

:gotAdmin
if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )

set APPDATA_DIR=%LOCALAPPDATA%\DumbDrawPhD
if not exist "%APPDATA_DIR%" (
    mkdir "%APPDATA_DIR%"
)

set ROOT=%~dp0
set ENV=%ROOT%env

set DUMBDRAW_DATA_DIR=%APPDATA_DIR%

call "%ENV%\Scripts\activate.bat"
"%ENV%\Scripts\DumbDrawPhD.exe"

endlocal