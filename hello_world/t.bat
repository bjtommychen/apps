REM  QBFC Project Options Begin
::  HasVersionInfo: No
REM  Companyname: 
REM  Productname: 
REM  Filedescription: 
REM  Copyrights: 
REM  Trademarks: 
REM  Originalname: 
REM  Comments: 
REM  Productversion:  0. 0. 0. 0
REM  Fileversion:  0. 0. 0. 0
REM  Internalname: 
REM  Appicon: 
REM  QBFC Project Options End

@echo off
time /t  >> bat.log
@echo %0 %*>>bat.log


if "%6" == "" goto short
@echo d:\test\tools\adb\adb1.exe %* > tmp.bat
call tmp.bat
goto end

:short
call d:\test\tools\adb\adb1.exe %1 %2 %3 %4 %5 %6 %7 %8 %9


:endi
rem @exit /b %errorlevel%
