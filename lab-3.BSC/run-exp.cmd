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
set "_OUT_DIR=unit-test"

:: Error transmission probabilities of BSCs
set _CREATE=0.2,0.5,0.7
set _ERRORS=0.1,0.5,0.8

:: Command to run calcBSCInfo
set "_CMD=python byteChannel.py"
set "_Source=python byteSource.py"
set "_Generate=python generate.py"
set "MSG_LENGTH=1024"

:: ----- Config : end

:: Get this script's directory.
for %%I in ("%~dp0.") do set "_SCRIPT_DIR=%%~fI"

:: Go into the script's directory (incase this script is called from other directory).
pushd %_SCRIPT_DIR%

:: Action.
echo:Unit generation is running...
if not exist %_DATA_DIR% mkdir %_DATA_DIR%
if not exist %_OUT_DIR% mkdir %_OUT_DIR%

set CSV_P=
set DATA_P=
set CSV_N=
set INPUT=
set OUTPUT=
set NOISE=
set /A NOISE_LENGTH=%MSG_LENGTH%


for %%j in (%_CREATE%) do (
    set CSV_P=!CSV_P!;%_DATA_DIR%\DMS.p0=%%j.csv
    set DATA_P=!DATA_P!;%_OUT_DIR%\DMS.p0=%%j.dat
)
call %_Generate% %_CREATE% %CSV_P%

set CSV_P=
set DATA_P=
for %%f in ("%_DATA_DIR%\DMS.*.csv") do (
    set CSV_P=!CSV_P!;%_DATA_DIR%\%%~nxf
    set DATA_P=!DATA_P!;%_OUT_DIR%\%%~nxf.dat
)
@REM echo "%CSV_P% %DATA_P%"
call %_Source% %CSV_P% %DATA_P% %MSG_LENGTH%

for %%j in (%_ERRORS%) do (
    set NOISE=!NOISE!;%_DATA_DIR%\BSC.p=%%j.dat
    set CSV_N=!CSV_N!;%_DATA_DIR%\BSC.p=%%j.csv
)
@REM echo "%NOISE% %CSV_N%"
call %_Generate% %_ERRORS% %CSV_N%
call %_Source% %CSV_N% %NOISE% %NOISE_LENGTH%


set NOISE=
for %%f in ("%_OUT_DIR%\DMS.*.dat") do (
    for %%j in (%_ERRORS%) do (
        set INPUT=!INPUT!;%%~nxf
        set NOISE=!NOISE!;%_DATA_DIR%\BSC.p=%%j.dat
        set OUTPUT=!OUTPUT!;BSC.p=%%j.%%~nxf
@REM     echo "!OUTPUT!"
    )
)
@REM echo %INPUT%
@REM echo %NOISE%
@REM echo %OUTPUT%
@REM echo %_DATA_DIR%
call %_CMD% "%INPUT%" "%NOISE%" "%OUTPUT%" -d %_OUT_DIR% -S

@REM del /Q %_TEMP_DIR%
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
