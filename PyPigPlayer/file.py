import configparser
import os
import random
import shutil
import time
import traceback

import chardet
import psutil
import pypinyin

import music
import popup
import web
from func import *
from init import *


class Item:
    """
    文件浏览器中的项。
    """

    icon: str = ''
    left: list = []
    name: str = ''
    right: list = []

    def __init__(self, name: str, icon: str, left: list, right: list = []) -> None:
        self.name = name
        self.icon = icon
        self.left = left
        self.right = right


class Viewer:
    """
    文件浏览器。
    """

    desktop: bool = False
    id: int = 0
    listname: str = ''
    lrc: music.Lrc = None
    lrctemp: str = ''
    mp3temp: str = ''
    now: web.Music = None
    online: bool = False
    page_time: float = 0
    page: str = ''
    page2: str = ''
    path: str = ''
    player: music.Player = None
    playing: str = '未打开文件'
    playing2: str = ''
    playlist: list = []
    popup: bool = False
    preparing: web.Music = None
    reload: bool = True
    repmode: int = 0
    showitems: list = []
    showmode: int = 0
    update_time: float = 0
    viewid: float = 0
    viewing_list: str = None

    def __init__(self, player: music.Player, lrc: music.Lrc) -> None:
        self.player = player
        self.lrc = lrc
        self.home()
        start_thread(self.update)

    def _lists(self) -> None:
        tmp = [Item('默认歌单', 'list', [(self.showlist, '', False)])] + sorted([Item(i, 'list', [(self.showlist, i, False)], [(self.delete_list, i, True)]) for i in os.listdir(
            Lists) if os.path.isdir(os.path.join(Lists, i))], key=lambda x: self.sort_by(x.name))
        if self.showmode == 4:
            self.showitems = tmp

    def _open(self, path: str) -> None:
        try:
            if not path:
                if is_windows:
                    self.page = '磁盘列表'
                    self.page2 = ''
                    self.showitems = ([Item(i.device, 'disk', [(self.open, i.device, False)])
                                       for i in psutil.disk_partitions()])
                else:
                    self.open('/')

            else:
                all = {os.path.join(path, i) for i in os.listdir(
                    path) if not i.startswith('.')}
                if is_windows:
                    for i in os.popen(f'attrib /d "{path}"\\*').read().splitlines():
                        properties = i[: 21]
                        name = i[21:]
                        if ('S' in properties or 'H' in properties) and name in all:
                            all.remove(name)
                dirs = []
                files = []
                for i in all:
                    if os.path.isdir(i):
                        dirs.append(
                            Item(filename(i), 'folder', [(self.open, i, False)]))
                    else:
                        for j in Supported_Formats:
                            if ext(i) == j:
                                files.append(
                                    Item(filename(i), 'music', [(self.play, i, True), [self.set_id, 0, False], (self.update_list, False)]))
                dirs.sort(key=lambda x: self.sort_by(x.name))
                files.sort(key=lambda x: self.sort_by(x.name))
                for i, item in enumerate(files):
                    item.left[1][1] = i
                if self.path == path:
                    self.showitems = dirs+files

        except Exception as e:
            traceback.print_exc()
            err.set('无法打开文件夹:'+str(e))

    def _showlist(self, name: str) -> None:
        path = os.path.abspath(os.path.join(Lists, name))
        tmp = []
        for i in os.listdir(path):
            if os.path.isfile(os.path.join(path, i)):
                if ext(i) == '.mp3':
                    tmp.append(
                        Item(i[:-4], 'music', [(self.play, os.path.join(path, i), True), [self.set_id, 0, False], (self.update_list, name, False)], [(self.delete_music, name, i, True)]))
        tmp.sort(key=lambda x: self.sort_by(x.name))
        for i, item in enumerate(tmp):
            item.left[1][1] = i
        if self.viewing_list == name:
            self.showitems = tmp

    def _themes(self) -> None:
        tmp = []
        for theme in os.listdir(Themes):
            if os.path.isdir(os.path.join(Themes, theme)):
                tmp.append(Item(theme, 'theme',
                                [(self.set_theme, theme, True)]))
        if self.showmode == 6:
            self.showitems = tmp

    def add(self) -> None:
        """
        添加音乐到歌单。
        """
        if not self.popup:
            self.popup = True
            mp3 = self.mp3temp
            lrc = self.lrctemp
            name = self.playing+'.mp3'
            ch = popup.choose('请选择要添加到的歌单', '添加到歌单', ['新建...', '默认歌单'] + sorted([i for i in os.listdir(
                Lists) if os.path.isdir(os.path.join(Lists, i))], key=self.sort_by), 1)
            if ch:
                if ch == '新建...':
                    while True:
                        new = popup.input('请输入歌单名称', '新建歌单')
                        if not new:
                            self.popup = False
                            return
                        try:
                            assert(new != '默认歌单')
                            os.makedirs(os.path.join(Lists, new))
                            savepath = os.path.join(Lists, new, name)
                            break
                        except:
                            popup.print('换一个名称试试吧!', '创建歌单失败')
                elif ch == '默认歌单':
                    savepath = os.path.join(Lists, name)
                else:
                    savepath = os.path.join(Lists, ch, name)
                try:
                    if os.path.isfile(savepath):
                        if popup.yesno('歌单中已有同名歌曲，是否替换?', '添加到歌单'):
                            os.remove(savepath)
                        else:
                            self.popup = False
                            return
                    shutil.copy(mp3, savepath)
                    if lrc:
                        with open(lrcpath(savepath), 'wb') as f:
                            f.write(lrc.encode(errors='ignore'))
                    msg.set('添加到歌单成功!')
                except Exception as e:
                    traceback.print_exc()
                    err.set('添加到歌单失败:'+str(e))
            self.popup = False

    def close(self) -> None:
        """
        关闭音乐。
        """
        self.player.close()
        self.lrc.clear()
        self.playing = '未打开文件'
        self.playing2 = ''

    def delete_list(self, listname: str) -> None:
        """
        删除歌单。
        """
        if not self.popup:
            self.popup = True
            try:
                if popup.yesno(f'是否要删除歌单"{listname}"及其中音乐?', '删除歌单'):
                    info.set('正在删除歌单……')
                    if self.listname == listname:
                        self.close()
                    shutil.rmtree(os.path.join(Lists, listname))
                    msg.set('删除歌单成功!')
                    self._lists()
            except Exception as e:
                traceback.print_exc()
                err.set('删除歌单失败:'+str(e))
            finally:
                info.clear()
                self.popup = False

    def delete_music(self, listname: str, name: str) -> None:
        """
        删除歌单中的音乐。
        """
        if not self.popup:
            self.popup = True
            try:
                if popup.yesno(f'是否要删除音乐"{name}"?', '删除歌单中的音乐'):
                    info.set('正在从歌单中删除音乐……')
                    file = os.path.join(
                        Lists, listname, name) if listname else os.path.join(Lists, name)
                    if self.player.file and os.path.samefile(self.player.file, file):
                        self.close()
                    os.remove(file)
                    if os.path.isfile(lrcpath(file)):
                        os.remove(lrcpath(file))
                    msg.set('从歌单中删除音乐成功!')
                    self._showlist(listname)
            except Exception as e:
                traceback.print_exc()
                err.set('从歌单中删除音乐失败:'+str(e))
            finally:
                info.clear()
                self.popup = False

    def end(self) -> None:
        """
        接受到 pygame.USEREVENT 事件时调用此方法。
        """
        if self.player.playing:
            if self.repmode == 1:
                self.player.replay()
            else:
                self.next()

    def father(self) -> None:
        """
        返回上一级目录。
        """
        if self.showmode == -1:
            return
        elif self.showmode in (1, 2, 4):
            self.showmode = -1
            self.home()
        elif self.showmode == 3:
            self.tops()
        elif self.showmode == 5:
            self.viewing_list = None
            self.lists()
        elif self.desktop and self.path == desktop():
            self.desktop = False
            self.home()
        elif not self.path or self.path == '/':
            self.home()
        elif self.path == dirname(self.path):
            self.open('')
        else:
            self.open(dirname(self.path))

    def getitem(self, itemid: int) -> Item:
        """
        获取项。
        """
        try:
            return self.showitems[itemid]
        except:
            return None

    def home(self) -> None:
        """
        主页。
        """
        self.showmode = -1
        self.page = '主页'
        self.page2 = ''
        self.update_time = time.time()
        self.showitems = [
            Item('打开文件', 'folder', [
                (lambda: start_thread(self.open_choose), False)]),
            Item('磁盘文件', 'disk', [(self.open, '', False)]),
            Item('桌面文件', 'desktop', [(self.open_desktop, False)]),
            Item('我的歌单', 'list', [(self.lists, False)]),
            Item('查看榜单', 'top', [(self.tops, False)]),
            Item('切换主题', 'theme', [(self.themes, False)]),
            Item('下载歌手', 'music', [(lambda: start_thread(web.singer), False)]),
            Item('下载歌单', 'music', [
                 (lambda: start_thread(web.songlist), False)])
        ]

    def last(self) -> None:
        """
        上一首。
        """
        if self.playlist:
            play = self.play if not self.online else lambda x: start_thread(
                self.play_online, x)
            if self.repmode == 2:
                last = self.id
                while last == self.id:
                    last = random.randrange(len(self.playlist))
                self.id = last
                play(self.playlist[self.id])
            else:
                self.id = (self.id - 1) % len(self.playlist)
                play(self.playlist[self.id])

    def lists(self) -> None:
        """
        显示歌单列表。
        """
        self.showmode = 4
        self.page = '歌单列表'
        self.page2 = ''
        self._lists()
        self.update_time = time.time()
        self.viewid = 0

    def load_list(self, data: list) -> None:
        """
        加载音乐列表。
        """
        i = 0
        tmp = []
        for music in data:
            if music.vip:
                tmp.append(Item('[VIP] '+music.singer + ' - '+music.name,
                           music._, [(self.open_vip, music.url, True), (self.update_list, False)]))
            else:
                tmp.append(Item(music.singer+' - '+music.name, music._, [(self.play_online, music, True),
                                (self.set_id, i, False), (self.update_list, False)]))
                i += 1
        self.viewid = 0
        self.update_time = time.time()
        self.showitems = tmp

    def next(self) -> None:
        """
        下一首。
        """
        if self.playlist:
            play = self.play if not self.online else lambda x: start_thread(
                self.play_online, x)
            if self.repmode == 2:
                next = self.id
                while next == self.id:
                    next = random.randrange(len(self.playlist))
                self.id = next
                play(self.playlist[self.id])
            else:
                self.id = (self.id + 1) % len(self.playlist)
                play(self.playlist[self.id])

    def open(self, path: str) -> None:
        """
        打开文件夹。
        """
        if path:
            path = os.path.abspath(path)
        self.showmode = 0
        self.path = path
        self.page = '桌面' if os.path.isdir(path) and os.path.samefile(
            path, desktop()) else '根目录' if path == '/' else filename(path)
        self.page2 = path
        self._open(path)
        self.update_time = time.time()
        self.viewid = 0

    def open_choose(self) -> None:
        """
        选择文件打开。
        """
        file = popup.open('打开文件', '音乐文件', ' '.join(Supported_Formats))
        if file:
            self.open_file(file)

    def open_desktop(self) -> None:
        """
        打开桌面。
        """
        self.open(desktop())
        self.desktop = True

    def open_file(self, file: str) -> None:
        """
        打开文件。
        """
        file = os.path.abspath(file)
        self.open(os.path.dirname(file))
        self.update_list()
        self.play(file)
        self.set_id(self.playlist.index(file))

    def open_vip(self, url: str) -> None:
        """
        打开 VIP 音乐链接。
        """
        if not self.popup:
            self.popup = True
            if popup.yesno('是否要在浏览器中打开链接?', '该音乐为付费歌曲'):
                os.system('start '+url)
            self.popup = False

    def play(self, music: str) -> None:
        """
        播放音乐。
        """
        try:
            if self.preparing:
                if self.preparing != music:
                    msg.set('正在打开其他音乐，请稍后再试!')
            elif self.now != music:
                self.preparing = music
                self.player.close()
                self.lrc.clear()
                self.lrc.open('[00:00.00]正在缓冲中，请稍等')
                self.playing = filebasename(os.path.join(self.path, music))
                self.playing2 = f'[歌单:{self.listname}]' if self.listname else os.path.join(
                    self.path, music)
                self.online = False
                self.mp3temp = mp3path(os.path.join(self.path, music))
                self.player.open(self.mp3temp)
                self.lrc.clear()
                if os.path.isfile(os.path.join(self.path, os.path.splitext(music)[0] + '.lrc')):
                    lrcpath = os.path.join(
                        self.path, os.path.splitext(music)[0] + '.lrc')
                    lrcdata = open(
                        lrcpath, 'rb').read()
                    self.lrctemp = lrcdata.decode(
                        chardet.detect(lrcdata)['encoding'], 'ignore')
                    self.lrc.open(self.lrctemp)
                else:
                    self.lrctemp = ''
                self.now = music

        except Exception as e:
            err.set('播放音乐出错:'+str(e))
            self.close()

        finally:
            self.preparing = None

    def play_online(self, music: web.Music) -> None:
        """
        播放网络上的音乐。
        """
        try:
            if self.preparing:
                if self.preparing != music:
                    msg.set('正在打开其他音乐，请稍后再试!')
            elif self.now != music:
                self.preparing = music
                self.player.close()
                self.lrc.clear()
                self.lrc.open('[00:00.00]正在缓冲中，请稍等')
                self.playing = music.singer+' - '+music.name
                self.playing2 = music.url
                self.mp3temp = musicpath(music)
                self.lrctemp = web.lrc(music)
                self.player.open(self.mp3temp)
                self.lrc.clear()
                self.lrc.open(self.lrctemp)
                self.online = True
                self.now = music

        except Exception as e:
            traceback.print_exc()
            err.set('在线播放音乐出错:'+str(e))
            self.close()

        finally:
            self.preparing = None

    def save(self) -> None:
        """
        保存音乐。
        """
        if not self.popup:
            self.popup = True
            mp3 = self.mp3temp
            lrc = self.lrctemp
            if lrc:
                savepath = popup.save(
                    '保存音乐及歌词', self.playing+'.mp3', 'MP3 音乐文件 & LRC 歌词文件', '.mp3')
            else:
                savepath = popup.save(
                    '保存音乐', self.playing+'.mp3', 'MP3 音乐文件', '.mp3')
            if savepath:
                savepath = makefilename(savepath)
                try:
                    shutil.copy(mp3, savepath)
                    if lrc:
                        open(lrcpath(savepath), 'wb').write(
                            lrc.encode(errors='ignore'))
                    msg.set('保存音乐成功!')
                except Exception as e:
                    traceback.print_exc()
                    err.set('保存音乐失败:'+str(e))
            self.popup = False

    def search_online(self) -> None:
        """
        在线搜索音乐。
        """
        key = popup.input('请输入搜索关键词', '在线搜索音乐')
        if key:
            data = web.search(key)
            if data:
                self.showmode = 1
                self.page = '搜索:'+key
                self.page2 = ''
                self.load_list(data)
            else:
                err.set('未搜索到音乐!')

    def set_id(self, id: int) -> None:
        """
        设置当前音乐在播放列表中的位置。
        """
        self.id = id

    def set_pos(self, pos: float) -> None:
        """
        设置浏览位置。
        """
        self.viewid = pos*len(self.showitems)

    def set_theme(self, theme: str) -> None:
        """
        设置主题。
        """
        config = configparser.ConfigParser()
        config.read('config.ini')
        config.set('theme', 'theme', theme)
        config.write(open('config.ini', 'w'))
        self.page2 = '当前主题:'+theme
        self.reload = True

    def showlist(self, name: str) -> None:
        """
        加载歌单。
        """
        self.showmode = 5
        self.page = name if name else '默认歌单'
        self.page2 = ''
        self.viewing_list = name
        self._showlist(name)
        self.update_time = time.time()
        self.viewid = 0

    def sort_by(self, name: str) -> list:
        """
        按名称排序字符串的 key。
        """
        ret = []
        for c in name:
            pinyin = pypinyin.lazy_pinyin(c)
            if pinyin[0] != c:
                ret.append('\uffff'+pinyin[0])
            else:
                ret.append(c.lower())
        return ret

    def switch_rep(self) -> None:
        """
        切换循环模式 (0:顺序播放, 1:单曲循环, 2:随机播放)。
        """
        self.repmode = (self.repmode+1) % 3

    def themes(self) -> None:
        """
        显示主题列表。
        """
        self.showmode = 6
        self.page = '切换主题'
        self._themes()
        self.update_time = time.time()
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.page2 = '当前主题:'+config.get('theme', 'theme')
        self.viewid = 0

    def toplist(self, topid: int) -> None:
        """
        加载榜单。
        """
        data = web.toplist(topid)
        if data:
            self.showmode = 3
            self.page = Toplists[topid]
            self.page2 = ''
            self.load_list(data)

    def tops(self) -> None:
        """
        显示榜单列表。
        """
        self.showmode = 2
        self.page = '榜单列表'
        self.page2 = ''
        tmp = []
        for topid in Toplists:
            tmp.append(Item(Toplists[topid], 'list',
                       [(self.toplist, topid, True)]))
        self.viewid = 0
        self.update_time = time.time()
        self.showitems = tmp

    def update(self) -> None:
        """
        实时更新列表。
        """
        while True:
            time.sleep(1)
            if self.showmode == 0:
                self._open(self.path)
            elif self.showmode == 4:
                self._lists()
            elif self.showmode == 5:
                self._showlist(self.viewing_list)
            elif self.showmode == 6:
                self._themes()

    def update_list(self, listname: str = None) -> None:
        """
        更新播放列表。
        """
        self.listname = listname if listname else '默认歌单' if listname != None else ''
        self.playlist = [
            i.left[0][1] for i in self.showitems if i.left[0][0] in (self.play, self.play_online)]
