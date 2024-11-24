:::::
:: Unit test for byteSourceCoder
:::::

:: Do not display every line of the code in the console.
@echo off

:: Make sure all variables set or changed in this script is local.
setlocal enabledelayedexpansion

:: ----- Config : begin

:: Directory for data
set "_DATA_DIR=unit-data"

:: Directory for Outputs
set "_OUT_DIR=unit-data"

:: Probabilities of DMSs
set _CREATE=0.2,0.5,0.7
set _CREATE_T=

:: Command to run calcBSCInfo
set "_CMD=python byteSourceCoder.py"
set "_Source=python byteSource.py"
set "_Generate=python generate.py"
set "MSG_LENGTH=102400"
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

for %%j in (%_CREATE%) do (
    set CSV_P=!CSV_P!;%_DATA_DIR%\DMS.p0=%%j.csv
    set DATA_P=!DATA_P!;%_OUT_DIR%\DMS.p0=%%j.dat
    set _CREATE_T=%%j
)
@REM echo "%CSV_P% %DATA_P%"
call %_Generate% %_CREATE% %CSV_P%
call %_Source% %CSV_P% %DATA_P% %MSG_LENGTH%

@REM echo Using corresponding PMF
for %%j in (%_CREATE%) do (
    call %_CMD% encode "%_DATA_DIR%\DMS.p0=%%j.csv" "%_OUT_DIR%\DMS.p0=%%j.dat" "%_OUT_DIR%\HC.en.p0=%%j.dat"
)

for %%j in (%_CREATE%) do (
    call %_CMD% decode "%_OUT_DIR%\HC.en.p0=%%j.dat" "%_OUT_DIR%\HC.de.p0=%%j.dat"
)

echo:
@REM echo Using other PMF
for %%j in (%_CREATE%) do (
    call %_CMD% encode "%_DATA_DIR%\DMS.p0=!_CREATE_T!.csv" "%_OUT_DIR%\DMS.p0=%%j.dat" "%_OUT_DIR%\HC.en.PMF=!_CREATE_T!.p0=%%j.dat"
    set _CREATE_T=%%j
)

for %%j in (%_CREATE%) do (
    call %_CMD% decode "%_OUT_DIR%\HC.en.PMF=!_CREATE_T!.p0=%%j.dat" "%_OUT_DIR%\HC.de.PMF=!_CREATE_T!.p0=%%j.dat"
    set _CREATE_T=%%j
)

echo:Unit coding completed.
echo:

:: Show results.
echo:
echo:Recommend to open these two files in a spreadsheet software for comparison.
echo:

for %%j in (%_CREATE%) do (
    call %_CMD% compare "%_OUT_DIR%\DMS.p0=%%j.dat" "%_OUT_DIR%\HC.de.p0=%%j.dat"
)



for %%j in (%_CREATE%) do (
    call %_CMD% compare "%_OUT_DIR%\DMS.p0=%%j.dat" "%_OUT_DIR%\HC.de.PMF=!_CREATE_T!.p0=%%j.dat"
    set _CREATE_T=%%j
)


:: Return to the previous directory.
popd

:: Exit.
endlocal & exit /b
