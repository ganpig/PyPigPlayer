import pygame


class Text():
    def __init__(self, font, size, align):
        self.font = f'font/{font}.ttf'
        self.minsize, self.maxsize = size
        self.align = align

    def show(self, screen, text, color, pos, maxwidth=10000, maxheight=10000, getwidth=False, getheight=False):
        ret = []

        size = self.maxsize
        render = pygame.font.Font(
            self.font, size).render(text, True, color)
        rect = render.get_rect()

        if getwidth:
            ret.append(rect.width)
        if getheight:
            ret.append(rect.height)

        if rect.width > maxwidth:
            size = int(size*maxwidth/rect.width)
            render = pygame.font.Font(
                self.font, size).render(text, True, color)
            rect = render.get_rect()

        if rect.height > maxheight:
            size = int(size*maxheight/rect.height)
            render = pygame.font.Font(
                self.font, size).render(text, True, color)
            rect = render.get_rect()

        if size < self.minsize:
            text += '...'
            while size < self.minsize:
                render = pygame.font.Font(
                    self.font, size).render(text, True, color)
                rect = render.get_rect()
                size = int(
                    size*min(maxwidth/rect.width, maxheight/rect.height))
                text = text[:-4]+'...'

        # 对齐方式
        if self.align == 'lu':
            rect.topleft = pos
        elif self.align == 'lm':
            rect.midleft = pos
        elif self.align == 'ld':
            rect.bottomleft = pos
        elif self.align == 'mu':
            rect.midtop = pos
        elif self.align == 'mm':
            rect.center = pos
        elif self.align == 'md':
            rect.midbottom = pos
        elif self.align == 'ru':
            rect.topright = pos
        elif self.align == 'rm':
            rect.midright = pos
        elif self.align == 'rd':
            rect.bottomright = pos

        screen.blit(render, rect)

        if ret:
            ret.append(rect)
            return ret
        else:
            return rect
