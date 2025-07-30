import argparse
import os
import queue
import signal
import subprocess
import sys
import threading


def enqueue_output(out, q):
    try:
        for line in iter(out.readline, ''):
            q.put(line)
        out.close()
    except Exception as e:
        print(f"Error reading output: {str(e)}")


def run_command(directory, command, pid_queue=None):
    try:
        # 切换到指定目录
        os.chdir(directory)
        print(f"Running '{command}' in {directory}")
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                   encoding='utf-8', errors='replace')
        print(process.pid)
        if pid_queue is not None:

            pid_queue.put(process.pid)

        q_stdout = queue.Queue()
        q_stderr = queue.Queue()

        t_stdout = threading.Thread(target=enqueue_output, args=(process.stdout, q_stdout))
        t_stderr = threading.Thread(target=enqueue_output, args=(process.stderr, q_stderr))

        t_stdout.start()
        t_stderr.start()
        print('start')

        while t_stdout.is_alive() or t_stderr.is_alive() or not q_stdout.empty() or not q_stderr.empty():
            while not q_stdout.empty():
                line = q_stdout.get_nowait()
                print(f"{directory}: {line}", end="")
            while not q_stderr.empty():
                line = q_stderr.get_nowait()
                print(f"{directory} [ERROR]: {line}", end="")
        t_stdout.join()
        t_stderr.join()

        return_code = process.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, command)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running '{command}' in {directory}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while running '{command}' in {directory}: {str(e)}")

