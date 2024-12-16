:::::
:: Unit work for repetitionCoder
:::::

:: Do not display every line of the code in the console.
@echo off

:: Make sure all variables set or changed in this script is local.
setlocal enabledelayedexpansion

:: ----- Config : begin

:: Directory for data
set "_DATA_DIR=unit-data"

:: Directory for Outputs
set "_SOURCE_FILE=unit-data\source.dat"
set "_RESULT_FILE=unit-data\result.csv"

:: Probabilities of DMSs
set _ERRORS=0.2,0.5,0.7
set _ERRORS_T=
set _REPEAT_LENGTH=3,5,7

:: Command to run
set "_CMD=python repetitionCoder.py"
set "_Channel=python byteChannel.py"
set "_Calc=python calcErrorRate.py"
set "_Generate=python generate.py"
set "_Source=python byteSource.py"
set "MSG_LENGTH=17258"
:: ----- Config : end

:: Get this script's directory.
for %%I in ("%~dp0.") do set "_SCRIPT_DIR=%%~fI"

:: Go into the script's directory (incase this script is called from other directory).
pushd %_SCRIPT_DIR%

:: Action.
echo:Unit generation is running...
if not exist %_DATA_DIR% mkdir %_DATA_DIR%
if not exist %_SOURCE_FILE% goto eof
if not exist %_RESULT_FILE% echo "">%_RESULT_FILE%

set CSV_P=
set ERROR_P=
set INPUT=
set OUTPUT=


@REM echo Get errors data
for %%i in (%_ERRORS%) do (
    set CSV_P=!CSV_P!;%_DATA_DIR%\DMS.p=%%i.csv
)
@REM echo %CSV_P%
for %%j in (%_REPEAT_LENGTH%) do (
    set ERROR_P=
    for %%i in (%_ERRORS%) do (
        set ERROR_P=!ERROR_P!;%_DATA_DIR%\DMS.p=%%i.len=%%j.dat
    )
    set /A _length = %MSG_LENGTH% * %%j
@REM     echo !ERROR_P! !_length!
    call %_Generate% %_ERRORS% %CSV_P%
    call %_Source% %CSV_P% !ERROR_P! !_length! -p=[5,0,0,0]
)

@REM echo Encode source different repeat times
for %%j in (%_REPEAT_LENGTH%) do (
    call %_CMD% encode %%j %_SOURCE_FILE% "%_DATA_DIR%\RC.en.len=%%j.dat"
)
echo:

@REM echo Apply BSC Channels to encoded sources
for %%j in (%_REPEAT_LENGTH%) do (
    set INPUT=
    set ERROR_P=
    set OUTPUT=
    for %%i in (%_ERRORS%) do (
        set INPUT=!INPUT!;"%_DATA_DIR%\RC.en.len=%%j.dat"
        set ERROR_P=!ERROR_P!;%_DATA_DIR%\DMS.p=%%i.len=%%j.dat
        set OUTPUT=!OUTPUT!;"%_DATA_DIR%\DMS.p=%%i.RC.en.len=%%j.dat"
    )
@REM     echo: !INPUT! !OUTPUT! !ERROR_P!
    call %_Channel% !INPUT! !ERROR_P! !OUTPUT! -S
)

echo:
@REM echo Decode encoded source with noise
for %%j in (%_REPEAT_LENGTH%) do (
    set INPUT=
    set OUTPUT=
    for %%i in (%_ERRORS%) do (
        set INPUT=!INPUT!;"%_DATA_DIR%\DMS.p=%%i.RC.en.len=%%j.dat"
        set OUTPUT=!OUTPUT!;"%_DATA_DIR%\DMS.p=%%i.RC.de.len=%%j.dat"
    )
@REM     echo: !INPUT! !OUTPUT!
    call %_CMD% decode !INPUT! !OUTPUT!
)

echo:Unit coding completed.
echo:

:: Show results.
echo:
echo:Recommend to open these two files in a spreadsheet software for comparison.
echo:

for %%j in (%_REPEAT_LENGTH%) do (
    set INPUT=
    set OUTPUT=
    for %%i in (%_ERRORS%) do (
        set INPUT=!INPUT!;%_SOURCE_FILE%
        set OUTPUT=!OUTPUT!;"%_DATA_DIR%\DMS.p=%%i.RC.de.len=%%j.dat"
    )
@REM     echo !INPUT! !OUTPUT! %_RESULT_FILE%
    call %_Calc% !INPUT! !OUTPUT! %_RESULT_FILE%
)

echo:>>%_RESULT_FILE%

:: Return to the previous directory.
popd

:: Exit.
endlocal & exit /b
