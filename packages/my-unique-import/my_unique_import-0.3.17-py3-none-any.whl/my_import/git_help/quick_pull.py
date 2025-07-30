import os
import queue
import threading
from .utils import run_command


def quick_pull(*args, **kwargs):
    # signal.signal(signal.SIGINT, signal_handler)
    # parameters_dict = get_hyperparameters()
    current_directory = os.getcwd()
    print("Current Directory:", current_directory)

    parent_directory = os.path.dirname(current_directory)
    print("Parent Directory:", parent_directory)

    # 定义三个目录的路径
    star_rail_node = os.path.join(parent_directory, 'star-rail-node')
    star_rail_solid = os.path.join(parent_directory, 'star-rail-solid')
    StarRail = current_directory
    print("Directories:", star_rail_node, star_rail_solid, StarRail)
    pid_queue = queue.Queue()
    commands = [
        (StarRail, "git pull origin api"),
        (star_rail_node, "git pull origin main"),
        (star_rail_solid, "git pull origin main"),
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
