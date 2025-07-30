import argparse


class ArgumentParser:

    def __init__(self, description=None, auto=True):
        if description is None:
            description = "Processing some arguments"
        self.parser = argparse.ArgumentParser(description=description)
        self.auto = auto
        self.kwargs = {}
        self.args = []

    def auto_setting(self):
        self.parser.add_argument("args", nargs='*', help="Positional arguments")
        self.parser.add_argument('--kwargs', nargs='*', help='Keyword arguments in the form key=value', default={})

    def add_argument(self, *args, **kwargs):
        self.parser.add_argument(*args, **kwargs)

    def add_arg(self, name, type, help=None):
        self.parser.add_argument(name, type=type, help=help)

    def parse_args(self):
        if self.auto:
            self.auto_setting()
        args = self.parser.parse_args()
        kwargs = {}
        for kwarg in args.kwargs:
            key, value = kwarg.split('=')
            kwargs[key] = value

        for k,v in vars(args).items():
            if k not in ['args', 'kwargs']:
                kwargs[k] = v
        self.args = args.args
        self.kwargs = kwargs
        return None

    def get(self, key):
        return self.kwargs.get(key, None)

    def __repr__(self):
        return f'args: {self.args} kwargs: {self.kwargs}'

    def __getitem__(self, key):
        return self.kwargs.get(key, None)
