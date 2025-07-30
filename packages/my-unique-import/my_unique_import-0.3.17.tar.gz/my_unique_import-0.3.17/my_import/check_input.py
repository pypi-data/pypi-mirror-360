import sys
from ctypes import wintypes
import ctypes
import pyautogui

KLF_ACTIVATE = 0x00000001


# 获取当前输入法的语言标识符
def set_english_keyboard_layout():
    hWnd = ctypes.windll.user32.GetForegroundWindow()
    thread_id = ctypes.windll.user32.GetWindowThreadProcessId(hWnd, None)
    layout_id = ctypes.windll.user32.GetKeyboardLayout(thread_id)
    locale_id = 0x0409
    if layout_id & 0xFFFF != locale_id:
        locale_id_wstr = "00000409"
        klid = ctypes.create_unicode_buffer(locale_id_wstr)
        user32 = ctypes.WinDLL("user32")
        LoadKeyboardLayoutW = user32.LoadKeyboardLayoutW
        LoadKeyboardLayoutW.argtypes = [wintypes.LPCWSTR, wintypes.UINT]
        LoadKeyboardLayoutW.restype = wintypes.HKL

        klh = LoadKeyboardLayoutW(klid, KLF_ACTIVATE)
        if klh == 0:
            raise ctypes.WinError()
        print(f"Loaded keyboard layout: {locale_id_wstr}, handle: 0x{klh:016X}")
        ctypes.windll.user32.ActivateKeyboardLayout(klh, KLF_ACTIVATE)
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        thread_id = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)
        hkl = ctypes.windll.user32.LoadKeyboardLayoutW(f"{locale_id:08X}", KLF_ACTIVATE)
        if hkl == 0:
            raise ctypes.WinError("Failed to load keyboard layout")
        ctypes.windll.user32.PostMessageW(hwnd, 0x0050, 0, hkl)
    else:
        # print("already english")
        pass
    return


def ensure_english_keyboard():
    set_english_keyboard_layout()


def is_caps_lock_on():
    hllDll = ctypes.WinDLL("User32.dll")
    VK_CAPITAL = 0x14
    return hllDll.GetKeyState(VK_CAPITAL) & 0x0001


def switch_to_lowercase():
    pyautogui.press('capslock')
    # print("Switched to lowercase by sending Shift key.")


def ensure_lowercase():
    if is_caps_lock_on():
        # print("Caps Lock is on, switching to lowercase...")
        switch_to_lowercase()
    else:
        pass
        # print("Caps Lock is already off, no need to switch.")


def block_input(block):
    ctypes.windll.user32.BlockInput(block)


def ensure_enter(func):
    def wrapper(*args, **kwargs):
        ensure_lowercase()
        ensure_english_keyboard()
        block_input(True)
        result = func(*args, **kwargs)
        block_input(False)
        # print(f"Function '{func.__name__}' execute with ensure enter")
        return result

    return wrapper


if __name__ == "__main__":
    print("Python {0:s} {1:d}bit on {2:s}\n".format(" ".join(item.strip() for item in sys.version.split("\n")),
                                                    64 if sys.maxsize > 0x100000000 else 32, sys.platform))
    ensure_lowercase()
