@echo off
pyinstaller -F main.py -w -n PyPigPlayer
rd /s /q build
rd /s /q __pycache__
del PyPigPlayer.spec
xcopy font dist\font /e /h /c /i
xcopy img dist\img /e /h /c /i
::xcopy tool dist\tool /e /h /c /i
copy settings.ini dist\
ren dist PyPigPlayer
pause