import numpy as np


class UniformSampler:

    def __init__(self, low, high, dtype=None):
        self.low = low
        self.high = high
        self.dtype = dtype if dtype is not None else np.float64

    def sample(self, size=None):
        random_values = np.random.uniform(low=self.low, high=self.high, size=size)

        if size is None:
            if self.dtype == int:
                return int(np.floor(random_values))
            return np.array(random_values).astype(self.dtype)

        if self.dtype == int:
            return np.floor(random_values).astype(int)

        return random_values.astype(self.dtype)


class BernoulliSampler:

    def __init__(self, p):
        if not isinstance(p, np.ndarray) and not (0 <= p <= 1):
            raise ValueError("p must be in [0, 1]")

        self.p = p

    def sample(self, size=None):
        if isinstance(self.p, np.ndarray):
            return np.array([np.random.binomial(n=1, p=p) for p in self.p])
        return np.random.binomial(n=1, p=self.p, size=size)

    def __repr__(self):
        return f"BernoulliSampler(p={self.p})"