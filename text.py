import pygame


class Text():
    def __init__(self, font, maxsize, maxwidth, pos, align):
        self.font = font
        self.maxsize = maxsize
        self.maxwidth = maxwidth
        self.align = align
        self.pos = pos

    def show(self, screen, text, color):
        render = pygame.font.Font(
            self.font, self.maxsize).render(text, True, color)
        rect = render.get_rect()
        if rect.width > self.maxwidth:
            render = pygame.font.Font(self.font, int(
                self.maxsize*self.maxwidth/rect.width)).render(text, True, color)
            rect = render.get_rect()
        if self.align == 'lu':
            rect.topleft = self.pos
        elif self.align == 'lm':
            rect.midleft = self.pos
        elif self.align == 'ld':
            rect.bottomleft = self.pos
        elif self.align == 'mu':
            rect.midtop = self.pos
        elif self.align == 'mm':
            rect.center = self.pos
        elif self.align == 'md':
            rect.midbottom = self.pos
        elif self.align == 'ru':
            rect.topright = self.pos
        elif self.align == 'rm':
            rect.midright = self.pos
        elif self.align == 'rd':
            rect.bottomright = self.pos
        screen.blit(render, rect)
