import pygame


class Button(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.size = size
        self.img = None

    def show(self, screen):
        if self.img:
            screen.blit(self.img, self.rect)

    def set_img(self, img):
        if img:
            self.img = pygame.transform.scale(
                pygame.image.load(f'img/{img}.png'), (self.size,)*2)
            self.rect = self.img.get_rect()
            self.rect.left, self.rect.top = self.pos
        else:
            self.img = None

    def test_click(self, pos):
        if self.rect.collidepoint(pos):
            self.onclick()
