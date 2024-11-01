:::::
:: Unit test for byteChannel
:::::

:: Do not display every line of the code in the console.
@echo off

:: Make sure all variables set or changed in this script is local.
setlocal enabledelayedexpansion

:: ----- Config : begin

:: Directory for data
set "_DATA_DIR=input"

:: Directory for Outputs
set "_OUT_DIR=output"

:: Error transmission probabilities of BSCs
set _ERRORS=0.1,0.3,0.6,0.8

:: Command to run calcBSCInfo
set "_CMD=python byteChannel.py"

:: ----- Config : end

:: Get this script's directory.
for %%I in ("%~dp0.") do set "_SCRIPT_DIR=%%~fI"

:: Go into the script's directory (incase this script is called from other directory).
pushd %_SCRIPT_DIR%

:: Action.
echo:Unit generation is running...

set INPUT=
set OUTPUT=
set NOISE=

for %%f in ("%_DATA_DIR%\DMS.*.dat") do (
    set INPUT=!INPUT!;%_DATA_DIR%\%%~nxf
@REM     echo "!INPUT!"
)
for %%j in (%_ERRORS%) do (
    set NOISE=!NOISE!;%%j
@REM     echo "!NOISE!"
)
for %%f in ("%_DATA_DIR%\DMS.*.dat") do (
    for %%j in (%_ERRORS%) do (
        set OUTPUT=!OUTPUT!;%_OUT_DIR%\BSC.p=%%j.%%~nxf
@REM     echo "!OUTPUT!"
    )
)
@REM echo %INPUT%
@REM echo %NOISE%
@REM echo %OUTPUT%
@REM echo %_DATA_DIR%
call %_CMD% "%INPUT%" "%NOISE%" "%OUTPUT%" -S

echo:Unit generation completed.
echo:

:: Show results.
echo:
echo:Recommend to open these two files in a spreadsheet software for comparison.
echo:

:: Return to the previous directory.
popd

:: Exit.
endlocal & exit /b
