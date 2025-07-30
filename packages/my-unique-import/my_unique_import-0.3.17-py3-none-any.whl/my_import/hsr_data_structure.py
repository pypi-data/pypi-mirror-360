class BidirectionalDict(dict):
    def __init__(self, *args, **kwargs):
        super(BidirectionalDict, self).__init__()
        for key, value in dict(*args, **kwargs).items():
            self[key] = value

    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        if value in self:
            del self[value]
        super(BidirectionalDict, self).__setitem__(key, value)
        super(BidirectionalDict, self).__setitem__(value, key)

    def __getitem__(self, key):
        if key in self:
            return super().__getitem__(key)
        import re
        stripped_key = re.sub(r'\W+', '', key)
        if stripped_key in self:
            return super().__getitem__(stripped_key)
        else:
            return super().__getitem__(key)

    def __delitem__(self, key):
        value = self[key]
        super(BidirectionalDict, self).__delitem__(key)
        super(BidirectionalDict, self).__delitem__(value)