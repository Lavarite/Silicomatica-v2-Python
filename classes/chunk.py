from classes.block import Block


class Chunk:
    def __init__(self, size):
        self.size = size
        self.blocks = {(x, y): Block() for x in range(size) for y in range(size)}
