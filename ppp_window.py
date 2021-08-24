import pygame
import win32gui
import win32con
import win32api


class Window:
    def __init__(self, defaultsize, minsize, title):
        self.defaultsize = defaultsize
        self.minx, self.miny = minsize
        self.fullscreen = False
        self.recul = True
        self.screenx = win32api.GetSystemMetrics(
            win32con.SM_CXSCREEN)
        self.screeny = win32api.GetSystemMetrics(
            win32con.SM_CYSCREEN)
        sizex, sizey = self.size = defaultsize
        self.screen = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        pygame.display.set_caption(title)
        self.handle = win32gui.FindWindow(None, title)

        win32gui.SetWindowPos(
            self.handle,
            win32con.HWND_TOPMOST,
            (self.screenx - sizex) // 2,
            (self.screeny - sizey) // 2,
            sizex,
            sizey,
            win32con.SWP_SHOWWINDOW)
        self.resize()

    def set_fullscreen(self, mode=1):
        if self.fullscreen:
            self.fullscreen = False
            self.recul = True
            sizex, sizey = self.size = self.defaultsize
            pygame.display.set_mode(self.size)
            pygame.display.set_mode(self.size, pygame.RESIZABLE)
            win32gui.SetWindowPos(
                self.handle,
                win32con.HWND_TOPMOST,
                (self.screenx - sizex) // 2,
                (self.screeny - sizey) // 2,
                sizex,
                sizey,
                win32con.SWP_SHOWWINDOW)
        else:
            if mode:
                self.fullscreen = True
                self.recul = True
                self.size = (
                    self.screenx, self.screeny)
                pygame.display.set_mode(
                    self.size, pygame.FULLSCREEN | pygame.HWSURFACE)

    def resize(self):
        self.recul = True
        size = self.screen.get_size()
        self.size = (max(size[0], self.minx), max(size[1], self.miny))
        pygame.display.set_mode(self.size, pygame.RESIZABLE)
