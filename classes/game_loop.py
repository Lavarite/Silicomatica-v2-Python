import os
import threading

import sys
from queue import Queue
from tkinter import filedialog

import dill
import pygame
import tkinter as tk
from classes.block import Blocks
from classes.item import Items, Recipies
from classes.server import send_large_data, receive_large_data

queue = Queue()

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Screen dimensions
WIDTH = 800
HEIGHT = 600

# Define block colors
BLOCK_COLORS = {
    0: WHITE,  # Air
    1: (128, 128, 128),  # Stone (Gray)
    2: (139, 69, 19),  # Wood (Brown)
    3: (255, 223, 0),  # Sand (Yellow)
    4: (0, 0, 0),  # Coal (Black)
    5: (50, 50, 50),  # Iron (Darker Gray)
    6: BLUE,  # Water
    7: RED,  # Workbench
    8: GREEN  # Furnace
}

# Define block size
BLOCK_SIZE = 50
PLAYER_SPEED = 5
DRAG = 0.2
PLAYER_SIZE = 30

CAMERA_SPEED = 2

chunk_borders = False
player_direction = {"Left": 0, "Right": 0, "Up": 0, "Down": 0}
player_acceleration = pygame.Vector2(0, 0)

last_selected_crafting_item = 0


def game_loop(world, player, socket=None, players=None):

    if not players:
        players = []
    else:
        for p in players:
            if p.id == player.id:
                players.remove(p)

    def unpack_data():
        nonlocal players
        while True:
            try:
                data_received = receive_large_data(socket)
                if data_received:

                    # Extract ID and serialized data
                    update_id, *update_data = data_received
                    if update_id == -2:
                        socket.close()
                        return
                    elif update_id == 0:  # Global world alteration
                        new_world = update_data[0]
                        world.size = new_world.size
                        world.seed = new_world.seed
                        world.chunks = new_world.chunks

                    elif update_id == 1:  # Player connected
                        new_players = update_data[0]
                        players = new_players[:]
                        for p in players:
                            if p.id == player.id:
                                players.remove(p)

                        print("player connected")

                    elif update_id == 2:  # Player disconnected
                        removed_player = update_data[0]
                        for p in players:
                            if p.id == removed_player.id:
                                players.remove(p)
                        print("player disconnected")

                    elif update_id == 3:  # Player Movement
                        new_player = update_data[0]
                        # Update player position and other state
                        if new_player.id != player.id:
                            for p in players:
                                if p.id == new_player.id:
                                    players.remove(p)
                                    players.append(new_player)

                    elif update_id == 4:  # Block Alteration
                        chunk_x, chunk_y = update_data[0]
                        block_x, block_y = update_data[1]
                        block_data = update_data[2]
                        # Update block in the world
                        world.chunks[(chunk_x, chunk_y)].blocks[(block_x, block_y)] = block_data

                    elif update_id == -404:
                        on_closing()
                        sys.exit()

            except Exception as e:
                continue

    if socket:
        receive_thread = threading.Thread(target=unpack_data)
        receive_thread.daemon = True
        receive_thread.start()

    def on_key_press(event):
        global chunk_borders, player_acceleration  # Make sure to access the global variables

        key = event.keysym
        if key == 'Left':
            player_direction["Left"] = 1
        if key == 'Right':
            player_direction["Right"] = 1
        if key == 'Up':
            player_direction["Up"] = 1
        if key == 'Down':
            player_direction["Down"] = 1
        if key == 'b':
            chunk_borders = not chunk_borders

        player_acceleration.x = player_direction["Right"] - player_direction["Left"]
        player_acceleration.y = player_direction["Down"] - player_direction["Up"]

        if player_acceleration.length() > 0:
            player_acceleration.normalize_ip()

    def on_key_release(event):
        global player_acceleration  # Make sure to access the global variable

        key = event.keysym
        if key in player_direction:
            player_direction[key] = 0

        player_acceleration.x = player_direction["Right"] - player_direction["Left"]
        player_acceleration.y = player_direction["Down"] - player_direction["Up"]

    def update_inventory(player, inventory_listbox):
        try:
            selected_index = inventory_listbox.curselection()[0]
            selected_item_name = inventory_listbox.get(selected_index).split(":")[0]
        except IndexError:
            selected_item_name = None
        inventory_listbox.delete(0, inventory_listbox.size())
        for slot_number, item in enumerate(player.inventory.slots):
            inventory_listbox.insert(tk.END, f"{item.name}: {item.count}")
        if selected_item_name is not None:
            for i, item in enumerate(player.inventory.slots):
                if item.name == selected_item_name:
                    inventory_listbox.select_set(i)
                    break

    def on_closing():
        nonlocal running
        if socket:
            send_large_data(socket, [-2, ""])
            socket.close()
        running = False
        pygame.quit()
        sys.exit()

    save_location = ""

    def save_world():
        def sw():
            save_root = tk.Tk()
            save_root.geometry("400x300")

            save_frame = tk.Frame(save_root, width=400, height=300)
            save_frame.pack()

            save_label = tk.Label(save_frame, text="Save world")
            save_label.pack(pady=5)

            selected_location_label = tk.Label(save_frame, text=f"Selected location: {save_location}")
            selected_location_label.pack(pady=5)

            def select_save_location():
                nonlocal save_location
                save_location = filedialog.askdirectory()
                selected_location_label.config(text=f"Selected location: {save_location}")
                if save_location != "":
                    save_world_button.config(state=tk.NORMAL)
                else:
                    save_world_button.config(state=tk.DISABLED)

            select_location_button = tk.Button(save_frame, text="Select save location", command=select_save_location)
            select_location_button.pack(pady=5)

            def save():
                try:
                    with open(save_location + f"/{world.name}.wrd", 'wb') as file:
                        dill.dump(world, file)
                        save_players = players[:]
                        save_players.append(player)
                        dill.dump(save_players, file)
                        file.close()
                except Exception as e:
                    print(e)

                for e in save_frame.winfo_children():
                    e.destroy()
                saved_label = tk.Label(save_frame, text="The world has been successfully saved!")
                saved_label.pack(pady=5)
                exit_buttom_saved = tk.Button(save_frame, text="Exit", command=sys.exit)
                exit_buttom_saved.pack(pady=5)

            save_world_button = tk.Button(save_frame, text="Save", command=save, state=tk.DISABLED)
            save_world_button.pack(pady=5)

            cancel_button = tk.Button(save_frame, text="Cancel", command=save_root.destroy)
            cancel_button.pack(pady=5)

            save_root.mainloop()

        sw_thread = threading.Thread(target=sw)
        sw_thread.daemon = True
        sw_thread.start()

    root = tk.Tk()
    root.geometry(f"{WIDTH + 400}x{HEIGHT}")
    root.title("slavery")
    root.bind("<KeyPress>", on_key_press)  # Bind key press event
    root.bind("<KeyRelease>", on_key_release)  # Bind key release event
    root.protocol("WM_DELETE_WINDOW", on_closing)

    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Menu", menu=menu)
    menu.add_command(label="Save", command=save_world)
    menu.add_command(label="Quit", command=on_closing)

    pygame_frame = tk.Frame(root, width=WIDTH, height=HEIGHT)
    pygame_frame.pack(side=tk.LEFT)

    # Frame for inventory
    inventory_frame = tk.Frame(root, width=400, height=HEIGHT)
    inventory_frame.pack()

    # Embed pygame into the tkinter frame
    os.environ['SDL_WINDOWID'] = str(pygame_frame.winfo_id())
    os.environ['SDL_VIDEODRIVER'] = 'windib'

    # Initialize pygame
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    pygame.init()

    player_id_label = tk.Label(inventory_frame, text=f"Player ID: {player.id}")
    player_id_label.pack()
    # Listbox for displaying inventory
    inventory_listbox = tk.Listbox(inventory_frame, selectmode="none")
    for item in player.inventory.slots:
        inventory_listbox.insert(tk.END, f"{item.name}: {item.count}")
    inventory_listbox.pack()

    crafting_frame = tk.Frame(root, width=400)

    crafting_list_frame = tk.Frame(crafting_frame)
    crafting_list_frame.pack()

    crafting_button = tk.Button(inventory_frame, text='Crafting',
                                command=lambda: crafting_frame.pack_forget() if crafting_frame.winfo_manager() else crafting_frame.pack())
    crafting_button.pack()

    # Create a scrollbar
    scrollbar = tk.Scrollbar(crafting_list_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Create a Listbox and attach the scrollbar
    crafting_list = tk.Listbox(crafting_list_frame, yscrollcommand=scrollbar.set, width=20, selectmode="none")
    crafting_list.pack(side=tk.LEFT)
    scrollbar.config(command=crafting_list.yview)

    # Function to populate the Listbox
    def populate_crafting_list():
        for item_id in Recipies.keys():
            item_name = Items[item_id].name  # Assuming Items dictionary is accessible
            crafting_list.insert(tk.END, item_name)

    # Populate the Listbox with craftable items
    populate_crafting_list()

    # Function to display required items
    def display_required_items(event=None):
        global last_selected_crafting_item  # Access the global variable
        complete = True
        selected_index = crafting_list.curselection()
        if selected_index:
            selected_item_id = list(Recipies.keys())[selected_index[0]]
            # Check if the selected item has changed
            if last_selected_crafting_item != selected_item_id:
                last_selected_crafting_item = selected_item_id  # Update the last selected item
        if last_selected_crafting_item in Recipies.keys():
            required_stations = Recipies[last_selected_crafting_item][0]
            present_stations = []
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    player_pos = pygame.Vector2((player.position.x // 50), (player.position.y // 50))
                    block_pos = pygame.Vector2(player_pos.x + dx, player_pos.y + dy)
                    if int(block_pos.x) in range(0, world.size * 16) and int(block_pos.y) in range(0, world.size * 16):
                        block = world.chunks[int(block_pos.x // 16), int(block_pos.y // 16)].blocks[
                            block_pos.x % 16, block_pos.y % 16]
                        if block.type:
                            try:
                                if any(rs[0] == int(block.type.split()[2]) for rs in
                                       required_stations) and block.type.split()[:2] == ["Crafting", "station"]:
                                    present_stations.append((int(block.type.split()[2]), block.name))
                            except IndexError or ValueError:
                                continue

            # Clear the existing items in the required items Listbox
            required_items_list.delete(0, tk.END)
            for station in required_stations:
                if station in present_stations:
                    color = "green"
                else:
                    color = "red"
                    complete = False
                required_items_list.insert(tk.END, f"Station required: {station[1]}")
                required_items_list.itemconfig(tk.END, {'fg': color})

            required_items = Recipies[last_selected_crafting_item][1]
            for item_id, amount in required_items:
                item_name = Items[item_id].name  # Assuming Items dictionary is accessible

                player_has_enough = False
                for i in player.inventory.slots:
                    if i.name == item_name and i.count >= amount:
                        player_has_enough = True

                color = "green" if player_has_enough else "red"
                if not player_has_enough:
                    complete = False
                required_items_list.insert(tk.END, f"{item_name} (x{amount})")
                required_items_list.itemconfig(tk.END, {'fg': color})
            craft_button.config(state=tk.NORMAL if complete else tk.DISABLED)

    # Create a Listbox for required items and attach the scrollbar
    required_items_list = tk.Listbox(crafting_list_frame, yscrollcommand=scrollbar.set, width=30)
    required_items_list.pack(side=tk.RIGHT)

    # Attach the click event to the main crafting list
    crafting_list.bind('<<ListboxSelect>>', display_required_items)

    def confirm_craft():
        player.inventory.add_item(Items[last_selected_crafting_item], 1)
        for item_id, amount in Recipies[last_selected_crafting_item][1]:
            player.inventory.remove_item(Items[item_id], amount)

    craft_button = tk.Button(crafting_frame, command=confirm_craft, text='Craft', state=tk.DISABLED)
    craft_button.pack()

    camera_offset = pygame.Vector2(0, 0)

    running = True

    while running:

        update_inventory(player, inventory_listbox)
        display_required_items()

        for event in pygame.event.get():
            # Detect block breaking
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Calculate the clicked block's position
                clicked_x = int((event.pos[0] + camera_offset.x) // BLOCK_SIZE)
                clicked_y = int((event.pos[1] + camera_offset.y) // BLOCK_SIZE)

                # Determine the chunk and block within the chunk
                chunk_x, chunk_y = clicked_x // 16, clicked_y // 16
                block_x, block_y = clicked_x % 16, clicked_y % 16

                # Boundary check for chunks
                if 0 <= chunk_x < world.size and 0 <= chunk_y < world.size:
                    drop_id = world.chunks[(chunk_x, chunk_y)].blocks[(block_x, block_y)].drop_id
                    if drop_id:
                        player.inventory.add_item(Items[drop_id], 1)
                    world.chunks[(chunk_x, chunk_y)].blocks[(block_x, block_y)] = Blocks[0]

                    if socket:
                        send_large_data(socket, [4, (chunk_x, chunk_y), (block_x, block_y), Blocks[0]])

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # Right mouse button
                # Calculate the clicked block's position
                clicked_x = int((event.pos[0] + camera_offset.x) // BLOCK_SIZE)
                clicked_y = int((event.pos[1] + camera_offset.y) // BLOCK_SIZE)

                # Determine the chunk and block within the chunk
                chunk_x, chunk_y = clicked_x // 16, clicked_y // 16
                block_x, block_y = clicked_x % 16, clicked_y % 16
                if world.chunks[(chunk_x, chunk_y)].blocks[(block_x, block_y)].transparent:
                    # Get selected item from inventory
                    selected_item_index = inventory_listbox.curselection()
                    if selected_item_index:
                        selected_item = player.inventory.slots[selected_item_index[0]]
                        # Check if the item has a block_form_id
                        if selected_item.block_form_id is not None:
                            # Get the block to be placed from Blocks list
                            block_to_place = Blocks[selected_item.block_form_id]
                            if 0 <= chunk_x < world.size and 0 <= chunk_y < world.size:
                                world.chunks[(chunk_x, chunk_y)].blocks[(block_x, block_y)] = block_to_place

                                if socket:
                                    send_large_data(socket, [4, (chunk_x, chunk_y), (block_x, block_y), block_to_place])

                            # Remove one unit of the item from the inventory
                            selected_item.count -= 1
                            if selected_item.count <= 0:
                                del player.inventory.slots[selected_item_index[0]]

                elif world.chunks[(chunk_x, chunk_y)].blocks[(block_x, block_y)].interact is not None:
                    world.chunks[(chunk_x, chunk_y)].blocks[(block_x, block_y)].interact(pygame_frame, inventory_frame,
                                                                                         player, world)
            if event.type == pygame.QUIT:
                running = False

        player.velocity += player_acceleration * PLAYER_SPEED

        # Apply drag
        player.velocity *= (1 - DRAG)

        player.position += player.velocity
        if socket:
            send_large_data(socket, [3, player])

        # Constrain player within borders
        player.position.x = max(0, min(world.size * 800 - PLAYER_SIZE, player.position.x))
        player.position.y = max(0, min(world.size * 800 - PLAYER_SIZE, player.position.y))

        # Update camera position
        camera_offset.x = player.position.x - WIDTH // 2
        camera_offset.y = player.position.y - HEIGHT // 2

        # Camera
        camera_offset = pygame.Vector2(player.position.x - WIDTH // 2, player.position.y - HEIGHT // 2)

        # Clear the screen
        screen.fill(WHITE)

        # Render visible blocks
        start_x = max(0, int(camera_offset.x // BLOCK_SIZE))
        end_x = int((camera_offset.x + WIDTH) // BLOCK_SIZE) + 1
        start_y = max(0, int(camera_offset.y // BLOCK_SIZE))
        end_y = int((camera_offset.y + HEIGHT) // BLOCK_SIZE) + 1

        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                chunk_x, chunk_y = x // 16, y // 16
                block_x, block_y = x % 16, y % 16

                # Boundary check for chunks
                if 0 <= chunk_x < world.size and 0 <= chunk_y < world.size:
                    block = world.chunks[(chunk_x, chunk_y)].blocks[(block_x, block_y)]
                    color = BLOCK_COLORS.get(block.id, WHITE)
                    pygame.draw.rect(screen, color, (x * BLOCK_SIZE - camera_offset.x,
                                                     y * BLOCK_SIZE - camera_offset.y,
                                                     BLOCK_SIZE, BLOCK_SIZE))

        # Draw chunk borders
        if chunk_borders:
            for x in range(0, (world.size + 1) * 16 * BLOCK_SIZE, 16 * BLOCK_SIZE):
                pygame.draw.line(screen, GREEN, (x - camera_offset.x, 0 - camera_offset.y),
                                 (x - camera_offset.x, world.size * 16 * BLOCK_SIZE - camera_offset.y), 5)
            for y in range(0, (world.size + 1) * 16 * BLOCK_SIZE, 16 * BLOCK_SIZE):
                pygame.draw.line(screen, GREEN, (0 - camera_offset.x, y - camera_offset.y),
                                 (world.size * 16 * BLOCK_SIZE - camera_offset.x, y - camera_offset.y), 5)

        # Draw players
        pygame.draw.rect(screen, player.color,
                         (player.position.x - camera_offset.x, player.position.y - camera_offset.y,
                          PLAYER_SIZE, PLAYER_SIZE))

        for p in players:
            if p.id != player.id:
                pygame.draw.rect(screen, p.color, (p.position.x - camera_offset.x, p.position.y - camera_offset.y,
                                                   PLAYER_SIZE, PLAYER_SIZE))

        pygame.display.flip()
        clock.tick(60)
        root.update()

    pygame.quit()
    root.destroy()
    sys.exit()
