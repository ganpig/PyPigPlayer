import pygame


class Button():
    def __init__(
            self,
            id,
            img=None,
            onclick=None,
            font=None,
            text=None,
            color=None):
        self.id = id
        self.set_img(img)
        self.font = font
        self.set_text(text)
        self.set_color(color)
        self.rect = None
        self.onclick = onclick

    def show(self, screen, rect):
        if self.img:
            img = pygame.transform.scale(
                self.img, (int(rect.width), int(rect.height)))
            self.rect = rect
            screen.blit(img, rect)
        if self.text:
            self.font.show(screen, self.text, self.color,
                           rect.center, rect.width, rect.height)

    def set_img(self, img):
        if img:
            self.img = pygame.image.load(f'img/btn/{img}.png')
        else:
            self.img = None

    def set_text(self, text):
        if text:
            self.text = text
        else:
            self.text = None

    def set_color(self, color):
        if color:
            self.color = color
        else:
            self.color = None

    def test_click(self, pos):
        if self.rect:
            if self.rect.collidepoint(pos):
                self.onclick()
