import configparser
import os
import sys
import time
import traceback

import pygame

import core
import ui
from init import *


def main():
    # 初始化窗口
    pygame.init()
    pygame.display.set_caption(title)
    pygame.key.set_repeat(500, 100)
    screen = pygame.display.set_mode((1000, 600), pygame.RESIZABLE)

    # 初始化类
    player = core.Player()
    volume = core.Volume()
    timer = core.Timer(player)
    lrc = core.Lrc()
    viewer = core.Viewer(player, lrc)

    # 程序变量
    debug_mode = False
    ctrl = False
    shift = False

    # 解析配置和主题
    config = configparser.ConfigParser()
    config.read('config.ini')
    animation_show_time = config.getfloat('time', 'animation')
    msg_show_time = config.getfloat('time', 'msg')
    error_show_time = config.getfloat('time', 'error')
    theme_path = os.path.join('Themes', config.get('theme', 'theme'))

    def themefile(name):
        return os.path.join(theme_path, name)

    def getimg(name):
        return pygame.image.load(themefile(name + '.png'))

    def getfont(name):
        return os.path.join('Fonts', name)

    theme = configparser.ConfigParser()
    theme.read(themefile('theme.ini'))
    space = theme.getint('global', 'space')
    button_size = theme.getint('button', 'size')
    viewer_line_width = theme.getint('viewerline', 'width')
    viewer_line_color = pygame.color.THECOLORS[theme.get(
        'viewerline', 'color')]
    line_width = theme.getint('line', 'width')
    line_color = pygame.color.THECOLORS[theme.get('line', 'color')]
    item_images = theme.getint('item', 'images')
    item_height = theme.getint('item', 'height')
    msg_height = theme.getint('msg', 'height')
    msg_color = pygame.color.THECOLORS[theme.get('msg', 'color')]
    error_height = theme.getint('error', 'height')
    error_color = pygame.color.THECOLORS[theme.get('error', 'color')]
    bg_pic = pygame.image.load(themefile('background.png'))

    # 创建文本
    def createtext(name, *args):
        fontname = getfont(config.get('font', name))
        fontcolor = pygame.color.THECOLORS[theme.get('fontcolor', name)]
        maxsize = theme.getint('fontsize', name)
        return ui.Text(fontname, fontcolor, maxsize//2, maxsize, *args)

    dirname_text = createtext('dirname', 'mu')
    dirpath_text = createtext('dirpath', 'mu')
    filename_text = createtext('filename', 'mu')
    filepath_text = createtext('filepath', 'mu')
    item_text = createtext('item', 'lm')
    mid_lrc_text = createtext('lrc1')
    up_lrc_text = createtext('lrc2')
    down_lrc_text = createtext('lrc2')
    progress_text = createtext('progress')
    timer_text = createtext('timer')
    volume_text = createtext('volume')
    msg_text = createtext('msg')
    error_text = createtext('error')

    # 切换播放顺序
    def switchorder(btn):
        if btn.data == 0:
            viewer.switch(1)
            btn.data = 1
            btn.img = getimg('repeat')
        elif btn.data == 1:
            viewer.switch(2)
            btn.data = 2
            btn.img = getimg('random')
        elif btn.data == 2:
            viewer.switch(0)
            btn.data = 0
            btn.img = getimg('order')

    # 创建按钮
    return_btn = ui.Button(getimg('return'), viewer.father, 'ld')
    search_btn = ui.Button(
        getimg('search'), lambda: start_thread(viewer.search_online), 'ld')
    top_btn = ui.Button(
        getimg('toplist'), viewer.tops, 'ld')
    last_btn = ui.Button(getimg('last'), viewer.last, 'rd')
    play_btn = ui.Button(getimg('play'), lambda: start_thread(
        player.pause if player.playing else player.play), 'md')
    next_btn = ui.Button(getimg('next'), viewer.next, 'ld')
    download_btn = ui.Button(
        getimg('download'), lambda: start_thread(viewer.save), 'rd')
    order_btn = ui.Button(
        getimg('order'), lambda: switchorder(order_btn), 'rd')
    buttons = [return_btn, search_btn, top_btn, last_btn,
               play_btn, next_btn, download_btn, order_btn]

    # 创建进度条
    def createprog(name, *args):
        return ui.Progbar(theme.getint(name, 'width'), theme.get(
            name, 'color1'), theme.get(name, 'color2'), *args)

    main_prog = createprog('progress', player.get_prog,
                           player.set_prog, player.get_text, progress_text, 'md')
    volume_prog = createprog(
        'volume', volume.get_volume, volume.set_volume, volume.get_text, volume_text, 'lu', True)
    timer_prog = createprog(
        'timer', timer.get_prog, timer.set_prog, timer.get_text, timer_text, 'ru', True)
    progress_bars = [main_prog, volume_prog, timer_prog]

    # 创建时钟
    clock = pygame.time.Clock()
    start_time = time.time()

    while True:
        try:
            # 计算运行时间
            total_time = time.time() - start_time

            # 更新窗口大小
            winw, winh = screen.get_size()

            # 更新窗口标题
            if info.changed:
                if info.query():
                    pygame.display.set_caption(title+' | '+info.query())
                else:
                    pygame.display.set_caption(title)

            # 填充背景图片
            screen.blit(pygame.transform.scale(bg_pic, (winw, winh)), (0, 0))

            # 显示按钮
            def showbutton(btn, xpos):
                if total_time < animation_show_time:
                    ypos = winh + button_size - \
                        (button_size + space) * \
                        (total_time / animation_show_time)**2
                else:
                    ypos = winh - space
                return btn.show(screen, (xpos, ypos), width=button_size)

            play_btn.img = getimg('pause' if player.playing else 'play')
            draw_left = showbutton(return_btn, space)
            draw_left = showbutton(search_btn, draw_left.right + space)
            showbutton(top_btn, draw_left.right + space)
            draw_bottom = showbutton(play_btn, winw / 2)
            showbutton(last_btn, draw_bottom.left - space)
            showbutton(next_btn, draw_bottom.right + space)
            draw_right = showbutton(order_btn, winw - space)
            if viewer.downloadable:
                showbutton(download_btn, draw_right.left-space)
            else:
                download_btn.noshow()
            draw_bottom.top -= space

            # 显示进度条
            if player.file:
                draw_bottom = main_prog.show(screen, draw_bottom.midtop, winw)
                draw_bottom.top -= space

            # 显示分割线
            mid_line = pygame.draw.line(screen, line_color, (winw / 2, 0),
                                        (winw / 2, draw_bottom.top * min(total_time / animation_show_time, 1)), line_width)

            # 显示文件夹名称和路径
            draw_left = dirname_text.show(
                screen, viewer.page, (mid_line.left / 2, space), mid_line.left - space * 2)
            if viewer.page2:
                draw_left = dirpath_text.show(
                    screen, viewer.page2, (mid_line.left / 2, draw_left.bottom), mid_line.left - space * 2)
            draw_left.bottom += space

            # 显示文件名称和路径
            draw_right = filename_text.show(screen, viewer.playing, ((
                mid_line.right + winw) / 2, space), mid_line.left - space * 2)
            if viewer.playing2:
                draw_right = filepath_text.show(screen, viewer.playing2, ((
                    mid_line.right + winw) / 2, draw_right.bottom), mid_line.left - space * 2)
            draw_right.bottom += space

            # 显示文件浏览器
            item_num = (draw_bottom.top - draw_left.bottom +
                        space) // (item_height + space)
            viewer.viewid = max(
                min(viewer.viewid, len(viewer.showitems) - item_num), 0)
            items = []
            for i in range(min(item_num, len(viewer.showitems) - viewer.viewid)):
                itemid = viewer.viewid + i
                item = viewer.showitems[itemid]
                item_screen = pygame.transform.scale(
                    getimg(f'item{itemid%item_images}'), (mid_line.left - space * 2, item_height))
                item_icon = item_screen.blit(
                    ui.scale(getimg(item.icon), height=item_height-space*2), (item_screen.get_width()*0.05, space))
                item_text.show(item_screen, item.name, (item_icon.right+space, item_icon.centery),
                               item_screen.get_width() - item_icon.right-space * 2)
                item_button = ui.Button(
                    item_screen, viewer.showitems[itemid], 'mu')
                items.append(item_button)
                item_button.show(
                    screen, (mid_line.left / 2, draw_left.bottom + (item_height + space) * i))
            viewer_area = pygame.Rect(
                0, draw_left.bottom, mid_line.left, draw_bottom.top - draw_left.bottom)
            if total_time >= 0.5 and len(viewer.showitems):
                viewer_prog = ui.aligner(pygame.Rect(
                    0, 0, viewer_line_width, viewer_area.height*min(item_num/len(viewer.showitems), 1)), 'ru',
                    (mid_line.left, viewer_area.top+viewer_area.height*viewer.viewid/len(viewer.showitems)))
                pygame.draw.rect(screen, viewer_line_color, viewer_prog,
                                 border_radius=viewer_line_width//2)

            # 显示音量和定时器
            volume_prog.show(
                screen, (mid_line.right + space, draw_right.bottom), (mid_line.left - space * 3) / 2)
            draw_right = timer_prog.show(
                screen, (winw - space, draw_right.bottom), (mid_line.left - space * 3) / 2)
            draw_right.bottom += space

            # 显示歌词
            if lrc.lrc:
                up_lrc_id = down_lrc_id = cur_lrc_id = lrc.get_lrc_id(
                    player.get_pos())
                each_width = mid_lrc_text.show(
                    screen, 'test', (0, 0), noshow=True).height
                coming = max(0.5+player.get_pos() -
                             lrc.get_mark(cur_lrc_id+1), 0)*2*each_width
                mid_lrc = mid_lrc_text.show(screen, lrc.get_lrc(cur_lrc_id), ((
                    mid_line.right + winw) / 2, (draw_right.bottom + draw_bottom.top) / 2-coming), mid_line.left - space * 2)
                up_lrc = [mid_lrc.centerx, mid_lrc.centery - each_width-space]
                down_lrc = [mid_lrc.centerx,
                            mid_lrc.centery + each_width+space]
                while True:
                    up_lrc_id -= 1
                    if up_lrc_text.show(screen, lrc.get_lrc(
                            up_lrc_id), up_lrc, mid_line.left - space * 2, True).top >= draw_right.bottom:
                        up_lrc_text.show(screen, lrc.get_lrc(
                            up_lrc_id), up_lrc, mid_line.left - space * 2)
                        up_lrc[1] -= each_width+space
                    else:
                        break
                while True:
                    down_lrc_id += 1
                    if down_lrc_text.show(screen, lrc.get_lrc(
                            down_lrc_id), down_lrc, mid_line.left - space * 2, True).bottom <= draw_bottom.top:
                        down_lrc_text.show(screen, lrc.get_lrc(
                            down_lrc_id), down_lrc, mid_line.left - space * 2)
                        down_lrc[1] += each_width+space
                    else:
                        break
                lrc_area = pygame.Rect(
                    mid_line.right, up_lrc[1], mid_line.left, down_lrc[1] - up_lrc[1])

            # 遍历事件列表
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    def pressed(key):
                        return event.key == key and keys[key]

                    keys = pygame.key.get_pressed()
                    if ctrl:
                        if pressed(pygame.K_m):
                            switchorder(order_btn)
                        elif pressed(pygame.K_UP):
                            volume.set_volume(1)
                        elif pressed(pygame.K_DOWN):
                            volume.set_volume(0)
                    elif pressed(pygame.K_LCTRL) or pressed(pygame.K_RCTRL):
                        ctrl = True
                    elif pressed(pygame.K_LSHIFT) or pressed(pygame.K_RSHIFT):
                        shift = True
                    elif pressed(pygame.K_SPACE):
                        if player.playing:
                            player.pause()
                        else:
                            player.play()
                    elif pressed(pygame.K_LEFT):
                        player.set_pos(player.get_pos() - 5)
                    elif pressed(pygame.K_RIGHT):
                        player.set_pos(player.get_pos() + 5)
                    elif pressed(pygame.K_UP):
                        volume.set_volume(round(volume.get_volume() + 0.05, 2))
                    elif pressed(pygame.K_DOWN):
                        volume.set_volume(round(volume.get_volume() - 0.05, 2))
                    elif pressed(pygame.K_MINUS):
                        timer.set_time(timer.get_time() - 300)
                    elif pressed(pygame.K_EQUALS):
                        timer.set_time(timer.get_time() + 300)
                    elif pressed(pygame.K_RETURN) and lrc.lrc:
                        if shift:
                            if cur_lrc_id >= 0:
                                player.set_pos(
                                    lrc.mark[cur_lrc_id - 1] if cur_lrc_id else 0)
                        else:
                            if cur_lrc_id + 1 < len(lrc.mark):
                                player.set_pos(lrc.mark[cur_lrc_id + 1])
                    elif pressed(pygame.K_F12):
                        debug_mode = not debug_mode

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                        ctrl = False
                    elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        shift = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for element in buttons + progress_bars + items:
                            element.click(event.pos)
                    elif event.button == 4:
                        if lrc.lrc and lrc_area.collidepoint(
                                event.pos) and cur_lrc_id >= 0:
                            player.set_pos(
                                lrc.mark[cur_lrc_id - 1] if cur_lrc_id else 0)
                        if viewer_area.collidepoint(event.pos):
                            viewer.viewid -= 1
                    elif event.button == 5:
                        if lrc.lrc and lrc_area.collidepoint(
                                event.pos) and cur_lrc_id + 1 < len(lrc.mark):
                            player.set_pos(lrc.mark[cur_lrc_id + 1])
                        if viewer_area.collidepoint(event.pos):
                            viewer.viewid += 1

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        for prog in progress_bars:
                            prog.mouse_up()

                elif event.type == pygame.MOUSEMOTION:
                    for prog in progress_bars:
                        prog.drag(event.pos)

                elif event.type == pygame.USEREVENT:
                    viewer.end()

            # 显示提醒信息
            if msg.time() <= msg_show_time:
                msg_width = winw-space*2
                msg_rect = ui.aligner(pygame.Rect(
                    0, 0, msg_width, msg_height), 'md', (winw/2, min((err.time()*100, 50))))
                pygame.draw.rect(screen, msg_color, msg_rect,
                                 border_radius=msg_height//2)
                msg_text.show(screen, msg.query(),
                              msg_rect.center, msg_width-space*2)

            # 显示错误信息
            if err.time() <= error_show_time:
                error_width = winw-space*2
                error_rect = ui.aligner(pygame.Rect(
                    0, 0, error_width, error_height), 'md', (winw/2, min((err.time()*100, 50))))
                pygame.draw.rect(screen, error_color, error_rect,
                                 border_radius=error_height//2)
                error_text.show(screen, err.query(),
                                error_rect.center, error_width-space*2)

            # 刷新时钟
            clock.tick()

            # 显示调试信息
            if debug_mode:
                def show_msg(text, align, pos):
                    render = font.render(text, True, (127, 127, 127))
                    screen.blit(render, ui.aligner(
                        render.get_rect(), align, pos))

                font = pygame.font.SysFont(None, 20)
                show_msg(time.strftime('%Y-%m-%d %H:%M:%S',
                                       time.localtime()), 'lu', (0, 0))
                show_msg(str(pygame.mouse.get_pos()), 'ru', (winw, 0))
                show_msg(str(clock.get_fps()) + ' fps', 'ld', (0, winh))
                show_msg('Debug mode', 'rd', (winw, winh))

        except Exception as e:
            traceback.print_exc()
            err.set(str(e))

        # 刷新窗口
        pygame.display.update()


if __name__ == '__main__':
    main()
