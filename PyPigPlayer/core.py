import _thread
import hashlib
import os
import random
import re
import shutil
import time
import traceback

import chardet
import easygui
import mutagen.mp3
import psutil
import pygame
import pypinyin

import web
from init import *


def autodecode(data: bytes) -> str:
    """
    自动识别编码并解码 bytes 类型数据。
    """
    encoding = chardet.detect(data)['encoding']
    return data.decode(encoding, errors='ignore') if encoding else ''


def fatherpath(path: str) -> str:
    """
    获取路径的上一级目录。
    """
    return os.path.split(path)[0]


def filename(path: str) -> str:
    """
    获取文件名。
    """
    tmp = os.path.split(path)
    return tmp[0][:-1] if tmp[0] == path else tmp[1]


def convert_mp3(file: str, target: str) -> None:
    """
    将音乐文件转换为 MP3 格式。
    """
    try:
        info.set('正在转换文件格式……')
        if not os.path.isdir(temp):
            os.makedirs(temp)
        if os.system(f'{ffmpeg} -v 0 -y -i \"{file}\" -f mp3 \"{target}\"') or not os.path.isfile(target):
            raise Exception()
        info.clear()

    except:
        info.clear()
        traceback.print_exc()
        err.set('转换文件格式失败!')


def mp3path(file: str) -> str:
    """
    获取文件对应的缓存路径。
    """
    if file.endswith('.mp3'):
        return file
    else:
        hash = hashlib.md5(open(file, 'rb').read()).hexdigest()
        target = os.path.join(temp, hash+'.mp3')
        if not os.path.isfile(target):
            convert_mp3(file, target)
        return target


def urlpath(url: str, type: str = '') -> str:
    """
    获取 URL 在本地缓存路径。
    """
    try:
        info.set('正在从网络获取数据……')
        if not os.path.isdir(temp):
            os.makedirs(temp)
        target = os.path.join(temp, hashlib.md5(
            url.encode('utf-8')).hexdigest()+type)
        if not os.path.isfile(target):
            open(target, 'wb').write(web.get(url))
        info.clear()
        return target
    except Exception as e:
        info.clear()
        raise e


class Player:
    """
    音乐播放器
    """

    file: str = ''
    offset: float = 0
    length: float = 0
    rate: float = 1
    playing: bool = False
    ready: bool = False
    delay: float = 0.02
    precision: float = 0.1
    fadeout: float = 0.5

    def open(self, file: str) -> None:
        """
        打开文件。
        """
        try:
            info.set('正在加载文件……')
            self.ready = False
            pygame.mixer.music.load(file)
            self.file = file
            self.offset = 0

            # 获取 Pygame 音乐时长以计算比率
            def check(length):
                pygame.mixer.music.play()
                pygame.mixer.music.set_pos(length)
                time.sleep(self.delay)
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                    return True
                else:
                    return False

            # 设置音量与结束事件
            vol_bak = pygame.mixer.music.get_volume()
            pygame.mixer.music.set_volume(0)
            pygame.mixer.music.set_endevent(0)

            l = 0
            r = 1.0
            # 倍增求上界
            while check(r):
                l = r
                r *= 2
            # 二分求时长
            while l + self.precision < r:
                mid = (l + r) / 2
                if check(mid):
                    l = mid
                else:
                    r = mid

            self.length = mutagen.mp3.MP3(self.file).info.length
            self.rate = l / self.length

            # 还原音量与结束事件
            pygame.mixer.music.set_volume(vol_bak)
            pygame.mixer.music.set_endevent(pygame.USEREVENT)
            pygame.mixer.music.play()
            self.playing = True
            self.ready = True

            info.clear()

        except Exception as e:
            info.clear()
            traceback.print_exc()
            err.set(f'打开文件 {file} 失败:' + str(e))

    def close(self) -> None:
        """
        关闭正在播放的文件。
        """
        pygame.mixer.music.stop()
        self.playing = False

    def play(self) -> None:
        """
        播放。
        """
        if self.ready:
            pygame.mixer.music.unpause()
            self.playing = True

    def pause(self) -> None:
        """
        暂停。
        """
        if self.ready:
            self.playing = False
            pos_bak = self.get_pos()
            pygame.mixer.music.fadeout(int(self.fadeout*1000))
            time.sleep(self.fadeout)
            pygame.mixer.music.play()
            pygame.mixer.music.pause()
            self.set_pos(pos_bak+self.fadeout)

    def replay(self) -> None:
        """
        从头播放。
        """
        pygame.mixer.music.stop()
        self.offset = 0
        pygame.mixer.music.play()
        self.playing = True

    def get_pos(self) -> float:
        """
        获取当前播放位置 (单位:秒)。
        """
        while not self.ready:
            pass
        return pygame.mixer.music.get_pos() / 1000 + self.offset

    def set_pos(self, pos: float) -> None:
        """
        设置当前播放位置 (单位:秒)。
        """
        if self.ready:
            pos = min(max(pos, 0), self.length)
            pygame.mixer.music.set_pos(pos * self.rate)
            self.offset = pos - pygame.mixer.music.get_pos() / 1000

    def get_prog(self) -> float:
        """
        获取当前播放进度。
        """
        while not self.ready:
            pass
        return self.get_pos() / self.length

    def set_prog(self, prog: float) -> float:
        """
        设置当前播放进度。
        """
        self.set_pos(self.length * prog)

    def get_text(self) -> str:
        """
        获取进度条文字。
        """
        while not self.ready:
            pass
        return '/'.join(map((lambda s: '{:0>2d}:{:0>2d}'.format(
            *divmod(int(s), 60))), (self.get_pos(), self.length)))


class Volume:
    """
    音量设置。
    """

    volume: float = 0.65

    def get_volume(self) -> float:
        """
        获取音量 (0~1之间)。
        """
        return self.volume

    def set_volume(self, vol: float) -> None:
        """
        设置音量 (0~1之间)。
        """
        self.volume = min(max(vol, 0), 1)
        pygame.mixer.music.set_volume(self.volume)

    def get_text(self) -> str:
        """
        获取音量百分比文本。
        """
        return f'音量{int(self.volume*100)}%'


class Timer:
    """
    定时关闭。
    """

    player: Player = None
    end: float = 0
    max: int = 7200

    def __init__(self, player: Player) -> None:
        self.player = player

    def get_time(self) -> float:
        """
        获取剩余时间。
        """
        if self.end < time.time():
            if self.end > time.time() - 1:
                self.player.pause()
            return 0
        else:
            return self.end - time.time()

    def set_time(self, sec: float) -> None:
        """
        设置剩余时间。
        """
        self.end = 0 if sec < 60 else time.time() + min(self.max, sec)

    def get_prog(self) -> float:
        """
        获取剩余时间与最大时间的比值。
        """
        return self.get_time() / self.max

    def set_prog(self, prog: float) -> None:
        """
        设置剩余时间与最大时间的比值。
        """
        self.set_time(prog * self.max)

    def get_text(self) -> str:
        """
        获取定时器文本。
        """
        if self.end < time.time():
            return '定时已关闭'
        else:
            return f'定时{int((self.end-time.time())/60)+1}min'


class Lrc:
    """
    滚动歌词。
    """

    lrc: dict = {}
    mark: list = []

    def clear(self) -> None:
        """
        清除歌词。
        """
        self.lrc = {}
        self.mark = []

    def open(self, lrc: str) -> None:
        """
        打开文件。
        """
        for line in lrc.splitlines():
            data = re.search('(.*)\\](.*)', line)
            if data:
                word = data.group(2).strip()
                for t in re.findall('\\[([0-9.:]*)\\]', line):
                    sec = self.time2sec(t)
                    self.lrc[sec] = word
        self.mark = sorted(self.lrc.keys())

    def time2sec(self, time: str) -> float:
        """
        将时间字符串转换成秒数。
        """
        time = time.split(':')
        if len(time) == 2:
            h = 0
            m, s = time
        else:
            h, m, s = time
        return int(h)*3600+int(m) * 60 + float(s)

    def get_lrc_id(self, sec: float) -> int:
        """
        获取指定时间的歌词编号。
        """
        id = -1
        while id < len(self.mark) - 1 and self.mark[id + 1] <= sec:
            id += 1
        return id

    def get_lrc(self, id: int) -> str:
        """
        获取指定编号的歌词。
        """
        return self.lrc[self.mark[id]] if 0 <= id < len(self.mark) else ''

    def get_mark(self, id: int) -> float:
        """
        获取指定编号的时间，
        """
        return self.mark[id] if 0 <= id < len(self.mark) else float('inf')


class Item:
    """
    文件浏览器中的项。
    """

    name: str = ''
    icon: str = ''
    onclicks: tuple = ()

    def __init__(self, name: str, icon: str, *args) -> None:
        self.name = name
        self.icon = icon
        self.onclicks = args

    def __call__(self) -> None:
        for onclick, param, newthread in self.onclicks:
            if newthread:
                _thread.start_new_thread(onclick, (param,))
            else:
                onclick(param)


class Viewer:
    """
    文件浏览器。
    """

    player: Player = None
    lrc: Lrc = None
    urltemp: str = ''
    lrctemp: str = ''
    mode: int = 0
    playlist: list = []
    showitems: list = []
    id: int = 0
    viewid: int = 0
    path: str = ''
    playing: str = '未打开文件'
    playing2: str = ''
    search_mode: bool = False
    search_key: str = ''

    def __init__(self, player: Player, lrc: Lrc) -> None:
        self.player = player
        self.lrc = lrc
        self.open(self.path)

    def open(self, path: str) -> None:
        """
        打开文件夹。
        """
        def sortby(item):
            ret = []
            for c in item.name:
                pinyin = pypinyin.lazy_pinyin(c)
                if pinyin[0] != c:
                    ret.append('\uffff'+pinyin[0])
                else:
                    ret.append(c.lower())
            return ret

        try:
            info.set('正在加载文件夹……')
            if path == '':
                self.showitems = sorted([Item(i.device, 'disk', (self.open, i.device, False))
                                        for i in psutil.disk_partitions()], key=sortby)
            else:
                all = set((os.path.join(path, i) for i in os.listdir(path)))
                for i in os.popen(f'attrib /d "{path}"\\*').read().splitlines():
                    properties = i[:21]
                    name = i[21:]
                    if 'S' in properties and name in all:
                        all.remove(name)
                dirs = []
                files = []
                for i in all:
                    if os.path.isdir(i):
                        dirs.append(
                            Item(filename(i), 'folder', (self.open, i, False)))
                    else:
                        for j in supported_formats:
                            if i.endswith('.'+j):
                                files.append(
                                    Item(filename(i), 'music', (self.play, i, True), [self.setid, 0, False]))
                dirs.sort(key=sortby)
                files.sort(key=sortby)
                for i, item in enumerate(files):
                    item.onclicks[1][1] = i
                self.showitems = dirs+files
            self.path = path
            self.viewid = 0
            info.clear()

        except Exception as e:
            info.clear()
            traceback.print_exc()
            err.set('无法打开文件夹:'+str(e))

    def search_online(self) -> None:
        """
        加载搜索结果。
        """
        tmp = []
        data = web.search(self.search_key)
        if data:
            i = 0
            for music in data:
                if music.vip:
                    tmp.append(Item('[VIP]'+music.singer +
                                    ' - '+music.name, music._, (os.system, 'start '+music.url, False)))
                else:
                    tmp.append(Item(music.singer+' - '+music.name, music._, (self.play_online, music, True),
                                    (self.setid, i, False)))
                    i += 1
            self.showitems = tmp
            self.search_mode = True
            self.viewid = 0

    def save(self) -> None:
        """
        保存当前歌曲。
        """
        savepath = easygui.filesavebox('选择保存路径', title, os.path.expanduser(
            '~\\desktop\\')+self.playing+'.mp3', '*.mp3')
        if savepath:
            try:
                shutil.copy(self.urltemp, savepath)
                if self.lrctemp:
                    with open(savepath[:-4]+'.lrc', 'w') as f:
                        f.write(self.lrctemp)
                msg.set('保存音乐成功!')
            except Exception as e:
                err.set('保存音乐失败:'+str(e))

    def father(self) -> None:
        """
        返回上一级目录。
        """
        if self.search_mode:
            self.search_mode = False
            self.lrc.clear()
            self.player.close()
            self.playing = '未打开文件'
            self.playing2 = ''
            self.open(self.path)
        elif self.path == fatherpath(self.path):
            self.open('')
        else:
            self.open(fatherpath(self.path))

    def switch(self, mode: int) -> None:
        """
        切换循环模式 (0:顺序播放, 1:单曲循环, 2:随机播放)。
        """
        self.mode = mode

    def play(self, name: str) -> None:
        """
        播放音乐。
        """
        self.playlist = [
            i.onclicks[0][1] for i in self.showitems if i.onclicks[0][0] == self.play]
        self.player.open(mp3path(os.path.join(self.path, name)))
        self.lrc.clear()
        if os.path.isfile(os.path.join(self.path, os.path.splitext(name)[0] + '.lrc')):
            lrcpath = os.path.join(
                self.path, os.path.splitext(name)[0] + '.lrc')
            self.lrc.open(autodecode(open(lrcpath, 'rb').read()))
        self.playing = filename(os.path.join(self.path, name))
        self.playing2 = os.path.join(self.path, name)

    def play_online(self, music: web.Music) -> None:
        """
        播放网络上的音乐。
        """
        try:
            self.playlist = [
                i.onclicks[0][1] for i in self.showitems if i.onclicks[0][0] == self.play_online]
            self.urltemp = mp3path(
                urlpath(web.link(music), '.mp3' if music._ == 'netease' else '.m4a'))
            self.lrctemp = web.lrc(music)
            self.player.open(self.urltemp)
            self.lrc.clear()
            self.lrc.open(self.lrctemp)
            self.playing = music.singer+' - '+music.name
            self.playing2 = music.url
        except Exception as e:
            traceback.print_exc()
            err.set('在线播放音乐出错:'+str(e))

    def setid(self, id: int) -> None:
        """
        设置当前音乐在播放列表中的位置。
        """
        self.id = id

    def last(self) -> None:
        """
        上一首。
        """
        if self.playlist:
            play = self.play if not self.search_mode else lambda x: _thread.start_new_thread(
                self.play_online, (x,))
            if self.mode == 2:
                last = self.id
                while last == self.id:
                    last = random.randrange(len(self.playlist))
                self.id = last
                play(self.playlist[self.id])
            else:
                self.id = (self.id - 1) % len(self.playlist)
                play(self.playlist[self.id])

    def next(self) -> None:
        """
        下一首。
        """
        if self.playlist:
            play = self.play if not self.search_mode else lambda x: _thread.start_new_thread(
                self.play_online, (x,))
            if self.mode == 2:
                next = self.id
                while next == self.id:
                    next = random.randrange(len(self.playlist))
                self.id = next
                play(self.playlist[self.id])
            else:
                self.id = (self.id + 1) % len(self.playlist)
                play(self.playlist[self.id])

    def end(self) -> None:
        """
        接受到 pygame.USEREVENT 事件时调用此方法。
        """
        if self.player.playing:
            if self.mode == 1:
                self.player.replay()
            else:
                self.next()
