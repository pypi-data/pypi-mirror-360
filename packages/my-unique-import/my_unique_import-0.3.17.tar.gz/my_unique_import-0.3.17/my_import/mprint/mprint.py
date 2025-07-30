def c_print(item):
    if isinstance(item, list):
        for i in item:
            print(i)


def bar_print(item, length=16, c='-'):
    bar = c * length
    print(f"{bar}{item}{bar}")