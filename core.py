import os
import random
import re
import time

import chardet
import easygui
import mutagen.mp3
import pygame
import pypinyin

from main import title


def autodecode(data: bytes) -> str:
    """
    自动识别编码并解码 bytes 类型数据。
    """
    encoding = chardet.detect(data)['encoding']
    return data.decode(encoding, errors='ignore') if encoding else ''


class Player:
    """
    音乐播放器。
    """

    def __init__(self) -> None:
        self.file = None
        self.offset = 0
        self.length = 0
        self.rate = 1
        self.playing = False

        # 获取 Pygame 音乐时长时的延时和精度
        self.delay = 0.02
        self.precision = 0.1

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
            easygui.msgbox(f'打开文件 {file} 失败:\n{e}', title)

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

    def __init__(self) -> None:
        self.volume = 0.65

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

    def __init__(self, player: Player) -> None:
        self.player = player
        self.end = 0

        # 定时最大时间
        self.max = 7200

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

    def __init__(self) -> None:
        self.lrc = {}
        self.mark = []

    def open(self, file: str) -> None:
        self.lrc = {}
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


class Viewer:
    """
    文件浏览器。
    """

    def __init__(self, player: Player, lrc: Lrc) -> None:
        self.player = player
        self.lrc = lrc
        self.mode = 0
        self.path = None
        self.items = []
        self.id = 0
        self.viewid = 0
        self.lastpath = os.path.expanduser('~/desktop')

    def open(self) -> None:
        """
        使用系统对话框让用户打开文件夹。
        """
        path = easygui.diropenbox('打开文件夹', title, self.lastpath)
        if path:
            self.path = path
            self.lastpath = os.path.sep.join(path.split(os.path.sep)[:-1])
            self.items = sorted([i[:-4] for i in os.listdir(path)if i.endswith(
                '.mp3') and os.path.isfile(os.path.join(path, i))], key=lambda x: pypinyin.lazy_pinyin(x))
            self.id = 0
            self.viewid = 0

    def switch(self, mode: int) -> None:
        """
        切换循环模式 (0:顺序播放, 1:单曲循环, 2:随机播放)。
        """
        self.mode = mode

    def play(self, name: str) -> None:
        self.player.open(os.path.join(self.path, name + '.mp3'))
        if os.path.isfile(os.path.join(self.path, name + '.lrc')):
            self.lrc.open(os.path.join(self.path, name + '.lrc'))

    def playid(self, id: int) -> None:
        self.id = id
        self.play(self.items[id])

    def next(self) -> None:
        if self.items:
            if self.mode == 2:
                next = self.id
                while next == self.id:
                    next = random.randrange(len(self.items))
                self.id = next
                self.play(self.items[self.id])
            else:
                self.id = (self.id + 1) % len(self.items)
                self.play(self.items[self.id])

    def last(self) -> None:
        if self.items:
            if self.mode == 2:
                last = self.id
                while last == self.id:
                    last = random.randrange(len(self.items))
                self.id = last
                self.play(self.items[self.id])
            else:
                self.id = (self.id - 1) % len(self.items)
                self.play(self.items[self.id])

    def end(self) -> None:
        """
        接受到 pygame.USEREVENT 事件时调用此方法。
        """
        if self.mode == 1:
            self.player.replay()
        else:
            self.next()
