@echo off
rd /s /q Building
rd /s /q Sources\PyPigPlayer\__pycache__
md Building\PyPigPlayer
xcopy Resources\Python Building\PyPigPlayer\Python /e /h /c /i
rd /s /q Building\PyPigPlayer\Python\Include
rd /s /q Building\PyPigPlayer\Python\Scripts
rd /s /q Building\PyPigPlayer\Python\share
xcopy Sources\Themes Building\PyPigPlayer\Themes /e /h /c /i
xcopy Sources\Fonts Building\PyPigPlayer\Fonts /e /h /c /i
xcopy Sources\Tools Building\PyPigPlayer\Tools /e /h /c /i
copy Sources\config.ini Building\PyPigPlayer\
copy Resources\Starter\PyPigPlayer.exe Building\PyPigPlayer\
python -m zipapp Sources\PyPigPlayer -c -m "main:main" -o Building\PyPigPlayer\PyPigPlayer.pyz
pause