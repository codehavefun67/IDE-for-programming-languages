@echo off
echo.
set /p file=Type the file name:
set /p out=Type output name:
where g++
if %errorlevel% equ 0
(
  echo [SYSTEM] G++ installed! Compiling...
  g++ -o %out% %file%
) else (
  echo.
  echo [SYSTEM] G++ is not installed!
)
echo.
echo Press any key to continue...
pause >nul 2>nul