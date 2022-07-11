import pygame

from func import *
from init import *


def aligner(rect: pygame.Rect, mode: str, pos: tuple) -> pygame.Rect:
    """
    按指定方式对齐矩形区域。
    """
    if mode == 'lu':
        rect.topleft = pos
    elif mode == 'lm':
        rect.midleft = pos
    elif mode == 'ld':
        rect.bottomleft = pos
    elif mode == 'mu':
        rect.midtop = pos
    elif mode == 'mm':
        rect.center = pos
    elif mode == 'md':
        rect.midbottom = pos
    elif mode == 'ru':
        rect.topright = pos
    elif mode == 'rm':
        rect.midright = pos
    elif mode == 'rd':
        rect.bottomright = pos
    return rect


def scale(img: pygame.Surface, size: tuple = None, width: int = None, height: int = None):
    """
    缩放 Pygame 表面。
    size、width、height参数同时只能使用一个。
    """
    if size:
        return pygame.transform.scale(img, size)
    elif width:
        return pygame.transform.scale(img, (width, width * img.get_height() / img.get_width()))
    elif height:
        return pygame.transform.scale(img, (height * img.get_width() / img.get_height(), height))
    else:
        return img


class Button:
    """
    按钮。
    """

    align: str = 'mm'
    img: pygame.Surface = None
    left: list = []
    rect: pygame.Rect = None
    right: list = []

    def __init__(self, img: pygame.Surface,
                 align: str = 'mm', left: list = [], right: list = []) -> None:
        self.img = img
        self.align = align
        self.left = left
        self.right = right

    def left_click(self, pos: tuple) -> None:
        """
        发生鼠标左击事件时，判断是否点击了按钮并进行操作。
        """
        if self.rect:
            if self.rect.collidepoint(pos):
                for i in self.left:
                    if i[-1]:
                        start_thread(i[0], *i[1:-1])
                    else:
                        i[0](*i[1:-1])

    def noshow(self) -> None:
        """
        清除矩形判定区域。
        """
        self.rect = None

    def right_click(self, pos: tuple) -> None:
        """
        发生鼠标右击事件时，判断是否点击了按钮并进行操作。
        """
        if self.rect:
            if self.rect.collidepoint(pos):
                for i in self.right:
                    if i[-1]:
                        start_thread(i[0], *i[1:-1])
                    else:
                        i[0](*i[1:-1])

    def show(self, screen: pygame.Surface, pos: tuple, *args, **kwargs) -> pygame.Rect:
        """
        在表面指定位置显示按钮。
        size、width、height参数同时只能使用一个。
        """
        img = scale(self.img, *args, **kwargs)
        self.rect = aligner(img.get_rect(), self.align, pos)
        screen.blit(img, self.rect)
        return pygame.Rect(self.rect)

    def touched(self, pos: tuple) -> bool:
        """
        判断光标是否在按钮上。
        """
        if self.rect:
            return self.rect.collidepoint(pos)
        else:
            return False


class Scrollbar:
    """
    滚动条。
    """

    color: tuple = (0, 0, 0)
    getlen = None
    getpos = None
    length: int = 0
    moving: bool = False
    rect: pygame.Rect = None
    round: bool = False
    setpos = None
    width: int = 0

    def __init__(self, width: int, color: tuple, getpos, getlen, setpos=None, round=False) -> None:
        self.width = width
        self.color = color
        self.getpos = getpos
        self.getlen = getlen
        self.setpos = setpos
        self.round = round

    def drag(self, rel: tuple) -> None:
        """
        发生鼠标移动事件时，判断是否拖动了滚动条。
        """
        if self.rect and self.moving:
            self.setpos(self.getpos()+rel[1]/self.length)

    def left_click(self, pos: tuple) -> None:
        """
        发生鼠标点击事件时需调用此方法。
        """
        if self.rect and self.rect.collidepoint(pos):
            self.moving = True

    def mouse_up(self) -> None:
        """
        发生鼠标松开事件时需调用此方法。
        """
        self.moving = False

    def noshow(self) -> None:
        """
        清除矩形判定区域。
        """
        self.rect = None

    def show(self, screen: pygame.Surface, pos: tuple,
             length: int) -> pygame.Rect:
        """
        在表面指定位置显示滚动条。
        """
        self.length = length
        self.rect = aligner(pygame.Rect(
            0, 0, self.width, length*self.getlen()), 'ru', (pos[0], pos[1]+length*self.getpos()))
        if self.round:
            pygame.draw.rect(screen, self.color, self.rect,
                             border_radius=self.width // 2)
        else:
            pygame.draw.rect(screen, self.color, self.rect)

        return pygame.Rect(self.rect)

    def touched(self, pos: tuple) -> bool:
        """
        判断光标是否在滚动条上。
        """
        if self.rect:
            return self.rect.collidepoint(pos)
        else:
            return False


class Text:
    """
    可设置字体、字号、对齐方式的文本类。
    """

    align: str = 'mm'
    color: tuple = (0, 0, 0)
    font: str = ''
    maxsize: int = 0
    minsize: int = 0

    def __init__(self, font: str, color: tuple, minsize: int,
                 maxsize: int, align: str = 'mm') -> None:
        self.font = font
        self.color = color
        self.minsize = minsize
        self.maxsize = maxsize
        self.align = align

    def show(self, screen: pygame.Surface, text: str, pos: tuple,
             width: int = None, noshow: bool = False) -> pygame.Rect:
        """
        在表面指定位置绘制若干文字，可使用width参数限制最大宽度。
        """

        # 尝试以最大字号绘制
        render = pygame.font.Font(
            self.font, self.maxsize).render(text, True, self.color)

        # 若超过最大宽度，则缩小字号
        if width and render.get_width() > width:
            render = pygame.font.Font(self.font, max(int(
                self.maxsize * width / render.get_width()), self.minsize)).render(text, True, self.color)
            # 若缩小字号后仍超过，强行缩放
            if render.get_width() > width:
                render = pygame.transform.scale(
                    render, (width, int(render.get_height())))

        rect = aligner(render.get_rect(), self.align, pos)
        if not noshow:
            screen.blit(render, rect)
        return rect


class Progbar:
    """
    支持显示值和文本、设置值的进度条。
    """

    align: str = 'mm'
    color1: tuple = (0, 0, 0)
    color2: tuple = (0, 0, 0)
    font: Text = None
    gettext = None
    getvalue = None
    moving: bool = False
    rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
    round: bool = False
    setvalue = None
    width: int = 0

    def __init__(self, width: int, color1: tuple, color2: tuple, getvalue, setvalue=None,
                 gettext=None, font: Text = None, align: str = 'mm', round=False) -> None:
        self.width = width
        self.color1 = color1
        self.color2 = color2
        self.getvalue = getvalue
        self.setvalue = setvalue
        self.gettext = gettext
        self.font = font
        self.align = align
        self.round = round

    def drag(self, pos: tuple) -> None:
        """
        发生鼠标移动事件时，判断是否拖动了进度条并设置值。
        """
        if self.moving:
            self.setvalue(
                max(0, min(1, (pos[0] - self.rect.left) / self.rect.w)))

    def show(self, screen: pygame.Surface, pos: tuple,
             length: int) -> pygame.Rect:
        """
        在表面指定位置显示进度条。
        """
        # 显示整条进度条
        self.rect = aligner(pygame.Rect(
            0, 0, length, self.width), self.align, pos)
        if self.round:
            pygame.draw.rect(screen, self.color2, self.rect,
                             border_radius=self.width // 2)
        else:
            pygame.draw.rect(screen, self.color2, self.rect)

        # 显示进度条的左边部分
        past_rect = pygame.Rect(
            self.rect.left, self.rect.top, length * self.getvalue(), self.width)
        if self.round:
            pygame.draw.rect(screen, self.color1, past_rect,
                             border_radius=self.width // 2)
        else:
            pygame.draw.rect(screen, self.color1, past_rect)

        if self.font:
            # 显示文本
            self.font.show(screen, self.gettext(),
                           self.rect.center, self.rect.w)

        return pygame.Rect(self.rect)

    def left_click(self, pos: tuple) -> None:
        """
        发生鼠标点击事件时，判断是否点击了进度条并设置值。
        """
        if self.rect.collidepoint(pos):
            self.setvalue((pos[0] - self.rect.left) / self.rect.w)
            self.moving = True

    def mouse_up(self) -> None:
        """
        发生鼠标松开事件时需调用此方法。
        """
        self.moving = False

    def touched(self, pos: tuple) -> bool:
        """
        判断鼠标是否在进度条上。
        """
        return self.rect.collidepoint(pos)
