import pygame
import win32gui
import win32con
import win32api


class Window:
    def __init__(self, defaultsize, minsize, title):
        self.defaultsize = defaultsize
        self.minx, self.miny = minsize
        self.fullscreen = False
        self.repaint = True
        sizex, sizey = self.size = defaultsize
        self.screen = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        win32gui.SetWindowPos(
            win32gui.GetForegroundWindow(),
            win32con.HWND_TOPMOST,
            (win32api.GetSystemMetrics(
                win32con.SM_CXSCREEN) - sizex) // 2,
            (win32api.GetSystemMetrics(
                win32con.SM_CYSCREEN) - sizey) // 2,
            sizex,
            sizey,
            win32con.SWP_SHOWWINDOW)
        pygame.display.set_caption(title)

    def resize(self, size):
        self.size = (max(size[0], self.minx), max(size[1], self.miny))
        pygame.display.set_mode(self.size, pygame.RESIZABLE)
        self.repaint = True

    def set_fullscreen(self, mode=1):
        if self.fullscreen:
            self.fullscreen = False
            sizex, sizey = self.size = self.defaultsize
            pygame.display.set_mode(self.size)
            pygame.display.set_mode(self.size, pygame.RESIZABLE)
            win32gui.SetWindowPos(
                win32gui.GetForegroundWindow(),
                win32con.HWND_TOPMOST,
                (win32api.GetSystemMetrics(
                    win32con.SM_CXSCREEN) - sizex) // 2,
                (win32api.GetSystemMetrics(
                    win32con.SM_CYSCREEN) - sizey) // 2,
                sizex,
                sizey,
                win32con.SWP_SHOWWINDOW)
            self.repaint = True
        else:
            if mode:
                self.fullscreen = True
                self.size = (
                    win32api.GetSystemMetrics(
                        win32con.SM_CXSCREEN), win32api.GetSystemMetrics(
                        win32con.SM_CYSCREEN))
                pygame.display.set_mode(
                    self.size, pygame.FULLSCREEN | pygame.HWSURFACE)
                self.repaint = True

    def getsize(self):
        if self.size != self.screen.get_size():
            self.resize(self.screen.get_size())
        return self.size

    def getscreen(self):
        return self.screen

    def need_repaint(self):
        if self.repaint:
            self.repaint = False
            return True
        else:
            return False
