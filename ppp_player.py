import pygame
from _thread import start_new_thread
from easygui import fileopenbox, diropenbox
from json import loads
from mutagen.mp3 import MP3
from os.path import exists, expanduser
from ppp_func import *
from time import time, sleep
from traceback import format_exc
from urllib.parse import quote
from urllib.request import urlopen


class Player:
    def __init__(self):
        self.music_file = None
        self.music_list = []
        self.music_total_time = 0
        self.music_offset_time = 0
        self.lrc_dic = None
        self.lrc_marks = None
        self.lrc_id = 0
        self.lrc_url = -1
        self.lrc_current_mark = 0
        self.timer = False
        self.timer_start_time = 0
        self.timer_set_time = 0
        self.repeat_mode = 0
        self.message_cnt = 0
        self.message = None
        self.state = None
        self.volume = 50
        self.set_vol(self.volume)
        pygame.mixer.music.set_endevent(pygame.USEREVENT)
        start_new_thread(self.update_lrc, tuple())

    def opened(self):
        return True if self.music_file else False

    def open_file(self, btn, file):
        try:
            self.music_file = file
            pygame.mixer.music.load(self.music_file)
            self.music_total_time = int(
                MP3(self.music_file).info.length * 1000)
            self.music_offset_time = 0
            self.lrc_id = 0
            self.lrc_url = -1
            pygame.mixer.music.play()
            btn.set_img('pause')
        except Exception as e:
            self.music_file = None
            self.error('打开失败:' + repr(e), format_exc())

        try:
            lrcfile = self.music_file[:-3] + 'lrc'
            if exists(lrcfile):
                with open(lrcfile, 'rb') as f:
                    self.lrc_dic = parse_lrc(auto_decode(f.read()).split('\n'))
                    self.lrc_marks = sorted(self.lrc_dic.keys())
                    self.lrc_current_mark = 0
            else:
                self.lrc_marks = None
        except Exception as e:
            self.error('加载歌词出错:' + repr(e), format_exc())

    def get_music_name(self):
        return self.music_file.split(
            '\\')[-1][:-4] if self.opened() else '未打开文件'

    def play_pause(self, btn):
        try:
            if self.music_file:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.pause()
                    btn.set_img('play')
                else:
                    pygame.mixer.music.unpause()
                    btn.set_img('pause')
            else:
                self.set_msg('请先打开音频文件')

        except Exception as e:
            self.error('播放失败:' + repr(e), format_exc())

    def music_end(self, btn):
        if self.is_timer_end():
            pygame.mixer.music.stop()
            pygame.mixer.music.play()
            pygame.mixer.music.pause()
            self.music_offset_time = 0
            btn.set_img('play')
            self.off_timer()
        else:
            if self.repeat_mode == 1:
                pygame.mixer.music.stop()
                pygame.mixer.music.play()
                self.music_offset_time = 0
            else:
                pygame.mixer.music.stop()
                pygame.mixer.music.play()
                pygame.mixer.music.pause()
                self.music_offset_time = 0
                btn.set_img('play')

    def get_pos(self):
        return pygame.mixer.music.get_pos() + self.music_offset_time

    def set_pos(self, pos):
        pos = min(max(0, pos), self.music_total_time)
        pygame.mixer.music.set_pos(pos / 1000)
        self.music_offset_time = pos - pygame.mixer.music.get_pos()

    def get_prog(self):
        if self.music_total_time:
            self.music_total_time = max(self.music_total_time, self.get_pos())
            return self.get_pos() / self.music_total_time
        else:
            return 0

    def set_prog(self, prog):
        self.set_pos(self.music_total_time * prog)

    def get_time(self):
        return '/'.join([sec_to_time(self.get_pos() / 1000),
                        sec_to_time(self.music_total_time / 1000)])

    def get_vol(self):
        return self.volume

    def set_vol(self, vol):
        self.volume = min(max(0, vol), 100)
        pygame.mixer.music.set_volume((self.volume / 100)**1.5)

    def have_lrc(self):
        return True if self.lrc_marks else False

    def get_lrc(self, id=0):
        id += self.lrc_current_mark
        return self.lrc_dic[self.lrc_marks[id]] if self.have_lrc(
        ) and 0 < id < len(self.lrc_marks) else ''

    def last_lrc(self):
        self.lrc_current_mark = max(self.lrc_current_mark - 1, 0)
        self.set_pos(self.lrc_marks[self.lrc_current_mark])

    def next_lrc(self):
        if self.lrc_current_mark < len(self.lrc_marks) - 1:
            self.lrc_current_mark += 1
            self.set_pos(self.lrc_marks[self.lrc_current_mark])

    def update_lrc(self):
        try:
            while True:
                if self.have_lrc():
                    self.lrc_current_mark = upper_bound(
                        self.lrc_marks, self.get_pos()) - 1
        except Exception as e:
            self.error('加载歌词出错:' + repr(e), format_exc())
            self.update_lrc()

    def download_lrc(self):
        start_new_thread(self._dl, (self.lrc_id,))

    def _dl(self, beginat):
        try:
            if self.opened():
                url = "https://api88.net/api/netease/?key=cb9744c96c6f9033&type=so&cache=0&nu=100&id=" + \
                    quote(self.get_music_name())
                if self.lrc_url == -1:
                    self.set_msg('正在搜索歌曲', keep=True)
                    self.lrc_url = loads(urlopen(url).read().decode())['Body']
                if self.lrc_url:
                    self.lrc_id %= len(self.lrc_url)
                    self.set_msg('正在下载歌词' + str(self.lrc_id + 1) + '/' +
                                 str(len(self.lrc_url)), keep=True)
                    lrc = auto_decode(
                        urlopen(self.lrc_url[self.lrc_id]['lrc']).read())
                    if '暂无歌词' in lrc:
                        if self.lrc_id == beginat - 1:
                            self.set_msg('暂无歌词')
                        else:
                            self._dl(beginat)
                    else:
                        self.lrc_dic = parse_lrc(lrc.split('\n'))
                        self.lrc_marks = sorted(self.lrc_dic.keys())
                        self.lrc_current_mark = 0
                        with open(self.music_file[:-3] + 'lrc', 'w') as f:
                            print(lrc, file=f)
                        self.set_msg('歌词保存成功')
                else:
                    self.lrc_marks = None
                    self.set_msg('未找到该歌曲')
            else:
                self.set_msg('请先打开音频文件')
        except Exception as e:
            self.lrc_marks = None
            self.error('下载失败:' + repr(e), format_exc())
        self.lrc_id += 1

    def set_msg(self, msg, keep=False):
        self.message_cnt += 1
        self.message = msg
        if not keep:
            start_new_thread(self.clear_msg, (3,))

    def get_msg(self):
        return self.message

    def clear_msg(self, delay=0):
        cnt = self.message_cnt
        if delay:
            sleep(delay)
        if cnt == self.message_cnt:
            self.message = None

    def get_state(self):
        repeat_mode_str = ['顺序播放', '单曲循环', '列表循环']
        return repeat_mode_str[self.repeat_mode] + \
            ' 音量:' + str(self.get_vol()) + '%'

    def on_off_timer(self):
        if self.timer:
            self.off_timer()
        else:
            self.on_timer()

    def on_timer(self):
        self.timer = True
        self.timer_start_time = time()
        self.timer_set_time = 600

    def off_timer(self):
        self.timer = False

    def set_timer(self, minute):
        self.timer_set_time = max(minute // 5 * 300, 60)

    def get_timer(self):
        return self.timer_set_time / 60

    def is_timer_on(self):
        return self.timer

    def is_timer_end(self):
        return time() > self.timer_start_time + self.timer_set_time

    def get_timer_text(self):
        if self.is_timer_end():
            if self.opened():
                return '定时已结束，播放此首后将自动停止'
            else:
                self.off_timer()
                return ''
        else:
            return '定时剩余' + sec_to_time(self.timer_start_time +
                                        self.timer_set_time - time())

    def get_timer_prog(self):
        if self.is_timer_end():
            return 1
        else:
            return (time() - self.timer_start_time) / self.timer_set_time

    def set_repeat_mode(self, btn):
        self.repeat_mode += 1
        self.repeat_mode %= 3
        btn.set_img('repeat' + str(self.repeat_mode))

    def error(self, msg, err):
        self.set_msg(msg)
        print(err)
