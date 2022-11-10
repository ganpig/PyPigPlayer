## search_netease

`http://music.163.com/api/search/get?s={name}&type=1`

eg: `http://music.163.com/api/search/get?s=Faded&type=1`

```python
return data['result']['songs']
```

返回结果：列表，`name`为歌名，`artists`为歌手（列表，各歌手`name`为歌手名），`album.name`为专辑名称，`id`为歌曲ID，`copyrightId`为0则为免费歌曲。

## download_netease

`http://music.163.com/song/media/outer/url?id={id}.mp3`

eg: `http://music.163.com/song/media/outer/url?id=36990266.mp3`

返回结果：MP3文件。

## lrc_netease

`http://music.163.com/api/song/media?id={id}`

eg: `http://music.163.com/api/song/media?id=36990266`

```python
return data['lyric']
```

返回结果：字符串。

## search_qqmusic

`https://c.y.qq.com/soso/fcgi-bin/client_search_cp?n=99&w={name}`

eg: `https://c.y.qq.com/soso/fcgi-bin/client_search_cp?n=99&w={mine}`

```python
return data['data']['song']['list']
```

返回结果：列表，`songname`为歌名，`singer`为歌手（列表，各歌手`name`为歌手名），`albumname`为专辑名称，`songid`为歌曲ID。

- 

## lrc_qqmusic

`https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_yqq.fcg?nobase64=1&musicid={id}&format=json`（需添加header：`referer=https://y.qq.com/n/yqq/song/{mid}.html`）

```python
return data['lyric']
```

返回结果：字符串，含有`&#10;`形式转义字符。

## download_qqmusic

```python
'https://u.y.qq.com/cgi-bin/musicu.fcg?data={%22data%22:{%22module%22:%22vkey.GetVkeyServer%22,%22method%22:%22CgiGetVkey%22,%22param%22:{%22guid%22:%220%22,%22songmid%22:[%22'+music.mid+'%22]}}}'
```

`http://ws.stream.qqmusic.qq.com/C{mid}.m4a?guid={guid}&vkey={vkey}`

## toplist_qqmusic

`https://c.y.qq.com/v8/fcg-bin/fcg_v8_toplist_cp.fcg?topid={id}`

ID取值如下：

- 26：热歌榜
- 27：新歌榜
- 62：飙升榜
