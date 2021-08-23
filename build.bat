@echo off
pyinstaller -F -i img/logo.ico -w -n PyPigPlayer --distpath PyPigPlayer\ main.py 
rd /s /q build
del PyPigPlayer.spec
xcopy font PyPigPlayer\font /e /h /c /i
xcopy img PyPigPlayer\img /e /h /c /i
copy config.ini PyPigPlayer\
7z a PyPigPlayer_v1.0_portable.zip PyPigPlayer