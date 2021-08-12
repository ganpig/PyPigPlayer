from text import Text
from button import Button
from configparser import ConfigParser
from pygame.locals import *
from pygame.color import THECOLORS as color
import _thread
import easygui
import pygame
import os
import eyed3
import wave
import contextlib
import mido


version = 'v0.2.1'
current_music = None
total_time = 0
is_paused = False
MUSICEND = pygame.USEREVENT


def convertime(sec):
    return '{:0>2d}:{:0>2d}'.format(*divmod(max(sec, 0), 60))


def get_total_time(file):
    # 获取音乐总时长
    if file[-4:] == '.mp3':
        return int(eyed3.load(current_music).info.time_secs)
    elif file[-4:] == '.wav':
        with contextlib.closing(wave.open(file, 'r')) as f:
            return int(f.getnframes()/f.getframerate())
    elif file[-4:] == '.mid':
        return int(mido.MidiFile(file, clip=True).length)


def openfile(btn):
    global current_music, total_time, is_paused, play_list
    # 打开文件对话框
    file = easygui.fileopenbox(filetypes=['*.mp3', '*.wav', '*.mid'])
    if file:
        current_music = file
        total_time = get_total_time(file)
        # 停止正在播放的歌曲
        stop(btn)
        try:
            pygame.mixer.music.load(current_music)
        except Exception as e:
            easygui.msgbox('播放失败:'+str(e))
            current_music = None


def play_pause(btn):
    try:
        global is_paused
        if not pygame.mixer.music.get_busy():
            if is_paused:
                pygame.mixer.music.unpause()
                btn.set_img('pause')
            else:
                pygame.mixer.music.play()
                pygame.mixer.music.set_endevent(MUSICEND)
                btn.set_img('pause')
                is_paused = True
        else:
            pygame.mixer.music.pause()
            btn.set_img('play')
    except Exception as e:
        easygui.msgbox(repr(e))


def stop(btn):
    global is_paused
    pygame.mixer.music.stop()
    btn.set_img('play')
    is_paused = False


def main():
    # 打开配置文件
    cp = ConfigParser()
    cp.read('settings.ini', encoding='utf-8')

    # 读取外观参数
    try:
        conf = dict(cp.items('Appearance'))
        fullscreen = int(conf['fullscreen'])
        if not fullscreen:
            defaultsize = tuple(eval(conf['default_window_size']))

        numbt = int(conf['button_num'])
        spacebt = int(conf['button_space'])
        maxsizebt = int(conf['button_max_size'])
        spaceline = int(conf['line_width'])

        colorline = conf['line_color']
        if colorline not in color.keys():
            raise(colorline+'不是有效的颜色名称!')

        colorbg = conf['background_color']
        if colorbg not in color.keys():
            raise(colorbg+'不是有效的颜色名称!')

        fontfile = conf['file_font']
        maxsizefile = int(conf['file_font_max_size'])

        colorfile = conf['file_font_color']
        if colorfile not in color.keys():
            raise(colorfile+'不是有效的颜色名称!')

        fonttime = conf['time_font']
        maxsizetime = int(conf['time_font_max_size'])

        colortime = conf['time_font_color']
        if colortime not in color.keys():
            raise(colortime+'不是有效的颜色名称!')

    except Exception as e:
        easygui.msgbox('读取外观参数时发生异常:'+str(e))
        return

    # 初始化窗口
    pygame.init()
    if fullscreen:
        size = pygame.display.list_modes()[0]
        screen = pygame.display.set_mode(size, FULLSCREEN | HWSURFACE)
    else:
        size = defaultsize
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        screen = pygame.display.set_mode(size)
    sizex, sizey = size
    pygame.display.set_caption('PyPigPlayer '+version)

    # 初始化菜单栏
    sizebt = int(min(maxsizebt, sizex/numbt-spacebt))
    pos = [(sizex/numbt*(i+0.5)-sizebt/2, sizey-sizebt-spacebt/2)
           for i in range(numbt)]
    # “打开”按钮
    bt_open = Button(pos[0], sizebt)
    bt_open.set_img('open')
    bt_open.onclick = lambda: _thread.start_new_thread(openfile, (bt_play,))
    # “播放”按钮
    bt_play = Button(pos[7], sizebt)
    bt_play.set_img('play')
    bt_play.onclick = lambda: play_pause(bt_play)
    # 按钮列表
    buttons = [bt_open, bt_play]

    # 初始化字体
    t_title = Text(fontfile, maxsizefile, sizex/2 -
                   spaceline, (sizex*0.75, 10), 'mu')
    t_time = Text(fonttime, maxsizetime, sizex/2 -
                  spaceline, (sizex*0.75, sizey-sizebt-spacebt-spaceline-10), 'md')

    while True:
        # 填充背景
        screen.fill(color[colorbg])
        # 绘制线
        pygame.draw.line(
            screen, color[colorline], (0, sizey-sizebt-spacebt-spaceline/2), (sizex, sizey-sizebt-spacebt-spaceline/2), spaceline)
        pygame.draw.line(
            screen, color[colorline], (sizex/2, 0), (sizex/2, sizey-sizebt-spacebt), spaceline)
        # 显示按钮
        for button in buttons:
            button.show(screen)
        # 渲染文字
        if current_music:
            t_title.show(screen, current_music.split(
                '\\')[-1], color[colorfile])
            t_time.show(
                screen, convertime(pygame.mixer.music.get_pos()//1000)+'/'+convertime(total_time), color[colortime])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    button.test_click(event.pos)
            if event.type == MUSICEND:
                stop(bt_play)

        pygame.display.update()


if __name__ == '__main__':
    main()
