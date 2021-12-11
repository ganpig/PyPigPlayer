import os
import time


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


title = 'PyPigPlayer v1.5'
ffmpeg = 'Tools\\ffmpeg.exe'
temp = 'Temp'
info = Msg()
msg = Msg()
err = Msg()
supported_formats = [
    'mp3',
    'wav',
    'm4a',
    'aif', 'aiff',
    'flac',
    'ape',
    'mid'
]
