import pygame
from pygame.locals import *
from ppp_button import Button
from ppp_config import Config
from ppp_file import *
from ppp_func import *
from ppp_player import Player
from ppp_text import Text
from ppp_window import Window
from sys import exit
from easygui import fileopenbox, msgbox, ynbox
from traceback import format_exc


if __name__ == '__main__':
    try:
        config = Config('config.ini')

        config.get_section('program')
        ver = config.get('version')

        config.get_section('window')
        ui_win_dflt_size = config.get_tuple('default_size')
        ui_win_min_size = config.get_tuple('min_size')
        ui_win_prpt = config.get_int('left_proportion') / 100

        config.get_section('button')
        ui_btn_max_size = config.get_int('button_max_size')
        ui_bar_max_size = config.get_int('bar_max_size')
        ui_bar_max_prpt = config.get_int('bar_max_proportion') / 100
        ui_sbar_max_prpt = config.get_int('sidebar_max_proportion') / 100

        config.get_section('line')
        ui_line_wid = config.get_int('width')
        ui_line_col = config.get_color('color')

        config.get_section('background')
        ui_bg_show_img = config.get_int('show_image')
        if ui_bg_show_img:
            ui_bg_img = config.get_img('image')
        else:
            ui_bg_col = config.get_color('color')

        config.get_section('filename')
        ui_t_file_ft = config.get('font')
        ui_t_file_col = config.get_color('color')
        ui_t_file_size = config.get_tuple('size')

        config.get_section('message')
        ui_t_msg_ft = config.get('font')
        ui_t_msg_col = config.get_color('color')
        ui_t_msg_size = config.get_tuple('size')

        config.get_section('state')
        ui_t_state_ft = config.get('font')
        ui_t_state_col = config.get_color('color')
        ui_t_state_size = config.get_tuple('size')

        config.get_section('lrc')
        ui_t_lrc_ft = config.get('font')
        ui_t_lrc_cur_col = config.get_color('color1')
        ui_t_lrc_col = config.get_color('color2')
        ui_t_lrc_size = config.get_tuple('size')
        ui_lrc_space = config.get_int('space')

        config.get_section('progress')
        ui_prog_wid = config.get_int('width')
        ui_prog_past_col = config.get_color('color1')
        ui_prog_col = config.get_color('color2')
        ui_t_prog_ft = config.get('font')
        ui_t_prog_size = config.get_tuple('size')
        ui_t_prog_col = config.get_color('color')

        config.get_section('timer')
        ui_tmr_wid = config.get_int('width')
        ui_tmr_past_col = config.get_color('color1')
        ui_tmr_col = config.get_color('color2')
        ui_t_tmr_ft = config.get('font')
        ui_t_tmr_size = config.get_tuple('size')
        ui_t_tmr_col = config.get_color('color')

        config.get_section('repeatkey')
        key_delay = config.get_int('delay')
        key_interval = config.get_int('interval')

    except Exception as e:
        msgbox('读取配置出错:' + repr(e))
        exit()

    try:
        pygame.init()
        window = Window(ui_win_dflt_size, ui_win_min_size,
                        'PyPigPlayer ' + ver)
        screen = window.screen
        ui_win_size_x, ui_win_size_y = window.size
        player = Player()
        pygame.key.set_repeat(key_delay, key_interval)

        # 零散按钮
        btn_back = Button(-1, 'back',
                          lambda: player.set_pos(player.get_pos() - 5000))
        btn_forward = Button(-1, 'forward',
                             lambda: player.set_pos(player.get_pos() + 5000))
        btn_minus = Button(-1, 'minus',
                           lambda: player.set_timer(player.get_timer() - 5))
        btn_plus = Button(-1, 'plus',
                          lambda: player.set_timer(player.get_timer() + 5))

        # 底部按钮
        btn_time = Button(0, 'time', player.on_off_timer)
        btn_mode = Button(1, 'mode', lambda: msgbox('该功能尚在开发'))
        btn_open = Button(2, 'open', lambda: player.open_file(
            btn_play, fileopenbox()))
        btn_last = Button(6, 'last', lambda: msgbox('该功能尚在开发'))
        btn_play = Button(7, 'play', lambda: player.play_pause(btn_play))
        btn_next = Button(8, 'next', lambda: msgbox('该功能尚在开发'))
        btn_repeat = Button(
            12, 'repeat0', lambda: player.set_repeat_mode(btn_repeat))
        btn_volm = Button(
            13, 'vol-', lambda: player.set_vol(player.get_vol() - 5))
        btn_volp = Button(
            14, 'vol+', lambda: player.set_vol(player.get_vol() + 5))
        btn_list_d = [btn_time, btn_mode, btn_open, btn_last, btn_play,
                      btn_next, btn_repeat, btn_volm, btn_volp]

        # 右侧按钮
        btn_close = Button(0, 'close', exit)
        btn_full = Button(1, 'fullscreen', window.set_fullscreen)
        btn_search = Button(2, 'search', player.download_lrc)
        btn_list_r = [btn_close, btn_full, btn_search]

        btn_lastlrc = Button(3, 'up', player.last_lrc)
        btn_nextlrc = Button(4, 'down', player.next_lrc)
        btn_list_r_lrc = [btn_lastlrc, btn_nextlrc]

        t_file = Text(ui_t_file_ft, ui_t_file_size, 'mu')
        t_msg = Text(ui_t_msg_ft, ui_t_msg_size, 'md')
        t_state = Text(ui_t_state_ft, ui_t_state_size, 'md')
        t_lrc = Text(ui_t_lrc_ft, ui_t_lrc_size, 'mm')
        t_prog = Text(ui_t_prog_ft, ui_t_prog_size, 'mm')
        t_tmr = Text(ui_t_tmr_ft, ui_t_tmr_size, 'mm')

        # 按键处理
        key_handling = {
            K_SPACE: lambda: player.play_pause(btn_play),
            K_UP: lambda: player.set_vol(player.get_vol() + 5),
            K_DOWN: lambda: player.set_vol(player.get_vol() - 5),
            K_LEFT: lambda: player.set_pos(player.get_pos() - 5000),
            K_RIGHT: lambda: player.set_pos(player.get_pos() + 5000),
            K_F11: window.set_fullscreen,
            K_ESCAPE: lambda: window.set_fullscreen(0)
        }

        mouse = False
        recul = True
        ui_btn_num = 15
        ui_sbtn_num = 5

    except Exception as e:
        msgbox('初始化出错:' + repr(e))
        exit()

    while True:
        try:
            for event in pygame.event.get():
                if event.type == QUIT:
                    exit()

                elif event.type == MOUSEBUTTONDOWN:
                    # 左键单击
                    if event.button == 1:
                        mouse = 1
                        for button in btn_list_d:
                            button.test_click(event.pos)

                        if player.is_timer_on():
                            btn_minus.test_click(event.pos)
                            btn_plus.test_click(event.pos)

                        if player.opened():
                            try:
                                if ui_prog_rect.collidepoint(event.pos):
                                    player.set_prog(
                                        (event.pos[0] - ui_prog_rect.left) / ui_prog_rect.width)
                            except BaseException:
                                pass

                            btn_back.test_click(event.pos)
                            btn_forward.test_click(event.pos)

                        if player.have_lrc():
                            for button in btn_list_r_lrc:
                                button.test_click(event.pos)

                        for button in btn_list_r:
                            button.test_click(event.pos)

                    # 滚轮下滑
                    elif event.button >= 5 and event.button % 2:
                        if player.opened():
                            try:
                                if ui_prog_rect.collidepoint(event.pos):
                                    player.set_pos(
                                        player.get_pos() + 200 * event.button)
                            except BaseException:
                                pass

                            if player.have_lrc():
                                try:
                                    if ui_lrc_rect.collidepoint(event.pos):
                                        player.next_lrc()
                                except BaseException:
                                    pass

                    # 滚轮上滑
                    elif event.button >= 4:
                        if player.opened():
                            try:
                                if ui_prog_rect.collidepoint(event.pos):
                                    player.set_pos(
                                        player.get_pos() - 200 * event.button)
                            except BaseException:
                                pass

                            if player.have_lrc():
                                try:
                                    if ui_lrc_rect.collidepoint(event.pos):
                                        player.last_lrc()
                                except BaseException:
                                    pass

                elif event.type == MOUSEBUTTONUP:
                    mouse = 0

                elif event.type == MOUSEMOTION:
                    if mouse:
                        if player.opened():
                            try:
                                if ui_prog_rect.collidepoint(event.pos):
                                    player.set_prog(
                                        (event.pos[0] - ui_prog_rect.left) / ui_prog_rect.width)
                            except BaseException:
                                pass

                elif event.type == USEREVENT:
                    player.music_end(btn_play)

                elif event.type == KEYDOWN:
                    if event.key in key_handling.keys():
                        key_handling[event.key]()

                elif event.type == VIDEORESIZE:
                    window.resize()

            if window.recul:
                window.recul = False
                ui_win_size_x, ui_win_size_y = window.size

                # 计算按钮大小及间距
                ui_btn_size, ui_bar_size, ui_btn_space = cul_btn(
                    ui_btn_num, ui_btn_max_size, ui_bar_max_size, ui_win_size_x, ui_win_size_y * ui_bar_max_prpt)
                ui_sbtn_size, ui_sbar_size, ui_sbtn_space = cul_btn(
                    ui_sbtn_num, ui_btn_max_size, ui_bar_max_size, ui_win_size_y * ui_sbar_max_prpt)

                # 侧边按钮不能大于底部按钮
                if ui_sbtn_size > ui_btn_size:
                    ui_sbtn_size, ui_sbar_size, ui_sbtn_space = ui_btn_size, ui_bar_size, ui_btn_space

                # 按钮位置列表
                ui_btn_rect_d = []
                ui_btn_rect_l = []
                ui_btn_rect_r = []
                for i in range(ui_btn_num):
                    rect = pygame.Rect(0, 0, ui_btn_size, ui_btn_size)
                    rect.center = ((i + 1) * ui_btn_space + (i + 0.5)
                                   * ui_btn_size, ui_win_size_y - ui_bar_size / 2)
                    ui_btn_rect_d.append(rect)
                for i in range(ui_sbtn_num):
                    rect = pygame.Rect(0, 0, ui_sbtn_size, ui_sbtn_size)
                    rect.center = (ui_sbar_size / 2, (i + 1) *
                                   ui_sbtn_space + (i + 0.5) * ui_sbtn_size)
                    ui_btn_rect_l.append(rect)
                    rect.center = (ui_win_size_x - ui_sbar_size / 2,
                                   (i + 1) * ui_sbtn_space + (i + 0.5) * ui_sbtn_size)
                    ui_btn_rect_r.append(rect)

                # X方向边界及宽度
                ui_list_ledge = ui_sbar_size + 10
                ui_list_redge = ui_win_size_x * ui_win_prpt - 12
                ui_list_mid = (ui_list_ledge + ui_list_redge) / 2
                ui_list_width = ui_list_redge - ui_list_ledge
                ui_music_ledge = ui_win_size_x * ui_win_prpt + 12
                ui_music_redge = ui_win_size_x - ui_sbar_size - 10
                ui_music_mid = (ui_music_ledge + ui_music_redge) / 2
                ui_music_width = ui_music_redge - ui_music_ledge

            # 填充背景
            if ui_bg_show_img:
                screen.blit(pygame.transform.scale(
                    ui_bg_img, (ui_win_size_x, ui_win_size_y)), (0, 0))
            else:
                screen.fill(ui_bg_col)

            # 显示按钮
            for button in btn_list_d:
                button.show(screen, ui_btn_rect_d[button.id])
            for button in btn_list_r:
                button.show(screen, ui_btn_rect_r[button.id])
            if player.have_lrc():
                for button in btn_list_r_lrc:
                    button.show(screen, ui_btn_rect_r[button.id])

            # 文件名
            ui_t_file_btm = t_file.show(
                screen,
                player.get_music_name(),
                ui_t_file_col,
                (ui_music_mid,
                 10),
                maxwidth=ui_music_width).bottom

            # 消息
            msg = player.get_msg()
            if msg:
                t_msg.show(
                    screen,
                    msg,
                    ui_t_msg_col,
                    (ui_list_mid,
                     ui_win_size_y -
                     ui_bar_size -
                     14),
                    maxwidth=ui_list_width)

            # 状态
            if not player.get_msg() and (player.opened() or player.is_timer_on()):
                ui_t_state_top = t_state.show(
                    screen,
                    player.get_state(),
                    ui_t_state_col,
                    (ui_win_size_x / 2,
                     ui_win_size_y - ui_bar_size - 14),
                    maxwidth=ui_win_size_x).top
            else:
                ui_t_state_top = t_state.show(
                    screen,
                    player.get_state(),
                    ui_t_state_col,
                    (ui_music_mid,
                     ui_win_size_y - ui_bar_size - 14),
                    maxwidth=ui_music_width).top

            if player.is_timer_on():
                # 定时器控制按钮
                btn_minus.show(
                    screen,
                    pygame.Rect(
                        10,
                        ui_t_state_top -
                        10 -
                        ui_tmr_wid,
                        ui_tmr_wid,
                        ui_tmr_wid))
                btn_plus.show(
                    screen,
                    pygame.Rect(
                        ui_win_size_x -
                        10 -
                        ui_tmr_wid,
                        ui_t_state_top -
                        10 -
                        ui_tmr_wid,
                        ui_tmr_wid,
                        ui_tmr_wid))

                # 定时器条
                ui_tmr_rect = pygame.Rect(
                    ui_tmr_wid + 20,
                    ui_t_state_top - 10 - ui_tmr_wid,
                    ui_win_size_x - ui_tmr_wid * 2 - 40,
                    ui_tmr_wid)
                pygame.draw.rect(screen, ui_tmr_col, ui_tmr_rect)

                # 已完成定时器条
                ui_tmr_past_rect = pygame.Rect(
                    ui_tmr_wid + 20,
                    ui_t_state_top - 10 - ui_tmr_wid,
                    (ui_win_size_x - ui_tmr_wid * 2 - 40) * player.get_timer_prog(),
                    ui_tmr_wid)
                pygame.draw.rect(screen, ui_tmr_past_col, ui_tmr_past_rect)

                # 定时器文字
                t_tmr.show(screen, player.get_timer_text(),
                           ui_t_tmr_col, ui_tmr_rect.center)

            if player.opened():
                # 计算进度区域下边界
                if player.is_timer_on():
                    ui_prog_btm = ui_tmr_rect.top - 10
                else:
                    ui_prog_btm = ui_t_state_top - 10

                # 进度控制按钮
                btn_back.show(screen, pygame.Rect(
                    10, ui_prog_btm - ui_prog_wid, ui_prog_wid, ui_prog_wid))
                btn_forward.show(
                    screen,
                    pygame.Rect(
                        ui_win_size_x -
                        10 -
                        ui_prog_wid,
                        ui_prog_btm -
                        ui_prog_wid,
                        ui_prog_wid,
                        ui_prog_wid))

                # 进度条
                ui_prog_rect = pygame.Rect(
                    ui_prog_wid + 20,
                    ui_prog_btm - ui_prog_wid,
                    ui_win_size_x - ui_prog_wid * 2 - 40,
                    ui_prog_wid)
                pygame.draw.rect(screen, ui_prog_col, ui_prog_rect)

                # 已完成进度条
                ui_prog_past_rect = pygame.Rect(
                    ui_prog_wid + 20,
                    ui_prog_btm - ui_prog_wid,
                    (ui_win_size_x - ui_prog_wid * 2 - 40) * player.get_prog(),
                    ui_prog_wid)
                pygame.draw.rect(screen, ui_prog_past_col, ui_prog_past_rect)

                # 进度文字
                t_prog.show(screen, player.get_time(),
                            ui_t_prog_col, ui_prog_rect.center)

                if player.have_lrc():
                    # 歌词区域
                    ui_lrc_rect = pygame.Rect(
                        ui_music_ledge,
                        ui_t_file_btm + 10,
                        ui_music_width,
                        ui_prog_rect.top - ui_t_file_btm - 20)

                    # 当前歌词
                    ui_lrc_cur_rect = t_lrc.show(
                        screen,
                        player.get_lrc(),
                        ui_t_lrc_cur_col,
                        (ui_music_mid,
                            (ui_t_file_btm + ui_prog_rect.top) / 2),
                        maxwidth=ui_music_width)

                    # 计算一方能显示的歌词数量（总数减一的一半）
                    ui_lrc_num = int(
                        (ui_prog_rect.top - ui_t_file_btm - 20 - ui_lrc_space) / ui_lrc_space / 2)

                    for i in range(1, ui_lrc_num + 1):
                        # 下方歌词
                        t_lrc.show(
                            screen,
                            player.get_lrc(i),
                            ui_t_lrc_col,
                            (ui_music_mid,
                             ui_lrc_cur_rect.centery +
                             i *
                             ui_lrc_space),
                            maxwidth=ui_music_width)

                        # 上方歌词
                        t_lrc.show(screen,
                                   player.get_lrc(-i),
                                   ui_t_lrc_col,
                                   (ui_music_mid,
                                    ui_lrc_cur_rect.centery - i * ui_lrc_space),
                                   maxwidth=ui_music_width)

            # 底部分界线
            pygame.draw.line(
                screen,
                ui_line_col,
                (0,
                 ui_win_size_y -
                 ui_bar_size -
                 2),
                (ui_win_size_x,
                 ui_win_size_y -
                 ui_bar_size -
                 2),
                4)

            # 中部分界线
            if player.opened():
                pygame.draw.line(
                    screen,
                    ui_line_col,
                    (ui_win_size_x *
                     ui_win_prpt,
                     0),
                    (ui_win_size_x *
                     ui_win_prpt,
                     ui_prog_rect.top -
                     10),
                    4)
            elif player.is_timer_on():
                pygame.draw.line(
                    screen,
                    ui_line_col,
                    (ui_win_size_x *
                     ui_win_prpt,
                     0),
                    (ui_win_size_x *
                     ui_win_prpt,
                     ui_tmr_rect.top -
                     10),
                    4)
            else:
                pygame.draw.line(
                    screen,
                    ui_line_col,
                    (ui_win_size_x *
                     ui_win_prpt,
                     0),
                    (ui_win_size_x *
                     ui_win_prpt,
                     ui_win_size_y -
                     ui_bar_size),
                    4)

            pygame.display.update()

        except Exception as e:
            if not ynbox(format_exc(), 'PyPigPlayer出错了,要继续运行吗?'):
                exit()
