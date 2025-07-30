import os
import queue
import threading
from .utils import run_command


def run_cmd(command, *args, **kwargs):
    current_directory = os.getcwd()
    print("Current Directory:", current_directory)
    StarRail = current_directory

    pid_queue = queue.Queue()
    cmd = command + " " + " ".join(args)
    print(cmd)
    commands = [
        (StarRail, cmd)
    ]
    try:
        print("Running... Press Ctrl+C to interrupt")
        threads = []

        for i, (directory, command) in enumerate(commands):
            thread = threading.Thread(target=run_command, args=(directory, command, pid_queue))
            threads.append(thread)
            thread.start()
            thread.join()

            print("Command completed. Clearing environment before starting the next command...")
            # clear_environment()

    except SystemExit:
        print("Process terminated gracefully")


def run(commands):
    pid_queue = queue.Queue()
    try:
        print("Running... Press Ctrl+C to interrupt")
        threads = []

        for i, (directory, command) in enumerate(commands):
            thread = threading.Thread(target=run_command, args=(directory, command, pid_queue))
            threads.append(thread)
            thread.start()
            thread.join()

            print("Command completed. Clearing environment before starting the next command...")
            # clear_environment()

    except SystemExit:
        print("Process terminated gracefully")


def get_branch(*args, **kwargs):
    run([(os.getcwd(), 'git branch')])
