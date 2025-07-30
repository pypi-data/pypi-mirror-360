import os
import subprocess
import argparse
import sys
import queue
import threading
import signal


def get_paramsdict():
    parser = argparse.ArgumentParser(description='Process some text.')
    parser.add_argument("filename", type=str, help="Given a filename")
    parser.add_argument("args", nargs='*', help="Positional arguments")
    parser.add_argument('--kwargs', nargs='*', help='Keyword arguments in the form key=value', default={})

    args = parser.parse_args()

    kwargs = {}
    for kwarg in args.kwargs:
        key, value = kwarg.split('=')
        kwargs[key] = value

    return vars(args)


def run_python(filename, *args, **kwargs):
    if not filename.endswith('.py'):
        filename += '.py'
    abs_filename = os.path.abspath(filename)
    if not os.path.exists(abs_filename):
        print(f"File {abs_filename} does not exist")
        from my_import.files.file_processing import find_file
        files = find_file(os.getcwd(), filename, False)
        if len(files) == 1:
            abs_filename = os.path.abspath(files[0])
            print(f"Found {abs_filename}")
        else:
            print(f"Found {len(files)} files matching {filename}")
            print(files)
            return

    command = [sys.executable, "-c", f"""
from my_import.setup_paths import setup_paths
setup_paths(verbose=False)
import runpy
runpy.run_path(r'{abs_filename}', run_name='__main__')
"""]

    for arg in args:
        command.append(str(arg))

    for key, value in kwargs.items():
        command.append(f"--{key}")
        command.append(str(value))

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        if len(result.stdout) == 0:
            return
        print("Output:")
        print(result.stdout)
        if len(result.stderr) == 0:
            return
        print("Errors:")
        print(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error running {filename}: {e}")
        print("Output:")
        print(e.stdout)
        print("Errors:")
        print(e.stderr)


def main(params=None):
    if params is None:
        params = get_paramsdict()
    run_python(params.get('filename'), *params.get('args'), **params.get('kwargs'))


class Runner:

    def __init__(self):
        self.pid_queue = queue.Queue()

    def run(self, commands):
        signal.signal(signal.SIGINT, self.signal_handler)
        try:
            print("Running... Press Ctrl+C to interrupt")
            threads = []

            for i, (directory, command) in enumerate(commands):
                if directory is None:
                    directory = os.getcwd()
                thread = threading.Thread(target=self.run_command, args=(directory, command, self.pid_queue))
                threads.append(thread)
                thread.start()
                thread.join()

                print("Command completed. Clearing environment before starting the next command...")

            while not self.pid_queue.empty():
                id = self.pid_queue.get()
                try:
                    os.kill(id, signal.SIGTERM)
                    print(f"Killing process {id}")
                except OSError:
                    print(f"Process {id} already terminated")

        except SystemExit:
            print("Process terminated gracefully")

    def signal_handler(self, sig, frame):
        print('You pressed Ctrl+C!')
        print(self.pid_queue)
        while not self.pid_queue.empty():
            id = self.pid_queue.get()
            try:
                os.kill(id, signal.SIGTERM)
                print(f"Killing process {id}")
            except OSError:
                print(f"Process {id} already terminated")
        sys.exit(0)

    @staticmethod
    def enqueue_output(out, q):
        try:
            for line in iter(out.readline, ''):
                q.put(line)
            out.close()
        except Exception as e:
            print(f"Error reading output: {str(e)}")

    def run_command(self, directory, command, pid_queue=None):
        try:
            # 切换到指定目录
            os.chdir(directory)
            print(f"Running '{command}' in {directory}")
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       text=True,
                                       encoding='utf-8', errors='replace', cwd=directory)
            print(process.pid)
            if pid_queue is not None:
                pid_queue.put(process.pid)

            q_stdout = queue.Queue()
            q_stderr = queue.Queue()

            t_stdout = threading.Thread(target=Runner.enqueue_output, args=(process.stdout, q_stdout))
            t_stderr = threading.Thread(target=Runner.enqueue_output, args=(process.stderr, q_stderr))

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


if __name__ == '__main__':
    main(get_paramsdict())
