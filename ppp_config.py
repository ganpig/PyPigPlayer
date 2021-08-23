from configparser import ConfigParser
from os.path import exists
from pygame.color import THECOLORS


class Config:
    def __init__(self, file):
        if exists(file):
            self.parser = ConfigParser()
            self.parser.read(file, encoding='utf-8')
        else:
            raise FileNotFoundError(file + '配置文件不存在!')

    def get_section(self, section):
        self.config = dict(self.parser.items(section))

    def get(self, key):
        if key in self.config.keys():
            return self.config[key]
        else:
            raise KeyError(key + '设置项不存在!')

    def get_int(self, key):
        data = self.get(key)
        return int(data)

    def get_color(self, key):
        data = self.get(key)
        if data in THECOLORS.keys():
            return THECOLORS[data]
        else:
            raise KeyError(data + '不是有效的颜色名称!')

    def get_tuple(self, key):
        data = self.get(key)
        return tuple(eval(data))

    def get_file(self, key):
        data = self.get(key)
        if exists(data):
            return data
        else:
            raise FileNotFoundError(data + '文件不存在!')
