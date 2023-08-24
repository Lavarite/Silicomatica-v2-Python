class Block:
    def __init__(self, id=0, name="", drop_id=0, interaction=lambda: None, transparent=False):
        self.id = id
        self.name = name
        self.interact = interaction
        self.drop_id = drop_id
        self.transparent = transparent


Blocks = {
    0: Block(0, "Air", 0, transparent=True),
    1: Block(1, "Stone", 1),
    2: Block(2, "Wood", 2),
    3: Block(3, "Sand", 3),
    4: Block(4, "Coal", 4),
    5: Block(5, "Iron", 5),
    6: Block(6, "Water", 0, transparent=True)
}