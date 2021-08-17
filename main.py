from text import Text
from button import Button
from mutagen.mp3 import MP3
from configparser import ConfigParser
from pygame.color import THECOLORS as color
import _thread
import os
import time
import easygui
import pygame
import win32api
import win32gui
import win32con

version = 'PyPigPlayer v0.9.1'
total_time = 0
offset_time = 0
start_time = 0
stop_time = 0
pagebt = 0
volume = 0
current_tm = 0
repaint = True
fullscreen = False
clock = False
repeat = False
cont = True
running = True
state = None
msg = None
lrc = None
timemark = None
current_music = None
defaultsize = None
screenx = None
screeny = None
sizex = None
sizey = None
size = None
MUSICEND = pygame.USEREVENT


def last_tm():
    global current_tm
    if timemark:
        if current_tm:
            current_tm -= 1
        setpoint(timemark[current_tm])
    else:
        show_msg('未载入歌词', 2)


def next_tm():
    global current_tm
    if timemark:
        if current_tm < len(timemark)-1:
            current_tm += 1
            setpoint(timemark[current_tm])
    else:
        show_msg('未载入歌词', 2)


def show_msg(m, t=0):
    global msg
    msg = m
    if t:
        _thread.start_new_thread(clear_msg, (t,))


def clear_msg(t=0):
    global msg
    if t:
        time.sleep(t)
    msg = None


def set_fullscreen(mode=1):
    global fullscreen, repaint, defaultsize, sizex, sizey, size
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
        if mode:
            print('Fullscreen on')
            fullscreen = 1
            sizex, sizey = size = (screenx, screeny)
            pygame.display.set_mode(
                size, pygame.FULLSCREEN | pygame.HWSURFACE)


def convertime(sec):
    return '{:0>2d}:{:0>2d}'.format(*divmod(max(sec, 0), 60))


def convertimemark(mark):
    m, s = mark.split(':')
    return int(int(m)*60000+float(s)*1000)


def getime():
    return pygame.mixer.music.get_pos()+offset_time


def set_repeat(btn):
    global repeat
    if repeat:
        repeat = False
        btn.set_img('repeat')
        print('Repeat off')
    else:
        repeat = True
        btn.set_img('repeat1')
        print('Repeat on')


def openfile(btn):
    global current_music, current_tm, total_time, offset_time, lrc, timemark
    # 打开文件对话框
    file = easygui.fileopenbox(default='*.mp3')
    if file:
        try:
            # 停止正在播放的歌曲
            if current_music:
                stop(btn)
            current_music = file
            # 载入文件
            print('Open file', file, end='...')
            pygame.mixer.music.load(current_music)
            print('Done')
            # 获取时长
            print('Getting total time', end='...')
            total_time = int(MP3(current_music).info.length*1000)
            print(total_time)
            # 解析歌词
            print('Parse lrc file', end='...')
            lrcfile = current_music[:-3]+'lrc'
            if os.path.exists(lrcfile):
                with open(lrcfile) as f:
                    parselrc(f.readlines())
                current_tm = 0
                print('Done')
            else:
                timemark = None
                print('Not exist')
            offset_time = 0
            pygame.mixer.music.play()
            pygame.mixer.music.pause()
        except Exception as e:
            easygui.msgbox('载入文件失败:'+str(e))
            current_music = None


def parselrc(file):
    global lrc, timemark
    lrc = {-1: ''}
    timemark = [-1]
    for line in file:
        for i in range(len(tmp := line[1:].replace('][', ']').split(']'))-1):
            lrc[convertimemark(tmp[i])] = tmp[-1].replace('\n', '').strip()
            timemark.append(convertimemark(tmp[i]))
    timemark.sort()


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
    global current_tm, offset_time
    current_tm = 0
    pygame.mixer.music.stop()
    pygame.mixer.music.play()
    pygame.mixer.music.pause()
    btn.set_img('play')
    offset_time = 0


def unload(btn):
    global current_music
    stop(btn)
    current_music = None


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
    global running, repeat, volume, start_time, stop_time, state, cont, clock
    while True:
        state = ('单曲循环:'+('开' if repeat else '关')) + \
            ' 音量:'+str(int(volume*100))+'%'+(' 定时:' +
                                             convertime(int(start_time+stop_time*60-time.time())) if clock else '')
        if clock and time.time() > start_time+stop_time*60:
            clock = cont = False
            stop_time = 0
            show_msg('定时已结束，播放此首后将自动停止')


def set_pagebt(x):
    global pagebt
    pagebt = x


def time_plus(x):
    global start_time, stop_time, clock
    stop_time += x
    if not clock:
        start_time = time.time()
        clock = True


def time_minus(x):
    global stop_time, clock
    if clock:
        stop_time = max(stop_time-x, 1)


def time_on_off(x):
    global clock, start_time, stop_time
    if clock:
        stop_time = 0
        clock = False
    else:
        start_time = time.time()
        stop_time = x
        clock = True


def culbt(n, mt, mb, x):
    ms = (mb-mt)/2
    if x >= n*(mt+ms)+ms:
        return mt, mb, (x-n*mt)/(n+1)
    a = mt/ms
    s = x/((a+1)*n+1)
    t = a*s
    return t, mb*t/mt, s


def close():
    global running
    running = False
    pygame.quit()


def main():
    global state, msg, pagebt, cont, repeat, stop_time, running, clock, volume, current_tm, current_music, defaultsize, screenx, screeny, fullscreen, sizex, sizey, size

    # 打开配置文件
    cp = ConfigParser()
    cp.read('settings.ini', encoding='utf-8')

    # 读取外观参数
    try:
        conf = dict(cp.items('Appearance'))

        fullscreen = last_fullscreen = int(conf['fullscreen'])
        if not fullscreen:
            defaultsize = tuple(eval(conf['window_default_size']))
            minx, miny = tuple(eval(conf['window_min_size']))

        maxsizebt = int(conf['button_max_size'])
        maxsizebar = int(conf['bar_max_size'])

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

        fontmsg = conf['message_font']
        maxsizemsg = int(conf['message_font_max_size'])
        colormsg = conf['message_font_color']
        if colormsg not in color.keys():
            raise ValueError(colormsg+'不是有效的颜色名称!')

        fontstate = conf['state_font']
        maxsizestate = int(conf['state_font_max_size'])
        colorstate = conf['state_font_color']
        if colorstate not in color.keys():
            raise ValueError(colorstate+'不是有效的颜色名称!')

        fontlrc = conf['lrc_font']
        maxsizelrc = int(conf['lrc_font_max_size'])
        colorlrc = conf['lrc_font_color']
        if colorlrc not in color.keys():
            raise ValueError(colorlrc+'不是有效的颜色名称!')
        colorlrcur = conf['current_lrc_font_color']
        if colorlrcur not in color.keys():
            raise ValueError(colorlrcur+'不是有效的颜色名称!')

        fonttime = conf['time_font']
        maxsizetime = int(conf['time_font_max_size'])
        colortime = conf['time_font_color']
        if colortime not in color.keys():
            raise ValueError(colortime+'不是有效的颜色名称!')

        fonttimer = conf['timer_font']
        maxsizetimer = int(conf['timer_font_max_size'])
        colortimer = conf['timer_font_color']
        if colortimer not in color.keys():
            raise ValueError(colortimer+'不是有效的颜色名称!')

        widthprog = int(conf['progress_width'])
        colorprog1 = conf['progress_color_1']
        if colorprog1 not in color.keys():
            raise ValueError(colorprog1+'不是有效的颜色名称!')
        colorprog2 = conf['progress_color_2']
        if colorprog2 not in color.keys():
            raise ValueError(colorprog2+'不是有效的颜色名称!')

    except Exception as e:
        easygui.msgbox('读取外观参数时发生异常:'+str(e))
        return

    # 读取播放器参数
    try:
        conf = dict(cp.items('Player'))

        timeb = int(conf['back_time'])
        timef = int(conf['forward_time'])

        defaultvol = int(conf['volume_default'])
        stepu = int(conf['volume_up_step'])
        stepd = int(conf['volume_down_step'])

        defaultime = int(conf['timer_default'])
        timep = int(conf['timer_longer_step'])
        timem = int(conf['timer_shorter_step'])

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
    pygame.display.set_caption(version)

    # 设置初始音量
    volume = defaultvol/100
    pygame.mixer.music.set_volume(volume)

    # 设置音乐结束事件
    pygame.mixer.music.set_endevent(MUSICEND)

    # 设置按键重复
    pygame.key.set_repeat(delaykey, intervalkey)

    # 初始化按钮栏
    d_num = 15
    l_num = 10
    r_num = 10
    d_bt, d_bar, d_space = culbt(d_num, maxsizebt, maxsizebar, sizex)
    l_bt, l_bar, l_space = culbt(l_num, maxsizebt, maxsizebar, sizey-d_bar)
    r_bt, r_bar, r_space = culbt(r_num, maxsizebt, maxsizebar, sizey-d_bar)
    d_pos = [((i+1)*d_space+(i+0.5)*d_bt, sizey-d_bar/2) for i in range(d_num)]
    l_pos = [(l_bar/2, (i+1)*l_space+(i+0.5)*l_bt) for i in range(l_num)]
    r_pos = [(sizex-r_bar/2, (i+1)*r_space+(i+0.5)*r_bt) for i in range(r_num)]

    # “定时”按钮
    bt_time = Button(0)
    bt_time.set_img('time')
    bt_time.onclick = lambda: set_pagebt(not pagebt)

    # “打开”按钮
    bt_open = Button(1)
    bt_open.set_img('plus')
    bt_open.onclick = lambda: _thread.start_new_thread(openfile, (bt_play,))

    # “上一首”按钮
    bt_last = Button(5)
    bt_last.set_img('last')
    bt_last.onclick = lambda: easygui.msgbox('上一首')

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

    # “下一首”按钮
    bt_next = Button(9)
    bt_next.set_img('next')
    bt_next.onclick = lambda: easygui.msgbox('下一首')

    # “重复”按钮
    bt_repeat = Button(12)
    bt_repeat.set_img('repeat')
    bt_repeat.onclick = lambda: set_repeat(bt_repeat)

    # “音量-”按钮
    bt_volm = Button(13)
    bt_volm.set_img('vol-')
    bt_volm.onclick = lambda: voldown(stepd)

    # “音量+”按钮
    bt_volp = Button(14)
    bt_volp.set_img('vol+')
    bt_volp.onclick = lambda: volup(stepu)

    # 按钮列表0
    buttons_0 = [bt_time, bt_open,  bt_back, bt_play,
                 bt_forward,  bt_repeat, bt_volm, bt_volp]

    # “关闭计时器”按钮
    bt_offtime = Button(1)
    bt_offtime.set_img('power')
    bt_offtime.onclick = lambda: time_on_off(defaultime)

    # “定时-”按钮
    bt_timem = Button(2)
    bt_timem.set_img('minus')
    bt_timem.onclick = lambda: time_minus(timem)

    # “定时+”按钮
    bt_timep = Button(3)
    bt_timep.set_img('plus')
    bt_timep.onclick = lambda: time_plus(timep)

    # 按钮列表1
    buttons_1 = [bt_time, bt_offtime, bt_timem, bt_timep]

    # 底部按钮列表
    d_list = [buttons_0, buttons_1]

    # “关闭”按钮
    bt_close = Button(0)
    bt_close.set_img('close')
    bt_close.onclick = close

    # “全屏”按钮
    bt_full = Button(1)
    bt_full.set_img('fullscreen')
    bt_full.onclick = set_fullscreen

    # “上一句”按钮
    bt_lastlrc = Button(2)
    bt_lastlrc.set_img('up')
    bt_lastlrc.onclick = last_tm

    # “下一句”按钮
    bt_nextlrc = Button(3)
    bt_nextlrc.set_img('down')
    bt_nextlrc.onclick = next_tm

    # 右侧按钮列表
    r_list = [bt_close, bt_full, bt_lastlrc, bt_nextlrc]

    # 初始化字体
    t_title = Text(fontfile, maxsizefile, 'mu')
    t_msg = Text(fontmsg, maxsizemsg, 'md')
    t_state = Text(fontstate, maxsizestate, 'md')
    t_lrc = Text(fontlrc, maxsizelrc, 'mm')
    t_time = Text(fonttime, maxsizetime, 'mm')
    t_timer = Text(fonttimer, maxsizetimer, 'rm')

    # 启动状态更新进程
    _thread.start_new_thread(get_state, tuple())

    # 定义鼠标按下变量
    mouse = 0

    # 主循环
    while True:
        if fullscreen != last_fullscreen or size != screen.get_size():
            # 更改窗口大小
            sizex, sizey = screen.get_size()
            sizex = max(sizex, minx)
            sizey = max(sizey, miny)
            size = (sizex, sizey)
            print('Resize window to', size)
            pygame.display.set_mode(size, pygame.RESIZABLE)
            repaint = 1
        last_fullscreen = fullscreen

        if repaint:
            # 重新初始化按钮栏
            d_num = 15
            l_num = 10
            r_num = 10
            d_bt, d_bar, d_space = culbt(d_num, maxsizebt, maxsizebar, sizex)
            l_bt, l_bar, l_space = culbt(
                l_num, maxsizebt, maxsizebar, sizey-d_bar)
            r_bt, r_bar, r_space = culbt(
                r_num, maxsizebt, maxsizebar, sizey-d_bar)
            d_pos = [((i+1)*d_space+(i+0.5)*d_bt, sizey-d_bar/2)
                     for i in range(d_num)]
            l_pos = [(l_bar/2, (i+1)*l_space+(i+0.5)*l_bt)
                     for i in range(l_num)]
            r_pos = [(sizex-r_bar/2, (i+1)*r_space+(i+0.5)*r_bt)
                     for i in range(r_num)]
            repaint = 0

            # 计算边界
            lledge = 10
            lmedge = l_bar+10
            lredge = (sizex-widthline)/2-10
            lmid = (lledge+lredge)/2
            lwidth = lredge-lledge
            lmmid = (lmedge+lredge)/2
            lmwidth = lredge-lmedge

            rledge = (sizex+widthline)/2+10
            rmedge = sizex-r_bar-10
            rredge = sizex-10
            rmid = (rledge+rredge)/2
            rwidth = rredge-rledge
            rmmid = (rledge+rmedge)/2
            rmwidth = rmedge-rledge

        # 填充背景
        screen.fill(color[colorbg])

        # 显示按钮
        for button in d_list[pagebt]:
            button.show(screen, d_pos[button.id], d_bt)
        for button in r_list:
            button.show(screen, r_pos[button.id], r_bt)

        # 渲染文字
        titlepos = t_title.show(screen,
                                current_music.split(
                                    '\\')[-1] if current_music else '请打开文件',
                                color[colorfile],
                                (rmmid, 10),
                                maxwidth=rmwidth).bottom
        if msg:
            t_msg.show(screen,
                       msg,
                       color[colormsg],
                       (lmmid, sizey-d_bar-widthline-10),
                       maxwidth=lmwidth)
        if msg or not current_music:
            statepos = t_state.show(screen,
                                    state,
                                    color[colorstate],
                                    (rmmid, sizey-d_bar-widthline-10),
                                    maxwidth=rmwidth).top
        else:
            statepos = t_state.show(screen,
                                    state,
                                    color[colorstate],
                                    (sizex/2, sizey-d_bar-widthline-10),
                                    maxwidth=sizex-20).top
        if current_music:
            # 绘制进度条
            rectprog = pygame.Rect(lledge,
                                   statepos - 10-widthprog,
                                   rredge-lledge,
                                   widthprog)
            progpos = rectprog.top-10
            pygame.draw.rect(screen,
                             color[colorprog1],
                             rectprog)
            if total_time:
                pygame.draw.rect(screen,
                                 color[colorprog2],
                                 pygame.Rect(lledge,
                                             statepos - 10-widthprog,
                                             (rredge-lledge) *
                                             getime()/total_time,
                                             widthprog))
            # 显示时间
            t_time.show(screen,
                        convertime(getime()//1000)+'/' +
                        convertime(total_time//1000),
                        color[colortime],
                        rectprog.center)
            if timemark:
                # 显示歌词
                while current_tm+1 < len(timemark) and getime() > timemark[current_tm+1]:
                    current_tm += 1
                while current_tm and getime() < timemark[current_tm]:
                    current_tm -= 1
                h_lrc, rectlrc = t_lrc.show(screen,
                                            lrc[timemark[current_tm]],
                                            color[colorlrcur],
                                            (rmmid,
                                             (titlepos+rectprog.top)/2),
                                            maxwidth=rmwidth,
                                            getheight=True)
                num_lrc = int((rectlrc.top-titlepos-10)/h_lrc)
                for i in range(1, num_lrc+1):
                    if current_tm-i > 0:
                        t_lrc.show(screen,
                                   lrc[timemark[current_tm-i]],
                                   color[colorlrc],
                                   (rmmid,
                                       (titlepos+rectprog.top)/2-i*h_lrc),
                                   maxwidth=rmwidth,
                                   maxheight=h_lrc)
                    if current_tm+i < len(timemark):
                        t_lrc.show(screen,
                                   lrc[timemark[current_tm+i]],
                                   color[colorlrc],
                                   (rmmid,
                                       (titlepos+rectprog.top)/2+i*h_lrc),
                                   maxwidth=rmwidth,
                                   maxheight=h_lrc)
        else:
            progpos = sizey-d_bar-widthline/2
        if pagebt == 1:
            t_timer.show(screen,
                         convertime(stop_time*60),
                         color[colortimer],
                         (sizex-10, sizey-d_bar/2),
                         maxheight=d_bar)

        # 绘制线
        pygame.draw.line(screen,
                         color[colorline],
                         (0, sizey-d_bar-widthline/2),
                         (sizex, sizey-d_bar-widthline/2),
                         widthline)
        pygame.draw.line(screen,
                         color[colorline],
                         (sizex/2, 0),
                         (sizex/2, progpos),
                         widthline)

        # 处理事件
        for event in pygame.event.get():
            # 关闭窗口
            if event.type == pygame.QUIT:
                close()
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
                for button in d_list[pagebt]:
                    button.test_click(event.pos)
                for button in r_list:
                    button.test_click(event.pos)
                if not running:
                    return

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
                if cont:
                    stop(bt_play)
                    if repeat:
                        play_pause(bt_play)
                else:
                    clear_msg()
                    unload(bt_play)

            # 按下按键
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    play_pause(bt_play)
                if event.key == pygame.K_UP:
                    last_tm()
                if event.key == pygame.K_DOWN:
                    next_tm()
                if event.key == pygame.K_LEFT:
                    back(timeb)
                if event.key == pygame.K_RIGHT:
                    forward(timef)
                if event.key == pygame.K_F11:
                    set_fullscreen()
                if event.key == pygame.K_ESCAPE:
                    set_fullscreen(0)

        # 刷新窗口
        pygame.display.update()


if __name__ == '__main__':
    main()
