from classes.PerlinNoise import PerlinNoise
from classes.block import Block, Blocks
from classes.chunk import Chunk


class World:
    def __init__(self, size, seed, name=""):
        self.size = size
        self.seed = seed
        self.name = name
        self.perlin = PerlinNoise(seed=self.seed)

        # Define noise value thresholds for different block types
        self.thresholds = {
            6: [(-1, -0.6), (-0.6, -0.4)],  # Water (deep and shallow)
            3: [(-0.4, -0.2)],  # Sand
            2: [(-0.2, 0)],  # Wood (Forests and sparse trees on grassland)
            1: [(0.2, 0.35), (0.4, 0.45), (0.6, 0.65), (0.75, 0.1)],  # Stone (Mountains)
            4: [(0.65, 0.75)],  # Coal (Scattered within mountains)
            5: [(0.35, 0.4)]  # Iron (Scattered within mountains)
        }

        self.chunks = {}

    def generate_world(self):
        """Generate chunks based on Perlin noise values."""
        for x in range(self.size):
            for y in range(self.size):
                chunk = Chunk(16)
                for block_x in range(chunk.size):
                    for block_y in range(chunk.size):
                        noise_val = self.perlin.noise((x * chunk.size + block_x) * 0.1,
                                                      (y * chunk.size + block_y) * 0.1)
                        block_id = self.get_block_id_from_noise(noise_val)
                        chunk.blocks[(block_x, block_y)] = Blocks[block_id]
                self.chunks[(x, y)] = chunk

    def get_block_id_from_noise(self, noise_val):
        for block_id, ranges in self.thresholds.items():
            for min_val, max_val in ranges:
                if (min_val is None or noise_val > min_val) and (max_val is None or noise_val <= max_val):
                    return block_id
        return 0  # Default to air (ID=0) if no match

