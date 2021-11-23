import urllib.request


class Music:
    name: str = ''
    singer: str = ''
    album: str = ''
    id: int = 0
    _: str = ''  # 来源平台(取啥名儿都是关键字)
    mid: str = ''  # 仅QQ音乐
    vip: bool = False  # 仅网易云音乐

    def __init__(self, name: str, singer: str, album: str, id: int, _: str, mid: str = '', vip: bool = False) -> None:
        self.name = name
        self.singer = singer
        self.album = album
        self.id = id
        self._ = _
        self.mid = mid
        self.vip = vip

def search_163(name:str):
    pass

def search_qq(name:str):
    pass

def search(name:str):
    pass
