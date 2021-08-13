from text import Text
from button import Button
from configparser import ConfigParser
from pygame.color import THECOLORS as color
import _thread
import time
import easygui
import pygame
import eyed3
import win32api
import win32gui
import win32con

version = 'v0.6'
current_music = None
total_time = 0
offset_time = 0
MUSICEND = pygame.USEREVENT
volume = 0.5
repeat = False


def convertime(sec):
    return '{:0>2d}:{:0>2d}'.format(*divmod(max(sec, 0), 60))


def getime():
    return pygame.mixer.music.get_pos()+offset_time


def set_repeat():
    global repeat
    if repeat:
        repeat = False
        print('Repeat off')
    else:
        repeat = True
        print('Repeat on')


def openfile(btn):
    global current_music, total_time, offset_time
    # 打开文件对话框
    file = easygui.fileopenbox(default='*.mp3')
    if file:
        print('Open file', file)
        try:
            # 停止正在播放的歌曲
            if current_music:
                stop(btn)
            current_music = file
            # 载入文件
            pygame.mixer.music.load(current_music)
            # 获取时长
            total_time = int(eyed3.load(current_music).info.time_secs*1000)
            offset_time = 0
            pygame.mixer.music.play()
            pygame.mixer.music.pause()
        except Exception as e:
            easygui.msgbox('载入文件失败:'+str(e))
            current_music = None


def play_pause(btn):
    try:
        global is_paused, current_music
        if current_music:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.unpause()
                btn.set_img('pause')
            else:
                pygame.mixer.music.pause()
                btn.set_img('play')
        else:
            easygui.msgbox('请先打开音频文件!')
    except Exception as e:
        easygui.msgbox(repr(e))


def stop(btn):
    global is_paused, offset_time
    pygame.mixer.music.stop()
    pygame.mixer.music.play()
    pygame.mixer.music.pause()
    btn.set_img('play')
    is_paused = False
    offset_time = 0


def back(time):
    global current_music, offset_time
    if current_music:
        to_point = max(0, getime()-time*1000)
        print('set time to', to_point)
        setpoint(to_point)


def forward(time):
    global current_music, offset_time, total_time
    if current_music:
        to_point = min(total_time, getime()+time*1000)
        print('set time to', to_point)
        setpoint(to_point)


def setpoint(to_point):
    global offset_time
    try:
        pygame.mixer.music.set_pos(to_point/1000)
        offset_time = to_point-pygame.mixer.music.get_pos()
    except Exception as e:
        print(repr(e))


def volup(step):
    global volume
    volume = round(min(volume+step/100, 1), 2)
    print('set volume to', volume)
    pygame.mixer.music.set_volume(volume)


def voldown(step):
    global volume
    volume = round(max(volume-step/100, 0), 2)
    print('set volume to', volume)
    pygame.mixer.music.set_volume(volume)

def get_state():
    global repeat,volume
    return '单曲循环:'+('开' if repeat else '关')+' 音量:'+str(int(volume*100))+'%'

def main():
    # 打开配置文件
    cp = ConfigParser()
    cp.read('settings.ini', encoding='utf-8')

    # 读取外观参数
    try:
        conf = dict(cp.items('Appearance'))
        fullscreen = int(conf['fullscreen'])
        if not fullscreen:
            defaultsize = tuple(eval(conf['window_default_size']))
            minx, miny = tuple(eval(conf['window_min_size']))
        numbt = int(conf['button_num'])
        minspacebt = int(conf['button_min_space'])
        maxsizebt = int(conf['button_max_size'])
        widthline = int(conf['line_width'])
        colorline = conf['line_color']
        if colorline not in color.keys():
            raise ValueError(colorline+'不是有效的颜色名称!')
        colorbg = conf['background_color']
        if colorbg not in color.keys():
            raise ValueError(colorbg+'不是有效的颜色名称!')
        fontfile = conf['file_font']
        maxsizefile = int(conf['file_font_max_size'])
        colorfile = conf['file_font_color']
        if colorfile not in color.keys():
            raise ValueError(colorfile+'不是有效的颜色名称!')
        fontstate = conf['state_font']
        maxsizestate = int(conf['state_font_max_size'])
        colorstate = conf['state_font_color']
        if colorfile not in color.keys():
            raise ValueError(colorfile+'不是有效的颜色名称!')
        fonttime = conf['time_font']
        maxsizetime = int(conf['time_font_max_size'])
        colortime = conf['time_font_color']
        if colortime not in color.keys():
            raise ValueError(colortime+'不是有效的颜色名称!')
        widthprog = int(conf['progress_width'])
        colorprog1 = conf['progress_color_1']
        if colorprog1 not in color.keys():
            raise ValueError(colorprog1+'不是有效的颜色名称!')
        colorprog2 = conf['progress_color_2']
        if colorprog2 not in color.keys():
            raise ValueError(colorprog2+'不是有效的颜色名称!')
        spaceprog = int(conf['progress_space'])
    except Exception as e:
        easygui.msgbox('读取外观参数时发生异常:'+str(e))
        return

    # 读取播放器参数
    try:
        conf = dict(cp.items('Player'))
        timeb = int(conf['back_time'])
        timef = int(conf['forward_time'])
        stepu = int(conf['volume_up_step'])
        stepd = int(conf['volume_down_step'])
    except Exception as e:
        easygui.msgbox('读取播放器参数时发生异常:'+str(e))
        return

    # 读取按键参数
    try:
        conf = dict(cp.items('Key'))
        delaykey = int(conf['repeat_delay'])
        intervalkey = int(conf['repeat_interval'])
    except Exception as e:
        easygui.msgbox('读取按键参数时发生异常:'+str(e))
        return

    # 获取屏幕分辨率
    screenx = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    screeny = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    print('Screen size is', (screenx, screeny))

    # 初始化窗口
    pygame.init()
    if fullscreen:
        sizex, sizey = size = (screenx, screeny)
        screen = pygame.display.set_mode(
            size, pygame.FULLSCREEN | pygame.HWSURFACE)
    else:
        sizex, sizey = size = defaultsize
        screen = pygame.display.set_mode(size, pygame.RESIZABLE)
        win32gui.SetWindowPos(win32gui.GetForegroundWindow(),
                              win32con.HWND_TOPMOST,
                              (screenx-sizex)//2, (screeny-sizey)//2,
                              sizex, sizey,
                              win32con.SWP_SHOWWINDOW)
    print('Window size is', size)
    pygame.display.set_caption('PyPigPlayer '+version)

    # 设置音乐结束事件
    pygame.mixer.music.set_endevent(MUSICEND)

    # 设置按键重复
    pygame.key.set_repeat(delaykey, intervalkey)

    # 初始化按钮栏
    sizebt = min(maxsizebt, (sizex-minspacebt)/numbt-minspacebt)
    spacebt = (sizex-numbt*sizebt)/(numbt+1)
    pos = [(sizex/numbt*(i+0.5)-sizebt/2, sizey-sizebt-spacebt/2)
           for i in range(numbt)]

    # “打开”按钮
    bt_open = Button(0)
    bt_open.set_img('open')
    bt_open.onclick = lambda: _thread.start_new_thread(openfile, (bt_play,))

    # “快退”按钮
    bt_back = Button(6)
    bt_back.set_img('back')
    bt_back.onclick = lambda: back(timeb)

    # “播放”按钮
    bt_play = Button(7)
    bt_play.set_img('play')
    bt_play.onclick = lambda: play_pause(bt_play)

    # “快进”按钮
    bt_forward = Button(8)
    bt_forward.set_img('forward')
    bt_forward.onclick = lambda: forward(timef)

    # “重复”按钮
    bt_repeat = Button(12)
    bt_repeat.set_img('repeat')
    bt_repeat.onclick = set_repeat

    # “音量-”按钮
    bt_volm = Button(13)
    bt_volm.set_img('vol-')
    bt_volm.onclick = lambda: voldown(stepd)

    # “音量+”按钮
    bt_volp = Button(14)
    bt_volp.set_img('vol+')
    bt_volp.onclick = lambda: volup(stepu)

    # 按钮列表
    buttons = [bt_open, bt_back, bt_play,
               bt_forward, bt_repeat, bt_volm, bt_volp]

    # 初始化字体
    t_title = Text(fontfile, maxsizefile, 'mu')
    t_state = Text(fontstate, maxsizestate, 'mu')
    t_time = Text(fonttime, maxsizetime, 'md')

    # 定义重绘变量
    repaint = 0

    # 定义鼠标按下变量
    mouse = 0

    # 初始化计数器
    start_time = time.time()
    frame = 0

    # 主循环
    while True:
        # 输出帧率
        if frame and not frame % 10000:
            print('current fps is', int(frame/(time.time()-start_time)))
        frame += 1

        if not fullscreen and size != screen.get_size():
            # 更改窗口大小
            sizex, sizey = screen.get_size()
            sizex = max(sizex, minx)
            sizey = max(sizey, miny)
            size = (sizex, sizey)
            print('Resize window to', size)
            pygame.display.set_mode(size, pygame.RESIZABLE)
            repaint = 1

        if repaint:
            # 重新初始化按钮栏
            sizebt = min(maxsizebt, (sizex-minspacebt)/numbt-minspacebt)
            spacebt = (sizex-numbt*sizebt)/(numbt+1)
            pos = [(spacebt+(sizebt+spacebt)*i, sizey-sizebt-spacebt/2)
                   for i in range(numbt)]
            repaint = 0

        # 填充背景
        screen.fill(color[colorbg])

        # 显示按钮
        for button in buttons:
            button.show(screen, pos[button.id], sizebt)

        # 绘制线
        pygame.draw.line(screen,
                         color[colorline],
                         (0, sizey-sizebt-spacebt-widthline/2),
                         (sizex, sizey-sizebt-spacebt-widthline/2),
                         widthline)
        pygame.draw.line(screen,
                         color[colorline],
                         (sizex/2, 0),
                         (sizex/2, sizey-sizebt-spacebt-widthline/2),
                         widthline)

        if current_music:
            # 绘制进度条
            rectprog = pygame.Rect((sizex+widthline)/2+spaceprog,
                                   sizey-sizebt-spacebt - widthline - spaceprog-widthprog,
                                   (sizex-widthline)/2-spaceprog*2,
                                   widthprog)
            pygame.draw.line(screen,
                             color[colorprog2],
                             ((sizex+widthline)/2+spaceprog, sizey-sizebt -
                              spacebt-widthline - spaceprog-widthprog/2),
                             (sizex-spaceprog, sizey-sizebt-spacebt -
                              widthline-spaceprog-widthprog/2),
                             widthprog)
            if total_time:
                pygame.draw.line(screen,
                                 color[colorprog1],
                                 ((sizex+widthline)/2+spaceprog+((sizex-widthline)/2-spaceprog*2)*getime()/total_time,
                                  sizey-sizebt-spacebt-widthline - spaceprog-widthprog/2),
                                 (sizex-spaceprog, sizey-sizebt-spacebt -
                                     widthline-spaceprog-widthprog/2),
                                 widthprog)

            # 渲染文字
            titlepos = t_title.show(screen,
                                    current_music.split('\\')[-1],
                                    color[colorfile],
                                    (sizex - widthline)/2,
                                    (sizex*0.75+widthline*0.25, 10)).midbottom
            t_state.show(screen,
                         get_state(),
                         color[colorstate],
                         (sizex - widthline)/2,
                         titlepos)
            t_time.show(screen,
                        convertime(getime()//1000)+'/' +
                        convertime(total_time//1000),
                        color[colortime],
                        (sizex - widthline)/2,
                        (sizex*0.75+widthline*0.25, sizey-sizebt-spacebt-widthline-10))

        # 处理事件
        for event in pygame.event.get():
            # 关闭窗口
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            # 鼠标按下
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = 1
                if current_music:
                    if rectprog.collidepoint(event.pos):
                        to_point = int(total_time *
                                       (event.pos[0]-rectprog.left)/rectprog.width)
                        print('set time to', to_point)
                        setpoint(to_point)
                for button in buttons:
                    button.test_click(event.pos)

            # 鼠标放开
            if event.type == pygame.MOUSEBUTTONUP:
                mouse = 0

            # 鼠标拖动
            if event.type == pygame.MOUSEMOTION:
                if mouse:
                    if current_music:
                        if rectprog.collidepoint(event.pos):
                            setpoint(int(
                                total_time*(event.pos[0]-rectprog.left)/rectprog.width))

            # 音乐结束
            if event.type == MUSICEND:
                stop(bt_play)
                if repeat:
                    play_pause(bt_play)

            # 按下按键
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    play_pause(bt_play)
                if event.key == pygame.K_UP:
                    volup(stepu)
                if event.key == pygame.K_DOWN:
                    voldown(stepd)
                if event.key == pygame.K_LEFT:
                    back(timeb)
                if event.key == pygame.K_RIGHT:
                    forward(timef)
                if event.key == pygame.K_F11:
                    if fullscreen:
                        print('Fullscreen off')
                        fullscreen = 0
                        sizex, sizey = size = defaultsize
                        pygame.display.set_mode(size)
                        pygame.display.set_mode(size, pygame.RESIZABLE)
                        win32gui.SetWindowPos(win32gui.GetForegroundWindow(),
                                              win32con.HWND_TOPMOST,
                                              (screenx-sizex)//2, (screeny-sizey)//2,
                                              sizex, sizey,
                                              win32con.SWP_SHOWWINDOW)
                    else:
                        print('Fullscreen on')
                        fullscreen = 1
                        sizex, sizey = size = (screenx, screeny)
                        screen = pygame.display.set_mode(size,
                                                         pygame.FULLSCREEN | pygame.HWSURFACE)
                    repaint = 1
                if event.key == pygame.K_ESCAPE:
                    if fullscreen:
                        print('Fullscreen off')
                        fullscreen = 0
                        sizex, sizey = size = defaultsize
                        pygame.display.set_mode(size)
                        pygame.display.set_mode(size, pygame.RESIZABLE)
                        win32gui.SetWindowPos(win32gui.GetForegroundWindow(),
                                              win32con.HWND_TOPMOST,
                                              (screenx-sizex)//2, (screeny-sizey)//2,
                                              sizex, sizey,
                                              win32con.SWP_SHOWWINDOW)
                        repaint = 1

        # 刷新窗口
        pygame.display.update()


if __name__ == '__main__':
    main()
