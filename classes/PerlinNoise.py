import math
import random

class PerlinNoise:
    def __init__(self, seed=None):
        self.seed = seed if seed is not None else random.randint(0, 2 ** 32 - 1)
        random.seed(self.seed)
        self.permutation = list(range(256))
        random.shuffle(self.permutation)
        self.permutation *= 2

    @staticmethod
    def _fade(t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    @staticmethod
    def _lerp(a, b, x):
        return a + x * (b - a)

    @staticmethod
    def _grad(hash_value, x, y, z):
        h = hash_value & 15
        grad = 1 + (h & 7)
        return ((grad * x + (1 - grad) * y) * (1 if h & 8 else -1)) / 15.0

    def noise(self, x, y, z=0.0):
        X, Y, Z = int(x) & 255, int(y) & 255, int(z) & 255
        x -= math.floor(x)
        y -= math.floor(y)
        z -= math.floor(z)

        u, v, w = self._fade(x), self._fade(y), self._fade(z)

        A = self.permutation[X] + Y
        B = self.permutation[X + 1] + Y

        AA = self.permutation[A] + Z
        BA = self.permutation[B] + Z
        AB = self.permutation[A + 1] + Z
        BB = self.permutation[B + 1] + Z

        raw_value = self._lerp(
            self._lerp(
                self._lerp(self._grad(self.permutation[AA], x, y, z),
                           self._grad(self.permutation[BA], x - 1, y, z), u),
                self._lerp(self._grad(self.permutation[AB], x, y - 1, z),
                           self._grad(self.permutation[BB], x - 1, y - 1, z), u), v),
            self._lerp(
                self._lerp(self._grad(self.permutation[AA + 1], x, y, z - 1),
                           self._grad(self.permutation[BA + 1], x - 1, y, z - 1), u),
                self._lerp(self._grad(self.permutation[AB + 1], x, y - 1, z - 1),
                           self._grad(self.permutation[BB + 1], x - 1, y - 1, z - 1), u), v),
            w)

        # Scaling based on the previously observed min and max values
        min_val, max_val = -0.286, 0.289
        return 2 * (raw_value - min_val) / (max_val - min_val) - 1
