:::::
:: Unit test for calcBSCInfo
:::::

:: Do not display every line of the code in the console.
@echo off

:: Make sure all variables set or changed in this script is local.
setlocal

:: ----- Config : begin

:: Directory for data
set "_DATA_DIR=unit-test"

:: Result file
set "_RESULT_FILE=%_DATA_DIR%\results.csv"

:: Expecting result file
set "_EXPECT_FILE=%_DATA_DIR%\results.expect.csv"

:: Command to run calcBSCInfo
set "_CMD=python calcBSCInfo.py"

:: ----- Config : end

:: Get this script's directory.
for %%I in ("%~dp0.") do set "_SCRIPT_DIR=%%~fI"

:: Go into the script's directory (incase this script is called from other directory).
pushd %_SCRIPT_DIR%

if exist "%_RESULT_FILE%" del "%_RESULT_FILE%"

:: Action.
echo:Unit test is running...
call %_CMD% "%_DATA_DIR%\DMS.p0=0.7.len=1MB.dat" "%_DATA_DIR%\BSC.p=0.2.DMS.p0=0.7.len=1MB.dat" "%_RESULT_FILE%"
call %_CMD% "%_DATA_DIR%\DMS.p0=0.7.len=1MB.dat" "%_DATA_DIR%\BSC.p=0.5.DMS.p0=0.7.len=1MB.dat" "%_RESULT_FILE%"
call %_CMD% "%_DATA_DIR%\DMS.p0=0.9.len=1MB.dat" "%_DATA_DIR%\BSC.p=0.2.DMS.p0=0.9.len=1MB.dat" "%_RESULT_FILE%"
echo:Unit test completed.
echo:

:: Show results.
echo:Expecting: ("%_EXPECT_FILE%")
type "%_EXPECT_FILE%"
echo:
echo:Results: ("%_RESULT_FILE%")
type "%_RESULT_FILE%"
echo:
echo:Recommend to open these two files in a spreadsheet software for comparison.
echo:

:: Return to the previous directory.
popd

:: Exit.
endlocal & exit /b
