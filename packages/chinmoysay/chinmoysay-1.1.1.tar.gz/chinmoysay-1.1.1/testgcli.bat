@echo off
cd /d "%~dp0"
python -m chinmoysay.main %*



@REM Now you have to go to "View Advanced system settings"
@REM and in "environment variables", add new path --> path of the directory your batch file is present.