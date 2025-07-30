#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

import argparse
from .git_help import quick_pull, quick_push, run_cmd
from .git_help import api

valid_commands = ['pull', 'push', 'status', 'commit']


def get_hyperparameters():
    parser = argparse.ArgumentParser(description="Set hyperparameters for start server.")
    parser.add_argument("command", type=str,
                        help="Select pull, push or any other command for git")  # .completer = ChoicesCompleter(
    #    valid_commands)
    parser.add_argument("args", nargs='*', help="Positional arguments")
    parser.add_argument("--kwargs", nargs='*', help="Keyword arguments in the form key=value")
    # parser.add_argument("--h", action="store_true",
    #                     help="Print hyperparameter options.")
    # argcomplete.autocomplete(parser)
    args = parser.parse_args()

    kwargs_dict = {}
    if args.kwargs:
        for kwarg in args.kwargs:
            key, value = kwarg.split('=')
            kwargs_dict[key] = value

    # if args.h:
    #     print("Usage: setup_paths.py [command]\n")
    #     print("Positional arguments:")
    #     print("  command    Set the command: 'pull' or 'push'")
    #     exit()
    print(args.command, args.args, kwargs_dict)
    return args.command, args.args, kwargs_dict


def has_function(module, func_name):
    return hasattr(module, func_name) and callable(getattr(module, func_name))


def main():
    command, args, kwargs_dict = get_hyperparameters()
    if command == 'pull':
        quick_pull(*args, **kwargs_dict)
    elif command == 'push':
        quick_push(*args, **kwargs_dict)
    elif has_function(api, command):
        getattr(api, command)(*args, **kwargs_dict)
    else:
        run_cmd(f'git {command}', *args, **kwargs_dict)


if __name__ == '__main__':
    main()
