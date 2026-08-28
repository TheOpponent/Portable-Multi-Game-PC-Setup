@echo off
@setlocal
nircmd setcursor 1920 0

for /f %%G in ('powershell -NoProfile -Command "(Start-Process -FilePath 'pythonw.exe' -ArgumentList '%USERPROFILE%\Desktop\Lutero\input_monitor.pyw' -PassThru).Id"') do set PID=%%G

:: Set these variables accordingly.
:: gameName must equal the name of a corresponding image file (without extension) 
:: in the digital sign's asset collection, case sensitive.
set "gameName=Game Name"
set "basePath=%USERPROFILE%\Desktop\Lutero"
set "logPath=%USERPROFILE%\Desktop\log.txt"
set "exitPath=%basePath%\exit.bat"
(
	echo @echo off
	:: Remove this line if you don't wish to keep logs.
    echo echo %%date%% %%time%% - Stopped ^>^> %logPath%
	
	echo taskkill /f /pid %PID%
	echo "%basePath%\update.pyw"
	:: Change the argument of taskkill to the image name of the executable of the game.
	:: Add additional `echo taskkill /f /im` lines if more than one executable is launched.
	echo taskkill /f /im game.exe
	::
	echo del %%~f0
) > %exitPath%

:: Remove this line if you don't wish to keep logs.
echo %date% %time% - %gameName% >> %logPath%

"%basePath%\update.pyw" "%gameName%"
"%basePath%\wallpaper.pyw"
:: This line stalls for 2 seconds, so the pre-launch message can be seen. You may wish to remove this line if the game has a naturally long launch time.
ping -n 3 127.0.0.1 >nul

nircmd win hide class Shell_TrayWnd

:: Add commands to launch the game below this line.

