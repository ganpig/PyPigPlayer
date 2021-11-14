import pygame


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


class Text:
    """
    可设置字体、字号、对齐方式的文本类。
    """

    font: str = ''
    color: tuple = (0, 0, 0)
    minsize: int = 0
    maxsize: int = 0
    align: str = 'mm'

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


class Button:
    """
    按钮。
    """

    rect: pygame.Rect = None
    img: pygame.Surface = None
    onclick = None
    align: str = 'mm'
    data = 0

    def __init__(self, img: pygame.Surface, onclick=None,
                 align: str = 'mm', data=0) -> None:
        self.img = img
        self.onclick = onclick
        self.align = align
        self.data = data

    def show(self, screen: pygame.Surface, pos: tuple, *args, **kwargs) -> pygame.Rect:
        """
        在表面指定位置显示按钮。
        size、width、height参数同时只能使用一个。
        """
        img = scale(self.img, *args, **kwargs)
        self.rect = aligner(img.get_rect(), self.align, pos)
        screen.blit(img, self.rect)
        return pygame.Rect(self.rect)

    def click(self, pos: tuple) -> None:
        """
        发生鼠标点击事件时，判断是否点击了按钮并进行操作。
        """
        if self.rect:
            if self.rect.collidepoint(pos):
                if self.onclick:
                    self.onclick()


class Progbar:
    """
    支持显示值和文本、设置值的进度条。
    """

    width: int = 0
    color1: tuple = (0, 0, 0)
    color2: tuple = (0, 0, 0)
    getvalue = None
    setvalue = None
    gettext = None
    moving: bool = False
    font: Text = None
    align: str = 'mm'
    round: bool = False
    rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)

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

    def click(self, pos: tuple) -> None:
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

    def drag(self, pos: tuple) -> None:
        """
        发生鼠标移动事件时，判断是否拖动了进度条并设置值。
        """
        if self.moving:
            self.setvalue(
                max(0, min(1, (pos[0] - self.rect.left) / self.rect.w)))


class Area:
    """
    滚动区域。
    """

    rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
    surface: pygame.Surface = pygame.Surface((0, 0))
    show_pos: float = 0
    mouse_pos: tuple = (0, 0)
    moving: bool = False

    def clear(self, size: tuple) -> None:
        """
        清空滚动区域。
        """
        self.surface = pygame.Surface(size).convert_alpha()
        self.surface.fill((0, 0, 0, 0))

    def blit(self, surface: pygame.Surface, pos: tuple) -> None:
        """
        绘制内容到滚动区域。
        """
        self.surface.blit(surface.convert_alpha(), pos)

    def show(self, screen: pygame.Surface, pos: tuple, height: float) -> None:
        """
        显示滚动区域。
        """
        self.show_pos = max(
            min(self.show_pos, self.surface.get_height()-height), 0)
        self.rect = pygame.Rect(*pos, self.surface.get_width(), height)
        screen.blit(self.surface, pos, (0, self.show_pos,
                    self.surface.get_width(), height))

    def click(self, pos: tuple) -> None:
        """
        处理鼠标点击事件。
        """
        if self.rect.collidepoint(pos):
            self.mouse_pos = pos
            self.moving = True

    def mouse_up(self, pos: tuple, test_list: list) -> None:
        """
        处理鼠标松开事件。
        """
        if self.mouse_pos == pos:
            area_pos = (pos[0]-self.rect.left, pos[1] -
                        self.rect.top+self.show_pos)
            for i in test_list:
                i.click(area_pos)
        self.moving = False

    def drag(self, rel: tuple) -> None:
        """
        处理鼠标移动事件。
        """
        if self.moving:
            self.show_pos -= rel[1]
