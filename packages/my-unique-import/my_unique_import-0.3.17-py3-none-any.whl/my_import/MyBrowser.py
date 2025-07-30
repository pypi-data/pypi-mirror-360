import subprocess
import webbrowser
import time
import pygetwindow as gw
from screeninfo import get_monitors
import pyautogui
import pyperclip
from .check_input import ensure_enter


class MyChrome:

    def __init__(self, name="", window=None):
        self.name = name
        self.window = window
        self.screens_info = get_screens_info()
        self.window_info = get_window_info(self.window)
        self.current_screen = self.get_window_position()

    def open(self, url, new=0):
        print(url, new, self.window)
        if new == 0 and self.window is not None:
            self.window.activate()
            webbrowser.open(url)
        elif new == 1 and self.window is not None:
            self.window.activate()
            webbrowser.open(url)
        elif new == 2 or self.window is None:
            before_windows = gw.getAllWindows()

            subprocess.Popen([r"C:\Program Files\Google\Chrome\Application\chrome.exe", '--new-window', 'google.com'])

            new_window = None
            for _ in range(30):
                after_windows = gw.getAllWindows()
                new_window = next((window for window in after_windows if window not in before_windows), None)
                if new_window:
                    break
                time.sleep(0.5)
            new_window.maximize()
            self.window = new_window
            self.window_info = get_window_info(self.window)
            self.current_screen = self.get_window_position()
            self.window.activate()
            webbrowser.open(url)

    def close(self):
        self.window.activate()
        pyautogui.hotkey('ctrl', 'w')

    def set_window(self, window):
        self.window = window

    @ensure_enter
    def put(self, cmd):
        pyautogui.hotkey('ctrl', 'shift', 'j')
        time.sleep(.2)
        # pyautogui.press('tab')
        pyperclip.copy(cmd)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
        pyautogui.hotkey('F12')

    @staticmethod
    def write(script):
        pyperclip.copy(script)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1)
        pyautogui.press('enter')

    def get_window_position(self):
        return which_screen_is_window_on(self.window_info, self.screens_info)

    def move_window_to_screen(self, screen_choice, maximize=True, center=False):
        if self.current_screen == screen_choice or self.current_screen == -1:
            return None
        move_window_to_screen(self.window, self.screens_info[screen_choice], maximize=maximize, center=center)


def get_screens_info():
    screens = []
    for monitor in get_monitors():
        screens.append({
            'left': monitor.x,
            'top': monitor.y,
            'width': monitor.width,
            'height': monitor.height,
            'right': monitor.x + monitor.width,
            'bottom': monitor.y + monitor.height
        })
    return screens


def get_window_info(window):
    if window:
        return {
            'left': window.left,
            'top': window.top,
            'width': window.width,
            'height': window.height,
            'right': window.left + window.width,
            'bottom': window.top + window.height
        }
    return None


def calculate_overlap_area(window_info, screen_info):
    overlap_left = max(window_info['left'], screen_info['left'])
    overlap_top = max(window_info['top'], screen_info['top'])
    overlap_right = min(window_info['right'], screen_info['right'])
    overlap_bottom = min(window_info['bottom'], screen_info['bottom'])

    if overlap_left < overlap_right and overlap_top < overlap_bottom:
        return (overlap_right - overlap_left) * (overlap_bottom - overlap_top)
    return 0


def which_screen_is_window_on(window_info, screens_info):
    if window_info is None:
        return -1
    max_overlap_area = 0
    best_screen_idx = -1

    for idx, screen in enumerate(screens_info):
        overlap_area = calculate_overlap_area(window_info, screen)
        if overlap_area > max_overlap_area:
            max_overlap_area = overlap_area
            best_screen_idx = idx

    return best_screen_idx


def move_window_to_screen(window, screen_info, maximize=True, center=False):
    window.restore()
    if window:
        if center:
            new_left = screen_info['left'] + (screen_info['width'] - window.width) // 2
            new_top = screen_info['top'] + (screen_info['height'] - window.height) // 2
            print(f"窗口已移动到屏幕的中间: ({new_left}, {new_top})")
        else:
            new_left = screen_info['left']
            new_top = screen_info['top']
            print(f"窗口已移动到屏幕的左上角: ({new_left}, {new_top})")
        # if maximize and not window.isMaximized:
        #     window.maximize()
        window.moveTo(new_left, new_top)
        if maximize and not window.isMaximized:
            window.maximize()
        print(window.isMaximized)
        print(window.width, window.height)
