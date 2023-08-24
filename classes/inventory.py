class Inventory:
    def __init__(self):
        self.slots = []

    def add_item(self, item, count=None):
        # Check if the item already exists in inventory
        for existing_item in self.slots:
            if existing_item.id == item.id:
                if count:
                    existing_item.count += count
                    return
                else:
                    existing_item.count += item.count
                    return

        # If not, find an empty slot or create a new one
        if count:
            item.count = count
        self.slots.append(item)

    def get_item(self, slot_number):
        return self.slots[slot_number]

    def __str__(self):
        return '\n'.join([f"Slot {slot}: {item}" for slot, item in enumerate(self.slots)])
