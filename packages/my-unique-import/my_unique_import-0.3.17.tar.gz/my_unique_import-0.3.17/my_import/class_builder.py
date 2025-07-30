import inspect


class ClassBuilder:

    @staticmethod
    def get_params():
        frame = inspect.currentframe().f_back
        args, _, _, values = inspect.getargvalues(frame)
        params = {arg: values[arg] for arg in args[1:]}
        return params

    @staticmethod
    def auto_init(obj):
        frame = inspect.currentframe().f_back
        args, _, _, values = inspect.getargvalues(frame)
        for arg in args[1:]:
            setattr(obj, arg, values[arg])





# class A:
#
#     def __init__(self, name, home):
#         ClassBuilder.auto_init(self)
#         print(self.name)
