import pygame
import os
import easygui
from pygame.color import THECOLORS as color
from pygame.locals import *
from configparser import ConfigParser
from button import Button
from text import Text

version = 'v0.2'
current_music = None
is_paused = False


def openfile(btn):
    try:
        global current_music, is_paused, play_list
        # 打开文件对话框
        file = easygui.fileopenbox()
        if file:
            current_music = file
            if pygame.mixer.music.get_busy():
                # 停止正在播放的歌曲
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
            pygame.mixer.music.load(current_music)
            is_paused = False
            # 播放刚打开的歌曲
            play_pause(btn)
    except Exception as e:
        easygui.msgbox(repr(e))


def play_pause(btn):
    try:
        global is_paused
        if not pygame.mixer.music.get_busy():
            if is_paused:
                pygame.mixer.music.unpause()
                btn.set_img('pause')
            else:
                pygame.mixer.music.play()
                btn.set_img('pause')
                is_paused = True
        else:
            pygame.mixer.music.pause()
            btn.set_img('play')
    except Exception as e:
        easygui.msgbox(repr(e))


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
    bt_open.onclick = lambda: openfile(bt_play)
    # “播放”按钮
    bt_play = Button(pos[7], sizebt)
    bt_play.set_img('play')
    bt_play.onclick = lambda: play_pause(bt_play)
    # 按钮列表
    buttons = [bt_open, bt_play]

    # 初始化字体
    t_title = Text(fontfile, maxsizefile, sizex/2 -
                   spaceline, (sizex*0.75, 10), 'mu')

    while True:
        # 填充背景
        screen.fill(color[colorbg])
        # 绘制线
        pygame.draw.line(
            screen, color[colorline], (0, sizey-sizebt-spacebt-spaceline/2), (sizex, sizey-sizebt-spacebt-spaceline/2), spaceline)
        pygame.draw.line(
            screen, color[colorline], (sizex/2, 0), (sizex/2, sizey-sizebt-spacebt-spaceline/2), spaceline)
        # 显示按钮
        for button in buttons:
            button.show(screen)
        # 渲染文字
        if current_music:
            t_title.show(screen, current_music.split(
                '\\')[-1], color[colorfile])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    button.test_click(event.pos)

        pygame.display.update()


if __name__ == '__main__':
    main()
