@echo off
title PyPigPlayer Builder
set /p ver=Input Version: 

title Upgrading pip 0%%
pip install --upgrade pip

title Upgrading autopep8 5%%
pip install --upgrade autopep8

title Upgrading chardet 10%%
pip install --upgrade chardet

title Upgrading easygui 15%%
pip install --upgrade easygui

title Upgrading mutagen 20%%
pip install --upgrade mutagen

title Upgrading pygame 25%%
pip install --upgrade pygame

title Upgrading pyinstaller 30%%
pip install --upgrade pyinstaller

title Upgrading pywin32 35%%
pip install --upgrade pywin32

title Formatting main.py 40%%
autopep8 -i -a -a -a -a -a main.py

title Formatting ppp_button.py 45%%
autopep8 -i -a -a -a -a -a ppp_button.py

title Formatting ppp_config.py 50%%
autopep8 -i -a -a -a -a -a ppp_config.py

title Formatting ppp_file.py 55%%
autopep8 -i -a -a -a -a -a ppp_file.py

title Formatting ppp_func.py 60%%
autopep8 -i -a -a -a -a -a ppp_func.py

title Formatting ppp_player.py 65%%
autopep8 -i -a -a -a -a -a ppp_player.py

title Formatting ppp_text.py 70%%
autopep8 -i -a -a -a -a -a ppp_text.py

title Formatting ppp_window.py 75%%
autopep8 -i -a -a -a -a -a ppp_window.py

title Building PyPigPlayer.exe 80%%
pyinstaller -F -i img/logo.ico -w -n PyPigPlayer --distpath PyPigPlayer\ main.py

title Removing temporary files 85%%
rd /s /q build
rd /s /q __pycache__
del PyPigPlayer.spec

title Copying program files 90%%
xcopy font PyPigPlayer\font /e /h /c /i
xcopy img PyPigPlayer\img /e /h /c /i
copy config.ini PyPigPlayer\

title Compressing program folder 95%%
7z a archive\%ver%\PyPigPlayer_%ver%_portable.zip PyPigPlayer

title Done 100%%
pause