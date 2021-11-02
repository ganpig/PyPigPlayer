import configparser
import os
import sys
import time
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = ''
title = 'PyPigPlayer v1.1.3'


def main():
    # 导入模块
    import pygame
    import core
    import ui

    # 初始化程序
    pygame.init()
    pygame.display.set_caption(title)
    pygame.key.set_repeat(500, 100)
    screen = pygame.display.set_mode((1000, 600), pygame.RESIZABLE)
    player = core.Player()
    volume = core.Volume()
    timer = core.Timer(player)
    lrc = core.Lrc()
    viewer = core.Viewer(player, lrc)

    # 解析配置和主题
    config = configparser.ConfigParser()
    config.read('config.ini')
    animation_show_time = config.getfloat('time', 'animation')
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
    error_height = theme.getint('error', 'height')
    error_color = pygame.color.THECOLORS[theme.get('error', 'color')]
    bg_pic = pygame.image.load(themefile('background.png'))

    # 创建文本
    def createtext(name, *args):
        return ui.Text(getfont(config.get('font', name)), pygame.color.THECOLORS[theme.get('fontcolor', name)], *args)

    dirname_text = createtext('dirname', 20, 30, 'mu')
    dirpath_text = createtext('dirpath', 15, 15, 'mu')
    filename_text = createtext('filename', 20, 30, 'mu')
    filepath_text = createtext('filepath', 15, 15, 'mu')
    item_text = createtext('item', 15, 25, 'lm')
    mid_lrc_text = createtext('lrc1', 15, 25)
    up_lrc_text = createtext('lrc2', 15, 25, 'md')
    down_lrc_text = createtext('lrc2', 15, 25, 'mu')
    progress_text = createtext('progress', 25, 25)
    timer_text = createtext('timer', 15, 15)
    volume_text = createtext('volume', 15, 15)
    error_text = createtext('error', 15, 25)

    # 创建按钮
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

    return_btn = ui.Button(getimg('return'), viewer.father, 'ld')
    last_btn = ui.Button(getimg('last'), viewer.last, 'rd')
    play_btn = ui.Button(getimg('play'), lambda: player.pause()
                         if player.playing else player.play(), 'md')
    next_btn = ui.Button(getimg('next'), viewer.next, 'ld')
    order_btn = ui.Button(
        getimg('order'), lambda: switchorder(order_btn), 'rd')
    buttons = [return_btn, last_btn,
               play_btn, next_btn, order_btn]

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

    # 调试模式
    debug_mode = False

    # 特殊按键
    ctrl = False
    shift = False

    # 错误信息
    error_msg = ''
    error_time = -float('inf')

    # 程序时钟
    clock = pygame.time.Clock()
    start_time = time.time()

    while True:
        try:
            # 计算运行时间
            total_time = time.time() - start_time

            # 更新窗口大小
            winw, winh = screen.get_size()

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
            showbutton(return_btn, space)
            draw_bottom = showbutton(play_btn, winw / 2)
            showbutton(last_btn, draw_bottom.left - space)
            showbutton(next_btn, draw_bottom.right + space)
            showbutton(order_btn, winw - space)
            draw_bottom.top -= space

            # 显示进度条
            if player.file:
                draw_bottom = main_prog.show(screen, draw_bottom.midtop, winw)
                draw_bottom.top -= space

            # 显示分割线
            mid_line = pygame.draw.line(screen, line_color, (winw / 2, 0),
                                        (winw / 2, draw_bottom.top * min(total_time / animation_show_time, 1)), line_width)

            # 显示文件夹名称和路径
            if os.name == 'nt' and viewer.path == '' or os.name == 'posix' and viewer.path == '/':
                dirname = '根目录'
            else:
                dirname = core.filename(viewer.path)
            draw_left = dirname_text.show(
                screen, dirname, (mid_line.left / 2, space), mid_line.left - space * 2)
            if viewer.path:
                draw_left = dirpath_text.show(
                    screen, viewer.path, (mid_line.left / 2, draw_left.bottom), mid_line.left - space * 2)
            draw_left.bottom += space

            # 显示文件名称和路径
            if not player.file:
                filename = '未打开文件'
            else:
                filename = core.filename(player.file)[:-4]
            draw_right = filename_text.show(screen, filename, ((
                mid_line.right + winw) / 2, space), mid_line.left - space * 2)
            if player.file:
                draw_right = filepath_text.show(screen, player.file, ((
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
                up_lrc = down_lrc = mid_lrc_text.show(screen, lrc.get_lrc(cur_lrc_id), ((
                    mid_line.right + winw) / 2, (draw_right.bottom + draw_bottom.top) / 2), mid_line.left - space * 2)
                while True:
                    up_lrc_id -= 1
                    if up_lrc_text.show(screen, lrc.get_lrc(
                            up_lrc_id), up_lrc.midtop, mid_line.left - space * 2, True).top >= draw_right.bottom:
                        up_lrc = up_lrc_text.show(screen, lrc.get_lrc(
                            up_lrc_id), up_lrc.midtop, mid_line.left - space * 2)
                    else:
                        break
                while True:
                    down_lrc_id += 1
                    if down_lrc_text.show(screen, lrc.get_lrc(
                            down_lrc_id), down_lrc.midbottom, mid_line.left - space * 2, True).bottom <= draw_bottom.top:
                        down_lrc = down_lrc_text.show(screen, lrc.get_lrc(
                            down_lrc_id), down_lrc.midbottom, mid_line.left - space * 2)
                    else:
                        break
                lrc_area = pygame.Rect(
                    mid_line.right, up_lrc.top, mid_line.left, down_lrc.bottom - up_lrc.top)

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

            # 显示错误信息
            if error_time+error_show_time > total_time:
                error_width = winw-space*2
                error_rect = ui.aligner(pygame.Rect(
                    0, 0, error_width, error_height), 'md', (winw/2, min((total_time-error_time)*100, 50)))
                pygame.draw.rect(screen, error_color, error_rect,
                                 border_radius=error_height//2)
                error_text.show(screen, error_msg,
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

            # 刷新窗口
            pygame.display.update()

        except Exception as e:
            error_msg = str(e)
            error_time = total_time


if __name__ == '__main__':
    main()
