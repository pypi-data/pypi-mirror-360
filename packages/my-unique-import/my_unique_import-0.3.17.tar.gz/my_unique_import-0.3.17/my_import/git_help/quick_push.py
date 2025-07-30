import os
import queue
import threading
from .utils import run_command


def quick_push(*args, **kwargs):
    # signal.signal(signal.SIGINT, signal_handler, pid_queue)
    # parameters_dict = get_hyperparameters()
    current_directory = os.getcwd()
    print("Current Directory:", current_directory)
    StarRail = current_directory

    pid_queue = queue.Queue()
    summary = kwargs.get('summary', 'update')
    commands = [
        (StarRail, "git add ."),
        (StarRail, f'git commit -m "{summary}"'),
        (StarRail, "git push"),
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