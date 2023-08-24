class Inventory:
    def __init__(self):
        self.slots = {}

    def add_item(self, item, count=None):
        if len(self.slots)>9: return
        # Check if the item already exists in inventory
        for slot, existing_item in self.slots.items():
            if existing_item.id == item.id:
                if count:
                    existing_item.count += count
                    return
                else:
                    existing_item.count += item.count
                    return

        # If not, find an empty slot or create a new one
        slot_number = len(self.slots) + 1
        self.slots[slot_number] = item
        if count:
            self.slots[slot_number].count = count

    def remove_item(self, slot_number, count=1):
        if slot_number in self.slots:
            item = self.slots[slot_number]
            if item.count <= count:
                del self.slots[slot_number]
            else:
                item.count -= count

    def get_item(self, slot_number):
        return self.slots.get(slot_number, None)

    def __str__(self):
        return '\n'.join([f"Slot {slot}: {item}" for slot, item in self.slots.items()])
