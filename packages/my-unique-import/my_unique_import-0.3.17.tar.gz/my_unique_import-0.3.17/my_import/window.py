import pygetwindow as gw
import pyautogui



class WindowSystem:

    def __init__(self):
        self.windows = self.get_windows()

    def get_windows(self):
        windows = {window.title: window for window in gw.getAllWindows()}
        self.windows = windows
        return windows

    def __repr__(self):
        return str(list(self.windows.keys()))