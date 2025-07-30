import inspect
import sys

import pyperclip
import pyautogui
import datetime
import time as _time
import os
from .MyBrowser import MyChrome


class AutoControl:

    @staticmethod
    def copy(source):
        return pyperclip.copy(source)

    @staticmethod
    def paste():
        return pyautogui.hotkey('ctrl', 'v')

    @staticmethod
    def get_time():
        return datetime.datetime.now()

    @staticmethod
    def shutdown():
        time = sys.argv[1] if len(sys.argv) > 1 else 0
        return os.system(f'shutdown /s /f /t {time}')

    @staticmethod
    def open(file):
        return os.system(f'start {file}')

    @staticmethod
    def open_url(url):
        browser = MyChrome()
        browser.open(url)
        return browser


class Timer:
    def __init__(self, current_time=None):
        self.current_time = datetime.datetime.now() if current_time is None else current_time
        self._interval = 0.1

    @property
    def interval(self):
        return self._interval

    @staticmethod
    def sleep(number):
        return _time.sleep(number)

    def set_task(self, timer, func):
        self.wait_timer(timer)

        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    def wait_timer(self, timer):
        while datetime.datetime.now() < timer:
            _time.sleep(self.interval)
        print(timer)


class Datetime(datetime.datetime):

    def __new__(cls, year=None, month=None, day=None, hour=0, minute=0, second=0,
                microsecond=0, tzinfo=None, *, fold=0):
        now = datetime.datetime.now()
        if year is None:
            year = now.year
        if month is None:
            month = now.month
        if day is None:
            day = now.day

        return super().__new__(cls, year=year, month=month, day=day, hour=hour, minute=minute, second=second,
                               microsecond=microsecond, tzinfo=tzinfo, fold=fold)

    @classmethod
    def tomorrow(cls):
        t = _time.time() + 24 * 60 * 60
        return cls.fromtimestamp(t)

    def next(self, time):
        t = self.timestamp() + time
        return self.fromtimestamp(t)
