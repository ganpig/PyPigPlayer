@echo off
title PyPigPlayer Builder
set /p ver=Input Version: 

title Upgrading packages
pip install --upgrade pip autopep8 chardet mutagen pygame pyinstaller

title Formatting code
autopep8 -i -a main.py core.py ui.py

title Building exe
pyinstaller -F -i logo.ico -w -n PyPigPlayer --distpath PyPigPlayer\ main.py

title Removing temporary files
rd /s /q build
rd /s /q __pycache__
del PyPigPlayer.spec

title Copying program files
xcopy theme PyPigPlayer\theme /e /h /c /i
copy theme.txt PyPigPlayer\

title Compressing program folder
7z a archive\%ver%\PyPigPlayer_%ver%_portable.zip PyPigPlayer

title Done
pause