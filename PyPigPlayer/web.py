import html
import json
import traceback
import urllib.parse
import urllib.request

import faker

import core
from init import *


class Music:
    """
    单曲信息。
    """
    name: str = ''
    singer: str = ''
    album: str = ''
    id: int = 0
    _: str = ''
    url: str = ''
    vip: bool = False
    mid: str = ''

    def __init__(self, name: str, singer: str, album: str, id: int, _: str, vip: bool = False, mid: str = '') -> None:
        self.name = name
        self.singer = singer
        self.album = album
        self.id = id
        self._ = _
        if _ == 'netease':
            self.url = f'https://music.163.com/#/song?id={id}'
        else:
            self.url = 'https://y.qq.com/n/ryqq/songDetail/'+mid
        self.vip = vip
        self.mid = mid


def get(url: str, headers: dict = {}, retry: int = 3) -> bytes:
    """
    获取 URL 数据。
    """
    if not retry:
        traceback.print_exc()
        err.set('无法访问 '+url)
    headers['User-Agent'] = faker.Faker().user_agent()
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
    return json.loads(core.autodecode(data))


def search(name: str) -> list:
    """
    搜索歌曲。
    """
    try:
        name = urllib.parse.quote_plus(name)
        info.set('正在网易云音乐搜索……')
        ret1 = [Music(i['name'], ' & '.join(j['name'] for j in i['artists']), i['album']['name'], i['id'], 'netease', i['fee'] == 1)
                for i in get_json('http://music.163.com/api/search/get?type=1&limit=100&s='+name)['result']['songs'] if not i['status']]
        info.set('正在QQ音乐搜索……')
        ret2 = [Music(i['songname'], ' & '.join(j['name'] for j in i['singer']), i['albumname'], i['songid'], 'qqmusic', i['pay']['payplay'], i['songmid'])
                for i in get_json('https://c.y.qq.com/soso/fcgi-bin/client_search_cp?n=99&format=json&w='+name)['data']['song']['list']]

        ret = []
        i = j = 0
        while i < len(ret1) and j < len(ret2):
            for k in range(5):
                if i+k == len(ret1):
                    break
                ret.append(ret1[i+k])
            for k in range(5):
                if j+k == len(ret2):
                    break
                ret.append(ret2[j+k])
            i += 5
            j += 5
        while i < len(ret1):
            ret.append(ret1[i])
            i += 1
        while j < len(ret2):
            ret.append(ret2[j])
            j += 1
        return ret

    except Exception as e:
        traceback.print_exc()
        err.set('搜索失败:'+str(e))

    finally:
        info.clear()


def link(music: Music) -> str:
    """
    获取歌曲音频链接。
    """
    info.set('正在获取音频链接……')
    try:
        if music._ == 'netease':
            return f'http://music.163.com/song/media/outer/url?id={music.id}'
        else:
            data = get_json(
                'https://u.y.qq.com/cgi-bin/musicu.fcg?data={%22data%22:{%22module%22:%22vkey.GetVkeyServer%22,%22method%22:%22CgiGetVkey%22,%22param%22:{%22guid%22:%220%22,%22songmid%22:[%22'+music.mid+'%22]}}}')
            return 'http://ws.stream.qqmusic.qq.com/'+data['data']['data']['midurlinfo'][0]['purl']

    except Exception as e:
        traceback.print_exc()
        err.set('获取音频链接失败:'+str(e))

    finally:
        info.clear()


def lrc(music: Music) -> str:
    """
    获取歌词。
    """
    info.set('正在获取歌词……')
    try:
        if music._ == 'netease':
            data = get_json(
                f'http://music.163.com/api/song/media?id={music.id}')
            return data['lyric'] if 'lyric' in data else ''
        else:
            data = get_json(f'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_yqq.fcg?nobase64=1&format=json&musicid={music.id}', {
                            'referer': f'https://y.qq.com/n/yqq/song/{music.mid}.html'})
            return html.unescape(html.unescape(data['lyric'])) if 'lyric' in data else ''

    except Exception as e:
        traceback.print_exc()
        err.set('获取歌词失败:'+str(e))

    finally:
        info.clear()


def toplist(topid: int) -> list:
    """
    获取 QQ 音乐榜单。
    """
    info.set('正在获取榜单……')
    try:
        data = get_json(
            f'https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg?topid={topid}')['songlist']
        return [Music(i['data']['songname'], ' & '.join(j['name'] for j in i['data']['singer']), i['data']['albumname'], i['data']['songid'], 'qqmusic', i['data']['pay']['payplay'], i['data']['songmid'])
                for i in data]

    except Exception as e:
        traceback.print_exc()
        err.set('获取榜单失败:'+str(e))

    finally:
        info.clear()
