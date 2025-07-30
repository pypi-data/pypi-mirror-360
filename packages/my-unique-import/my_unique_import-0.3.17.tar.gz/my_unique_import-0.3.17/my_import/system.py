import sys
from multiprocessing import Process, Lock
import time
import os
import runpy


def child_process():
    print(f"Child process {os.getpid()} started")
    time.sleep(2)
    print(f"Child process {os.getpid()} finished")


def parent_process():
    print(sys.argv)
    print(f"Parent process {os.getpid()} started")
    p = Process(target=child_process)
    p.start()
    print(f"Parent process {os.getpid()} created child process {p.pid}")
    p.join()  # 等待子进程结束
    print(f"Parent process {os.getpid()} finished")


def run(func):
    def wrapper(*args, **kwargs):
        p = Process(target=func, args=args, kwargs=kwargs)
        p.start()
        print("Main process started")
        p.join()

    return wrapper


def main():
    parent_process()


if __name__ == "__main__":
    main()
