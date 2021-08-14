import pygame


class Text():
    def __init__(self, font, maxsize, align):
        self.font = f'font/{font}.ttf'
        self.maxsize = maxsize
        self.align = align

    def show(self, screen, text, color, pos, maxwidth=10000, maxheight=10000):
        render = pygame.font.Font(
            self.font, self.maxsize).render(text, True, color)
        rect = render.get_rect()
        if rect.width > maxwidth:
            render = pygame.font.Font(self.font, int(
                self.maxsize*maxwidth/rect.width)).render(text, True, color)
            rect = render.get_rect()
        if rect.height > maxheight:
            render = pygame.font.Font(self.font, int(
                self.maxsize*maxheight/rect.height)).render(text, True, color)
            rect = render.get_rect()

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
        return rect
