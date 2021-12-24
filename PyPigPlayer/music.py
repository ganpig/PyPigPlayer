import re
import time
import traceback

import mutagen.mp3
import pygame

import popup
from init import *


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

    def get_lrc(self, id: int) -> str:
        """
        获取指定编号的歌词。
        """
        return self.lrc[self.mark[id]] if 0 <= id < len(self.mark) else ''

    def get_lrc_id(self, sec: float) -> int:
        """
        获取指定时间的歌词编号。
        """
        id = -1
        while id < len(self.mark) - 1 and self.mark[id + 1] <= sec:
            id += 1
        return id

    def get_mark(self, id: int) -> float:
        """
        获取指定编号的时间，
        """
        return self.mark[id] if 0 <= id < len(self.mark) else float('inf')

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


class Player:
    """
    音乐播放器
    """

    delay: float = 0.02
    fadeout: float = 0.5
    file: str = ''
    length: float = 0
    offset: float = 0
    opening: bool = False
    playing: bool = False
    precision: float = 0.1
    rate: float = 1
    ready: bool = False

    def close(self) -> None:
        """
        关闭正在播放的文件。
        """
        pygame.mixer.music.unload()
        self.file = ''
        self.playing = False
        self.ready = False
        self.length = 0

    def get_pos(self) -> float:
        """
        获取当前播放位置 (单位:秒)。
        """
        return pygame.mixer.music.get_pos() / 1000 + self.offset if self.ready else 0

    def get_prog(self) -> float:
        """
        获取当前播放进度。
        """
        return self.get_pos() / self.length if self.length else 0

    def get_text(self) -> str:
        """
        获取进度条文字。
        """
        return '/'.join(map((lambda s: '{:0>2d}:{:0>2d}'.format(
            *divmod(int(s), 60))), (self.get_pos(), self.length)))

    def open(self, file: str) -> None:
        """
        打开文件。
        """
        if not self.opening:
            info.set('正在打开文件……')
            try:
                self.opening = True
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
                self.opening = False

            except Exception as e:
                traceback.print_exc()
                err.set(f'打开文件失败:' + str(e))

            finally:
                info.clear()

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

    def play(self) -> None:
        """
        播放。
        """
        if self.ready:
            pygame.mixer.music.unpause()
            self.playing = True

    def replay(self) -> None:
        """
        从头播放。
        """
        pygame.mixer.music.stop()
        self.offset = 0
        pygame.mixer.music.play()
        self.playing = True

    def set_pos(self, pos: float) -> None:
        """
        设置当前播放位置 (单位:秒)。
        """
        if self.ready:
            pos = min(max(pos, 0), self.length)
            pygame.mixer.music.set_pos(pos * self.rate)
            self.offset = pos - pygame.mixer.music.get_pos() / 1000

    def set_prog(self, prog: float) -> float:
        """
        设置当前播放进度。
        """
        self.set_pos(self.length * prog)


class Timer:
    """
    定时关闭。
    """

    end: float = 0
    player: Player = None
    setting: bool = False
    total: float = float('-inf')

    def __init__(self, player: Player) -> None:
        self.player = player

    def get_prog(self) -> float:
        """
        获取剩余时间与最大时间的比值。
        """
        return self.get_time() / self.total

    def get_text(self) -> str:
        """
        获取定时器文本。
        """
        if self.end < time.time():
            return '定时器已关闭'
        else:
            return f'定时剩余 {int((self.end-time.time())/60)+1} 分钟'

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

    def set(self) -> None:
        """
        设置定时器。
        """
        if not self.setting:
            self.setting = True
            ch = popup.choose('请选择多长时间后关闭', '设置定时器', list(Timer_Time.keys()),
                              list(Timer_Time.values()).index(self.total))
            if ch:
                self.total = Timer_Time[ch]
                self.end = time.time()+self.total
            self.setting = False


class Volume:
    """
    音量设置。
    """

    volume: float = 0.65

    def __init__(self) -> None:
        pygame.mixer.music.set_volume(self.volume)

    def get_text(self) -> str:
        """
        获取音量百分比文本。
        """
        return f'音量{int(self.volume*100)}%'

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
