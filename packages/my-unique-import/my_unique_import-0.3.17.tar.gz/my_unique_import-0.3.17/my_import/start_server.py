import argparse
import os
import sys


def get_hyperparameters():
    parser = argparse.ArgumentParser(description="Set hyperparameters for start server.")
    parser.add_argument("language", type=str, choices=['en', 'ch'], nargs='?', default='en',
                        help="Set the language: 'ch' for Chinese, 'en' for English")
    parser.add_argument("--config", type=str,
                        help="Set the configuration file")
    parser.add_argument("--h", action="store_true",
                        help="Print hyperparameter options.")

    args = parser.parse_args()
    if args.h:
        print("Usage: setup_paths.py [language]\n")
        print("Positional arguments:")
        print("  language    Set the language: 'ch' for Chinese, 'en' for English")
        exit()
    return vars(args)


def main():
    from pathlib import Path
    from .file_config import find_top_level_package
    parameters_dict = get_hyperparameters()
    current_dir = find_top_level_package((os.getcwd()))
    current_dir = Path(current_dir).resolve()
    print(current_dir)
    sys.path.insert(0, str(current_dir))
    file_name = 'quick_start'
    package = os.path.basename(current_dir)
    from .custom_importer import import_module
    print(package)
    module = import_module(file_name, package)

    module.main(parameters_dict)
