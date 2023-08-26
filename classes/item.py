class Item:
    def __init__(self, item_id, name, item_type, block_form_id=None, interaction=lambda: None, count=1):
        self.id = item_id  # unique identifier for each type of item
        self.name = name
        self.type = item_type  # e.g., 'block', 'tool', 'consumable'
        self.count = count
        self.interact = interaction
        self.block_form_id = block_form_id

    def __str__(self):
        return f"{self.name} (x{self.count})"


Items = {
    0: Item(None, None, None),
    1: Item(1, "Stone", "Block", 1),
    2: Item(2, "Wood", "Block", 2),
    3: Item(3, "Sand", "Block", 3),
    4: Item(4, "Coal lump", "Block", 4),
    5: Item(5, "Iron lump", "Block", 5),
    6: Item(6, "Workbench", "Block", 7),
    7: Item(7, "Furnace", "Block", 8),
    8: Item(8, "Iron ingot", "Material", None)
}

Recipies = {
    # code:
    # item_id: ("reqs", [(item_id,amount)])
    6: ([], [(2, 16)]),  # Workbench
    7: ([(1, "Workbench")], [(4, 8), (1, 8)]),  # Furnace
    8: ([(1, "Workbench"), (2, "Furnace")], [(4, 2), (5, 1)])  # Iron ingot
}
