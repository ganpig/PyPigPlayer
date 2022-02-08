import os
import time

Title = 'PyPigPlayer v2.3.1'

Fonts = 'Fonts'
Lists = 'Lists'
Temp = 'Temp'
Themes = 'Themes'
Tools = 'Tools'

Supported_Formats = [
    '.aif',
    '.aiff',
    '.ape',
    '.flac',
    '.m4a',
    '.mid',
    '.mp3',
    '.wav'
]

Toplists = {
    26: '热歌榜',
    27: '新歌榜',
    62: '飙升榜',
    4: '流行指数榜'
}

Timer_Time = {
    '不开启定时器': float('-inf'),
    '15 分钟': 900,
    '30 分钟': 1800,
    '45 分钟': 2700,
    '60 分钟': 3600,
    '90 分钟': 5400,
    '120 分钟': 7200
}


class Msg:
    msg: str = ''
    changed: bool = False
    change_time: float = 0

    def set(self, msg: str) -> None:
        self.change_time = time.time()
        self.changed = True
        self.msg = msg

    def query(self) -> str:
        self.changed = False
        return self.msg

    def clear(self) -> None:
        if self.msg:
            self.changed = True
            self.msg = ''

    def time(self) -> None:
        return time.time()-self.change_time


info = Msg()
msg = Msg()
err = Msg()

for i in (Lists, Temp):
    if not os.path.isdir(i):
        os.makedirs(i)

is_windows = os.name == 'nt'
