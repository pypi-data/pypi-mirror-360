class highlambder(object):

    _attr_blocklist = {
        "__getitem__",
        "keys",
        "__contains__",
    }

    def __init__(self, ops=None, new=None):
        self._ops = [new or (lambda x: x)] + (ops or [])

    def __call__(self, x):
        temp = None
        for f in self._ops[::-1]:
            temp = f(x if temp is None else temp)
            if isinstance(temp, highlambder):
                temp = temp(x)
            if callable(temp):
                temp = temp()
        return temp

    def __str__(self):
        return highlambder(
            ops=self._ops,
            new=lambda x: str(x))

    def __add__(self, y):
        return highlambder(
            ops=self._ops,
            new=lambda x: x + y)

    def __radd__(self, y):
        return highlambder(
            ops=self._ops,
            new=lambda x: y + x)

    def __sub__(self, y):
        return highlambder(
            ops=self._ops,
            new=lambda x: x - y)

    def __rsub__(self, y):
        return highlambder(
            ops=self._ops,
            new=lambda x: y - x)

    def __mul__(self, y):
        return highlambder(
            ops=self._ops,
            new=lambda x: x * y)

    def __rmul__(self, y):
        return highlambder(
            ops=self._ops,
            new=lambda x: y * x)

    def __truediv__(self, y):
        return highlambder(
            ops=self._ops,
            new=lambda x: x / y)

    def __rtruediv__(self, y):
        return highlambder(
            ops=self._ops,
            new=lambda x: y / x)

    def __getattr__(self, y):
        if y in highlambder._attr_blocklist:
            raise AttributeError(f"Highlambder has no attribute {y}")
        return highlambder(
            ops=self._ops,
            new=lambda x: getattr(x, y))

    def __getitem__(self, y):
        return highlambder(
            ops=self._ops,
            new=lambda x: x[y])

    # def __array__(self, dtype=None):
    #     return self._ops

    def __contains__(self, y):
        raise NotImplementedError('__contains__ not supported')

    def __len__(self, y):
        raise NotImplementedError('__len__ not supported')


L = highlambder()
