import hashlib
import os
import re
import subprocess
import threading

import web
from init import *

if is_windows:
    import win32api
    import win32con


def convert_mp3(file: str, target: str) -> None:
    """
    将音乐文件转换为 MP3 格式。
    """
    info.set('正在转换文件格式……')
    try:
        assert subprocess.call(
            [os.path.join(Tools, 'ffmpeg.exe'), '-v', '0', '-y', '-i', file, '-f', 'mp3', target], creationflags=0x08000000) == 0
        assert os.path.isfile(target)

    except:
        raise Exception('转换文件格式失败!')

    finally:
        info.clear()


def desktop() -> str:
    if is_windows:
        key = win32api.RegOpenKey(
            win32con.HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders', 0, win32con.KEY_READ)
        return win32api.RegQueryValueEx(key, 'Desktop')[0]
    else:
        return os.popen('eval echo `cat $HOME/.config/user-dirs.dirs|grep DESKTOP|tail -1|cut -d\'=\' -f 2|sed \'s/\\\"//g\'`').read().strip()


def dirname(path: str) -> str:
    """
    获取路径的上一级目录。
    """
    return os.path.abspath(os.path.split(path)[0])


def ext(file: str) -> str:
    """
    获取文件拓展名。
    """
    return os.path.splitext(file)[1]


def filebasename(name: str) -> str:
    """
    获取除去拓展名的文件名。
    """
    return os.path.splitext(filename(name))[0]


def filename(path: str) -> str:
    """
    获取文件名。
    """
    tmp = os.path.split(path)
    return tmp[0][:-1] if tmp[0] == path else tmp[1]


def lrcpath(file: str) -> str:
    """
    获取对应歌词文件路径。
    """
    return os.path.splitext(file)[0]+'.lrc'


def makefilename(name:str)->str:
    """
    规范化文件名。
    """
    return re.sub(r'[\/\\\:\*\?\"\<\>\|]', '_', name)

def mp3path(file: str) -> str:
    """
    获取文件对应的缓存路径。
    """
    if ext(file) == '.mp3':
        return file
    else:
        hash = hashlib.md5(open(file, 'rb').read()).hexdigest()
        target = os.path.join(Temp, hash+'.mp3')
        if not os.path.isfile(target):
            convert_mp3(file, target)
        return target


def musicpath(music: web.Music) -> str:
    """
    获取音乐缓存路径。
    """
    hash = hashlib.md5(music.url.encode('utf-8')).hexdigest()
    dl_path = os.path.abspath(os.path.join(
        Temp, hash+('.mp3' if music._ == 'netease' else '.m4a')))
    target = os.path.abspath(os.path.join(Temp, hash+'.mp3'))

    if os.path.isfile(target):
        return target

    else:
        try:
            link = web.link(music)
            info.set('正在下载数据……')
            open(dl_path, 'wb').write(web.get(link))

        except Exception as e:
            raise e

        finally:
            info.clear()

        if ext(dl_path) == '.m4a':
            convert_mp3(dl_path, target)
        return target


def start_thread(func, *args, **kwargs):
    threading.Thread(target=func, args=args,
                     kwargs=kwargs, daemon=True).start()
