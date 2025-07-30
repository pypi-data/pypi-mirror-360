import subprocess
import sys
import os


def update_environment(requirements_file='requirements.txt'):
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
        print("Environment updated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while updating the environment: {e}")


def main():
    from .file_config import find_top_level_package
    package = find_top_level_package(os.getcwd())
    requirements_file = os.path.join(package, 'requirements.txt')
    if not os.path.exists(requirements_file):
        print('No requirements file found. Please create one and try again.')
        return None
    print(requirements_file)
    update_environment(requirements_file)


if __name__ == "__main__":
    update_environment()
