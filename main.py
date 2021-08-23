import pygame
from easygui import msgbox, ynbox
from ppp_button import Button
from ppp_config import Config
from ppp_func import *
from ppp_player import Player
from ppp_text import Text
from ppp_window import Window
from sys import exit
from traceback import format_exc


if __name__ == '__main__':
    try:
        config = Config('config.ini')

        config.get_section('program')
        ver = config.get('version')

        config.get_section('window')
        windflt = config.get_tuple('default_size')
        winmin = config.get_tuple('min_size')
        winprpt = config.get_int('left_proportion') / 100

        config.get_section('button')
        btnmax = config.get_int('button_max_size')
        barmax = config.get_int('bar_max_size')
        barprpt = config.get_int('bar_max_proportion') / 100
        sbarprpt = config.get_int('sidebar_max_proportion') / 100

        config.get_section('line')
        lnwid = config.get_int('width')
        lncol = config.get_color('color')

        config.get_section('background')
        shimg = config.get_int('show_image')
        if shimg:
            bgimg = pygame.image.load(config.get_file('image'))
        else:
            bgcol = config.get_color('color')

        config.get_section('filename')
        fileft = config.get('font')
        filecol = config.get_color('color')
        filesize = config.get_tuple('size')

        config.get_section('message')
        msgft = config.get('font')
        msgcol = config.get_color('color')
        msgsize = config.get_tuple('size')

        config.get_section('state')
        stateft = config.get('font')
        statecol = config.get_color('color')
        statesize = config.get_tuple('size')

        config.get_section('lrc')
        lrcft = config.get('font')
        lrccol1 = config.get_color('color1')
        lrccol2 = config.get_color('color2')
        lrcsize = config.get_tuple('size')

        config.get_section('progress')
        progwid = config.get_int('width')
        progft = config.get('font')
        progsize = config.get_tuple('size')
        progcol = config.get_color('color')
        progcol1 = config.get_color('color1')
        progcol2 = config.get_color('color2')

        config.get_section('timer')
        tmrwid = config.get_int('width')
        tmrft = config.get('font')
        tmrsize = config.get_tuple('size')
        tmrcol = config.get_color('color')
        tmrcol1 = config.get_color('color1')
        tmrcol2 = config.get_color('color2')

        config.get_section('repeatkey')
        delay = config.get_int('delay')
        interval = config.get_int('interval')

    except Exception as e:
        msgbox('读取配置出错:' + repr(e))
        exit()

    try:
        pygame.init()
        window = Window(windflt, winmin, 'PyPigPlayer ' + ver)
        screen = window.getscreen()
        player = Player()
        pygame.key.set_repeat(delay, interval)

        btn_back = Button(-1, 'back',
                          lambda: player.set_pos(player.get_pos() - 5000))
        btn_forward = Button(-1, 'forward',
                             lambda: player.set_pos(player.get_pos() + 5000))
        btn_minus = Button(-1, 'minus',
                           lambda: player.set_timer(player.get_timer() - 5))
        btn_plus = Button(-1, 'plus',
                          lambda: player.set_timer(player.get_timer() + 5))

        btn_time = Button(0, 'time', player.on_off_timer)
        btn_mode = Button(1, 'mode', lambda: msgbox('该功能尚在开发'))
        btn_open = Button(2, 'open', lambda: player.open_file(btn_play))
        btn_last = Button(6, 'last', lambda: msgbox('该功能尚在开发'))
        btn_play = Button(7, 'play', lambda: player.play_pause(btn_play))
        btn_next = Button(8, 'next', lambda: msgbox('该功能尚在开发'))
        btn_repeat = Button(
            12, 'repeat0', lambda: player.set_repeat_mode(btn_repeat))
        btn_volm = Button(
            13, 'vol-', lambda: player.set_vol(player.get_vol() - 5))
        btn_volp = Button(
            14, 'vol+', lambda: player.set_vol(player.get_vol() + 5))
        d_list = [btn_time, btn_mode, btn_open, btn_last, btn_play,
                  btn_next, btn_repeat, btn_volm, btn_volp]

        btn_close = Button(0, 'close', exit)
        btn_full = Button(1, 'fullscreen', window.set_fullscreen)
        r_list = [btn_close, btn_full]

        btn_lastlrc = Button(2, 'up', player.last_lrc)
        btn_nextlrc = Button(3, 'down', player.next_lrc)
        r_list_lrc = [btn_lastlrc, btn_nextlrc]

        btn_search = Button(2, 'search', player.download_lrc)
        r_list_mp3 = [btn_search]

        t_file = Text(fileft, filesize, 'mu')
        t_msg = Text(msgft, msgsize, 'md')
        t_state = Text(stateft, statesize, 'md')
        t_lrc = Text(lrcft, lrcsize, 'mm')
        t_prog = Text(progft, progsize, 'mm')
        t_tmr = Text(tmrft, tmrsize, 'mm')

        mouse = 0

    except Exception as e:
        msgbox('初始化出错:' + repr(e))
        exit()

    while True:
        try:
            sizex, sizey = window.getsize()
            if window.need_repaint():
                d_num = 15
                l_num = 4
                r_num = 4
                d_bt, d_bar, d_space = cul_btn(
                    d_num, btnmax, barmax, sizex, sizey * barprpt)
                l_bt, l_bar, l_space = cul_btn(
                    l_num, btnmax, barmax, sizey * sbarprpt)
                if l_bt > d_bt:
                    l_bt, l_bar, l_space = d_bt, d_bar, d_space
                r_bt, r_bar, r_space = cul_btn(
                    r_num, btnmax, barmax, sizey * sbarprpt)
                if r_bt > d_bt:
                    r_bt, r_bar, r_space = d_bt, d_bar, d_space
                d_pos = [((i + 1) * d_space + (i + 0.5) * d_bt,
                          sizey - d_bar / 2) for i in range(d_num)]
                l_pos = [(l_bar / 2, (i + 1) * l_space + (i + 0.5) * l_bt)
                         for i in range(l_num)]
                r_pos = [(sizex - r_bar / 2, (i + 1) * r_space +
                          (i + 0.5) * r_bt) for i in range(r_num)]
                lledge = 10
                lmedge = l_bar + 10
                lredge = sizex * winprpt - 12
                lmid = (lledge + lredge) / 2
                lwidth = lredge - lledge
                lmmid = (lmedge + lredge) / 2
                lmwidth = lredge - lmedge
                rledge = sizex * winprpt + 12
                rmedge = sizex - r_bar - 10
                rredge = sizex - 10
                rmid = (rledge + rredge) / 2
                rwidth = rredge - rledge
                rmmid = (rledge + rmedge) / 2
                rmwidth = rmedge - rledge

            if shimg:
                screen.blit(pygame.transform.scale(
                    bgimg, (sizex, sizey)), (0, 0))
            else:
                screen.fill(bgcol)

            for button in d_list:
                button.show(screen, d_pos[button.id], d_bt)
            for button in r_list:
                button.show(screen, r_pos[button.id], r_bt)
            if player.opened():
                if player.have_lrc():
                    for button in r_list_lrc:
                        button.show(screen, r_pos[button.id], r_bt)
                else:
                    for button in r_list_mp3:
                        button.show(screen, r_pos[button.id], r_bt)

            lrctop = t_file.show(screen,
                                 player.get_music_name(), filecol,
                                 (rmmid, 10),
                                 maxwidth=rmwidth).bottom + 10
            msg = player.get_msg()
            if msg:
                t_msg.show(screen,
                           msg,
                           msgcol,
                           (lmmid, sizey - d_bar - 14),
                           maxwidth=lmwidth)
            progbtm = tmrbtm = t_state.show(
                screen,
                player.get_state(),
                statecol,
                (sizex / 2,
                 sizey - d_bar - 14),
                maxwidth=rredge - lledge).top - 10 if not player.get_msg() and (
                player.opened() or player.is_timer_on()) else t_state.show(
                screen,
                player.get_state(),
                statecol,
                (rmmid,
                 sizey - d_bar - 14),
                maxwidth=rmwidth).top - 10
            if player.is_timer_on():
                btn_minus.show(
                    screen, (tmrwid / 2 + 10, tmrbtm - tmrwid / 2), tmrwid)
                btn_plus.show(screen, (sizex - tmrwid / 2 - 10,
                              tmrbtm - tmrwid / 2), tmrwid)
                tmrrt = pygame.Rect(tmrwid + 20,
                                    tmrbtm - tmrwid,
                                    sizex - tmrwid * 2 - 40,
                                    tmrwid)
                progbtm = tmrrt.top - 10
                pygame.draw.rect(screen,
                                 tmrcol2,
                                 tmrrt)
                pygame.draw.rect(screen,
                                 tmrcol1,
                                 pygame.Rect(tmrwid + 20,
                                             tmrbtm - tmrwid,
                                             (sizex - tmrwid * 2 - 40) *
                                             player.get_timer_prog(),
                                             tmrwid))
                t_tmr.show(screen, player.get_timer_text(),
                           tmrcol, tmrrt.center)
            if player.opened():
                btn_back.show(
                    screen, (progwid / 2 + 10, progbtm - progwid / 2), progwid)
                btn_forward.show(screen, (sizex - progwid / 2 - 10,
                                 progbtm - progwid / 2), progwid)
                progrt = pygame.Rect(progwid + 20,
                                     progbtm - progwid,
                                     sizex - progwid * 2 - 40,
                                     progwid)
                lrcbtm = progrt.top - 10
                pygame.draw.rect(screen,
                                 progcol2,
                                 progrt)
                pygame.draw.rect(screen,
                                 progcol1,
                                 pygame.Rect(progwid + 20,
                                             progbtm - progwid,
                                             (sizex - progwid * 2 - 40) *
                                             player.get_prog(),
                                             progwid))
                t_prog.show(screen, player.get_time(), progcol, progrt.center)
                if player.have_lrc():
                    lrcsp, lrcrt = t_lrc.show(screen,
                                              player.get_lrc(0),
                                              lrccol1,
                                              (rmmid,
                                               (lrctop + lrcbtm) / 2),
                                              maxwidth=rmwidth,
                                              getheight=True)
                    lrcnum = int((lrcrt.top - lrctop) / lrcsp)
                    for i in range(1, lrcnum + 1):
                        t_lrc.show(screen,
                                   player.get_lrc(-i),
                                   lrccol2,
                                   (rmmid,
                                    lrcrt.centery - i * lrcsp),
                                   maxwidth=rmwidth,
                                   maxheight=lrcsp)
                        t_lrc.show(screen,
                                   player.get_lrc(i),
                                   lrccol2,
                                   (rmmid,
                                    lrcrt.centery + i * lrcsp),
                                   maxwidth=rmwidth,
                                   maxheight=lrcsp)
            pygame.draw.line(screen,
                             lncol,
                             (0, sizey - d_bar - 2),
                             (sizex, sizey - d_bar - 2),
                             4)
            pygame.draw.line(
                screen,
                lncol,
                (sizex *
                 winprpt,
                 0),
                (sizex *
                 winprpt,
                 lrcbtm if player.opened() else progbtm if player.is_timer_on() else sizey -
                 d_bar),
                4)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse = 1
                    if player.opened():
                        if progrt.collidepoint(event.pos):
                            player.set_prog(
                                (event.pos[0] - progrt.left) / progrt.width)
                    for button in d_list:
                        button.test_click(event.pos)
                    if player.is_timer_on():
                        btn_minus.test_click(event.pos)
                        btn_plus.test_click(event.pos)
                    if player.opened():
                        btn_back.test_click(event.pos)
                        btn_forward.test_click(event.pos)
                        if player.have_lrc():
                            for button in r_list_lrc:
                                button.test_click(event.pos)
                        else:
                            for button in r_list_mp3:
                                button.test_click(event.pos)
                    for button in r_list:
                        button.test_click(event.pos)

                if event.type == pygame.MOUSEBUTTONUP:
                    mouse = 0

                if event.type == pygame.MOUSEMOTION:
                    if mouse:
                        if player.opened():
                            if progrt.collidepoint(event.pos):
                                player.set_prog(
                                    (event.pos[0] - progrt.left) / progrt.width)

                if event.type == pygame.USEREVENT:
                    player.music_end(btn_play)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.play_pause(btn_play)
                    if event.key == pygame.K_UP:
                        player.set_vol(player.get_vol() + 5)
                    if event.key == pygame.K_DOWN:
                        player.set_vol(player.get_vol() - 5)
                    if event.key == pygame.K_LEFT:
                        player.set_pos(player.get_pos() - 5000)
                    if event.key == pygame.K_RIGHT:
                        player.set_pos(player.get_pos() + 5000)
                    if event.key == pygame.K_F11:
                        window.set_fullscreen()
                    if event.key == pygame.K_ESCAPE:
                        window.set_fullscreen(0)

            pygame.display.update()

        except Exception as e:
            if not ynbox(format_exc(), 'PyPigPlayer出错了,要继续运行吗?'):
                exit()
