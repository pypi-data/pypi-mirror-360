import sys

def get_python_version():
    return sys.version_info


def get_python_environment():
    return sys.executable


def get_args():
    return sys.argv