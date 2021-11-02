import os
import random
import re
import time

import chardet
import mutagen.mp3
import psutil
import pygame
import pypinyin


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
    if os.name == 'nt':
        tmp = os.path.split(path)
        return tmp[0][:-1] if tmp[0] == path else tmp[1]
    else:
        return os.path.split(path)[1]


class Player:
    """
    音乐播放器。
    """

    file: str = ''
    offset: float = 0
    length: float = 0
    rate: float = 1
    playing: bool = False
    delay: float = 0.02
    precision: float = 0.1

    def open(self, file: str) -> None:
        """
        打开文件。
        """
        try:
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

        except Exception as e:
            raise Exception(f'打开文件 {file} 失败:' + str(e))

    def play(self) -> None:
        """
        播放。
        """
        if self.file:
            pygame.mixer.music.unpause()
            self.playing = True

    def pause(self) -> None:
        """
        暂停。
        """
        if self.file:
            pygame.mixer.music.pause()
            self.playing = False

    def replay(self) -> None:
        """
        从头播放。
        """
        pygame.mixer.music.stop()
        self.offset = 0
        pygame.mixer.music.play()

    def get_pos(self) -> float:
        """
        获取当前播放位置 (单位:秒)。
        """
        return pygame.mixer.music.get_pos() / 1000 + self.offset

    def set_pos(self, pos: float) -> None:
        """
        设置当前播放位置 (单位:秒)。
        """
        if self.file:
            pos = min(max(pos, 0), self.length)
            pygame.mixer.music.set_pos(pos * self.rate)
            self.offset = pos - pygame.mixer.music.get_pos() / 1000

    def get_prog(self) -> float:
        """
        获取当前播放进度。
        """
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

    def open(self, file: str) -> None:
        """
        打开文件。
        """
        for line in autodecode(open(file, 'rb').read()).split('\n'):
            data = re.search('(.*)\\](.*)', line)
            if data:
                word = data.group(2).strip()
                for t in re.findall('\\[([0-9.:]*)\\]', line):
                    self.lrc[self.time2sec(t)] = word
        self.mark = sorted(self.lrc.keys())

    def time2sec(self, time: str) -> float:
        """
        将“分:秒”形式的时间转换成秒数。
        """
        m, s = time.split(':')
        return int(m) * 60 + float(s)

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


class Item:
    """
    文件浏览器中的项。
    """

    name: str = ''
    icon: str = ''
    onclick = None
    param = None
    onclick2 = None
    param2 = None

    def __init__(self, name: str, icon: str, onclick, param, onclick2=None, param2=None) -> None:
        self.name = name
        self.icon = icon
        self.onclick = onclick
        self.param = param
        self.onclick2 = onclick2
        self.param2 = param2

    def __call__(self):
        self.onclick(self.param)
        if self.onclick2:
            self.onclick2(self.param2)


class Viewer:
    """
    文件浏览器。
    """

    player: Player = None
    lrc: Lrc = None
    mode: int = 0
    playlist: list = []
    showitems: list = []
    id: int = 0
    viewid: int = 0
    path: str = ''

    def __init__(self, player: Player, lrc: Lrc) -> None:
        self.player = player
        self.lrc = lrc
        if os.name == 'nt':
            self.path = ''
        else:
            self.path = '/'
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
            if path == '':
                self.showitems = sorted([Item(i.device, 'disk', self.open, i.device)
                                        for i in psutil.disk_partitions()], key=sortby)
            else:
                dirs = []
                files = []

                def add_item(path):
                    if os.path.isdir(path):
                        dirs.append(
                            Item(filename(path), 'folder', self.open, path))
                    elif path.endswith('.mp3'):
                        files.append(
                            Item(filename(path)[:-4], 'music', self.play, path, self.setid))

                if os.name == 'nt':
                    for i in os.popen(f'attrib /d "{path}"\\*').read().splitlines():
                        properties = i[:21]
                        name = i[21:]
                        if 'S' not in properties:
                            add_item(name)
                else:
                    for i in os.listdir(path):
                        if not i.startswith('.'):
                            add_item(os.path.join(path, i))

                dirs.sort(key=sortby)
                files.sort(key=sortby)
                for i, item in enumerate(files):
                    item.param2 = i
                self.showitems = dirs+files
            self.path = path
            self.viewid = 0
        except Exception as e:
            raise Exception('无法打开文件夹:'+str(e))

    def father(self) -> None:
        """
        返回上一级目录。
        """
        if os.name == 'nt' and self.path == fatherpath(self.path):
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
        播放音乐并更新播放列表。
        """
        self.playlist = [
            i.param for i in self.showitems if i.onclick == self.play]
        self.player.open(os.path.join(self.path, name))
        self.lrc.clear()
        if os.path.isfile(os.path.join(self.path, name[:-4] + '.lrc')):
            self.lrc.open(os.path.join(self.path, name[:-4] + '.lrc'))

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
            if self.mode == 2:
                last = self.id
                while last == self.id:
                    last = random.randrange(len(self.playlist))
                self.id = last
                self.play(self.playlist[self.id])
            else:
                self.id = (self.id - 1) % len(self.playlist)
                self.play(self.playlist[self.id])

    def next(self) -> None:
        """
        下一首。
        """
        if self.playlist:
            if self.mode == 2:
                next = self.id
                while next == self.id:
                    next = random.randrange(len(self.playlist))
                self.id = next
                self.play(self.playlist[self.id])
            else:
                self.id = (self.id + 1) % len(self.playlist)
                self.play(self.playlist[self.id])

    def end(self) -> None:
        """
        接受到 pygame.USEREVENT 事件时调用此方法。
        """
        if self.mode == 1:
            self.player.replay()
        else:
            self.next()
