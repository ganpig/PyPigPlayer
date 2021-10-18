import _thread
import configparser
import os
import sys
import time
import traceback

import easygui
import pygame

import core
import ui

title = 'PyPigPlayer v1.0'


def main():
    try:
        # 初始化程序
        pygame.init()
        pygame.key.set_repeat(500, 100)
        pygame.display.set_caption(title)
        screen = pygame.display.set_mode((1000, 600), pygame.RESIZABLE)
        player = core.Player()
        volume = core.Volume()
        timer = core.Timer(player)
        lrc = core.Lrc()
        viewer = core.Viewer(player, lrc)

        # 解析主题
        def themefile(name):
            return os.path.join(themepath, name)

        def getimg(name):
            return pygame.image.load(themefile(name + '.png'))

        theme = configparser.ConfigParser()
        themepath = os.path.join('theme', open('theme.txt').readline())
        theme.read(themefile('theme.ini'))
        space = theme.getint('global', 'space')
        button_size = theme.getint('global', 'button_size')
        line_width = theme.getint('global', 'line_width')
        line_color = pygame.color.THECOLORS[theme.get('global', 'line_color')]
        item_images = theme.getint('global', 'item_images')
        item_height = theme.getint('global', 'item_height')
        bg_pic = pygame.image.load(themefile('background.png'))

        # 创建文本
        def createtext(name, *args):
            return ui.Text(themefile(theme.get(name, 'font')),
                           pygame.color.THECOLORS[theme.get(name, 'color')], *args)

        dirname_text = createtext('dirname', 20, 30, 'mu')
        dirpath_text = createtext('dirpath', 15, 15, 'mu')
        filename_text = createtext('filename', 20, 30, 'mu')
        filepath_text = createtext('filepath', 15, 15, 'mu')
        item_text = createtext('item', 15, 25)
        mid_lrc_text = createtext('lrc1', 15, 25)
        up_lrc_text = createtext('lrc2', 15, 25, 'md')
        down_lrc_text = createtext('lrc2', 15, 25, 'mu')
        progress_text = createtext('progress', 25, 25)
        timer_text = createtext('timer', 15, 15)
        volume_text = createtext('volume', 15, 15)

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

        open_btn = ui.Button(getimg('open'), viewer.open, 'ld')
        last_btn = ui.Button(getimg('last'), viewer.last, 'rd')
        play_btn = ui.Button(getimg('play'), lambda: player.pause()
                             if player.playing else player.play(), 'md')
        next_btn = ui.Button(getimg('next'), viewer.next, 'ld')
        order_btn = ui.Button(
            getimg('order'), lambda: switchorder(order_btn), 'rd')
        buttons = [open_btn, last_btn,
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

        # 程序时钟
        clock = pygame.time.Clock()
        start_time = time.time()

        while True:
            # 计算运行时间
            total_time = time.time() - start_time

            # 更新窗口大小
            winw, winh = screen.get_size()

            # 填充背景图片
            screen.blit(pygame.transform.scale(bg_pic, (winw, winh)), (0, 0))

            # 显示按钮
            def showbutton(btn, xpos):
                if total_time < 0.5:
                    ypos = winh + button_size - \
                        (button_size + space) * (total_time * 2)**2
                else:
                    ypos = winh - space
                return btn.show(screen, (xpos, ypos), width=button_size)

            play_btn.img = getimg('pause' if player.playing else 'play')
            showbutton(open_btn, space)
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
                                        (winw / 2, draw_bottom.top * min(total_time * 2, 1)), line_width)

            # 显示文件夹名称和路径
            draw_left = dirname_text.show(screen, viewer.path.split(
                os.path.sep)[-1] if viewer.path else title, (mid_line.left / 2, space), mid_line.left - space * 2)
            if viewer.path:
                draw_left = dirpath_text.show(
                    screen, viewer.path, (mid_line.left / 2, draw_left.bottom), mid_line.left - space * 2)
            draw_left.bottom += space

            # 显示文件名称和路径
            draw_right = filename_text.show(screen, player.file.split(
                os.path.sep)[-1][:-4] if player.file else '未打开文件', ((mid_line.right + winw) / 2, space), mid_line.left - space * 2)
            if player.file:
                draw_right = filepath_text.show(screen, player.file, ((
                    mid_line.right + winw) / 2, draw_right.bottom), mid_line.left - space * 2)
            draw_right.bottom += space

            # 显示文件浏览器
            item_num = (draw_bottom.top - draw_left.bottom +
                        space) // (item_height + space)
            viewer.viewid = max(
                min(viewer.viewid, len(viewer.items) - item_num), 0)
            items = []
            for i in range(min(item_num, len(viewer.items) - viewer.viewid)):
                class itemplay:
                    def __init__(self):
                        self.id = itemid

                    def __call__(self):
                        viewer.playid(self.id)

                itemid = viewer.viewid + i
                item_screen = pygame.transform.scale(pygame.image.load(themefile(
                    f'item{itemid%item_images}.png')), (mid_line.left - space * 2, item_height))
                item_text.show(item_screen, viewer.items[itemid], item_screen.get_rect().center,
                               item_screen.get_width() - space * 2)
                item_button = ui.Button(
                    item_screen, itemplay(), 'mu')
                items.append(item_button)
                item_button.show(
                    screen, (mid_line.left / 2, draw_left.bottom + (item_height + space) * i))
            viewer_area = pygame.Rect(
                0, draw_left.bottom, mid_line.left, draw_bottom.top - draw_left.bottom)

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
                        if pressed(pygame.K_o):
                            if debug_mode and shift:
                                player.open(easygui.fileopenbox())
                            else:
                                _thread.start_new_thread(viewer.open, ())
                        elif pressed(pygame.K_s) and debug_mode:
                            pygame.image.save(
                                screen, easygui.filesavebox(default='snapshot.png'))
                        elif pressed(pygame.K_m):
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

    except Exception:
        if easygui.ynbox(traceback.format_exc(),
                         '出错了! - ' + title, ('重启', '退出')):
            pygame.quit()
        else:
            sys.exit()


if __name__ == '__main__':
    while True:
        main()
