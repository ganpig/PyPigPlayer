import difflib
import html
import json
import urllib.parse
import urllib.request


class Music:
    """
    单曲信息。
    """
    name: str = ''
    singer: str = ''
    album: str = ''
    id: int = 0
    _: str = ''  # 来源平台
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


def get(url: str, headers: dict = {}, retry: int = 3) -> bytes:
    """
    获取 URL 数据。
    """
    if not retry:
        raise Exception()
    req = urllib.request.Request(url, headers=headers)
    try:
        return urllib.request.urlopen(req).read()
    except:
        return get(url, headers, retry-1)


def get_json(url: str, headers: dict = {}):
    """
    获取 URL 数据并按 JSON 格式解析。
    """
    data = get(url, headers)
    return json.loads(data.decode())


def search(name: str) -> list:
    """
    搜索歌曲。
    """
    def similar(x):
        return difflib.SequenceMatcher(None, name, x.name+x.singer).ratio()

    ret1 = [Music(i['name'], ' / '.join(j['name'] for j in i['artists']), i['album']['name'], i['id'], 'netease', vip=i['fee'] == 1)
            for i in get_json('http://music.163.com/api/search/get?type=1&limit=100&s='+name)['result']['songs']]
    ret2 = [Music(i['songname'], ' / '.join(j['name'] for j in i['singer']), i['albumname'], i['songid'], 'qqmusic', i['songmid'])
            for i in get_json('https://c.y.qq.com/soso/fcgi-bin/client_search_cp?n=99&format=json&w='+name)['data']['song']['list']]
    ret = []
    i = j = 0
    while i < len(ret1) and j < len(ret2):
        if similar(ret1[i]) >= similar(ret2[j]):
            ret.append(ret1[i])
            i += 1
        else:
            ret.append(ret2[j])
            j += 1
    while i < len(ret1):
        ret.append(ret1[i])
        i += 1
    while j < len(ret2):
        ret.append(ret2[j])
        j += 1
    return ret


def download(music: Music) -> bytes:
    """
    下载歌曲音频。
    """
    if music._ == 'netease':
        return get(f'http://music.163.com/song/media/outer/url?id={music.id}')
    else:
        data = get_json(
            'https://u.y.qq.com/cgi-bin/musicu.fcg?data={%22data%22:{%22module%22:%22vkey.GetVkeyServer%22,%22method%22:%22CgiGetVkey%22,%22param%22:{%22guid%22:%220%22,%22songmid%22:[%22'+music.mid+'%22]}}}')
        return get('http://ws.stream.qqmusic.qq.com/'+data['data']['data']['midurlinfo'][0]['purl'])


def lrc(music: Music) -> str:
    """
    获取歌曲歌词。
    """
    if music._ == 'netease':
        data = get_json(f'http://music.163.com/api/song/media?id={music.id}')
        return data['lyric']
    else:
        data = get_json(f'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_yqq.fcg?nobase64=1&format=json&musicid={music.id}', {
                        'referer': f'https://y.qq.com/n/yqq/song/{music.mid}.html'})
        return html.unescape(html.unescape(data['lyric']))


def toplist(topid: int) -> list:
    """
    获取 QQ 音乐榜单。
    """
    return [Music(i['data']['songname'], ' / '.join(j['name'] for j in i['data']['singer']), i['data']['albumname'], i['data']['songid'], 'qqmusic', i['data']['songmid'])
            for i in get_json(f'https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg?topid={topid}')['songlist']]
