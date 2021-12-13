import threading
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


title = 'PyPigPlayer v1.6.1'
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
toplists = {
    26: '热歌榜',
    27: '新歌榜',
    62: '飙升榜',
    4: '流行指数榜'
}


def start_thread(func, *args, **kwargs):
    threading.Thread(target=func, args=args,
                     kwargs=kwargs, daemon=True).start()
