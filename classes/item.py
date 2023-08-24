class Item:
    def __init__(self, item_id, name, item_type, interaction=lambda: None, count=1):
        self.id = item_id  # unique identifier for each type of item
        self.name = name
        self.type = item_type  # e.g., 'block', 'tool', 'consumable'
        self.count = count
        self.interact = interaction

    def __str__(self):
        return f"{self.name} (x{self.count})"


Items = {
    0: Item(None, None, None),
    1: Item(1, "Stone", "Block"),
    2: Item(2, "Wood", "Block"),
    3: Item(3, "Sand", "Block"),
    4: Item(4, "Coal lump", ""),
    5: Item(5, "Iron lump", "")
}
