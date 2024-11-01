:::::
:: Run a batch experiment
:: ver: 20211014.1833
:::::
:: Do not display every line of the code
@echo off

:: Make sure all variables in this script is local
setlocal

:: ----- Config : begin

:: Directory for input files
set "EXP_INPUT_DIR=input"

:: Directory for output files
set "EXP_OUTPUT_DIR=output"

:: Length of each output file.
set "MSG_LEN=1024000"

:: Command to call for each input file
set "EXP_CMD=python byteSource.py"

:: ----- Config : end

:: Get this script's directory
for %%I in ("%~dp0.") do set "SCRIPT_DIR=%%~fI"

:: Go into the script's directory (incase this script is called from other directory)
pushd "%SCRIPT_DIR%"

:: Run EXP_CMD on each file in EXP_INPUT_DIR
for %%f in ("%EXP_INPUT_DIR%\*.*") do (
    echo Processing "%EXP_INPUT_DIR%\%%~nxf" ...
    call %EXP_CMD% "%EXP_INPUT_DIR%\%%~nxf" "%EXP_OUTPUT_DIR%\%%~nxf.dat" %MSG_LEN%

    REM :: Use calcInfo to verify if the output meets our needs.
    call python calcInfo.py "%EXP_OUTPUT_DIR%\%%~nxf.dat" "%EXP_OUTPUT_DIR%\calcInfo.csv"^
        --export-p "%EXP_OUTPUT_DIR%\%%~nxf.dat.PDF.csv"
)



:: Return to the previous directory
popd

:: Exit
endlocal & exit /b
