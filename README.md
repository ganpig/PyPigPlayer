# PyPigPlayer

使用 Pygame 实现的简易音乐播放器，未来将支持歌词显示、定时关闭等高级功能。
当前版本仅支持 mp3 文件播放。未来将支持导入各种格式到“我的音乐”。
若想播放其他格式文件，请使用 v0.2.1 版本（不支持进度功能）。

# 当前支持功能

- ### 播放 MP3
- ### 控制并显示进度条，快进快退
- ### 控制音量
- ### 单曲循环

# 使用方法

## 通过 exe 程序目录使用（无调试信息）

直接打开`PyPigPlayer.exe`即可。

## 通过源代码使用（有调试信息）

### 请先安装 Python3 及以下依赖库：

```bash
pip install easygui
pip install pygame
pip install eyed3
pip install pywin32
pip install pyinstaller
```

### 打开主程序：

```bash
python3 main.py
```

### 创建 exe 程序目录

直接打开`build.bat`即可。
