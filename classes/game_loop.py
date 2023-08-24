import os
import sys

import pygame
import tkinter as tk
from classes.block import Blocks
from classes.item import Items

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
    6: (0, 0, 255)  # Water (Blue)
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

def game_loop(world, player):
    '''
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Game Title")
    clock = pygame.time.Clock()
    '''
    root = tk.Tk()
    root.geometry(f"{WIDTH+200}x{HEIGHT}")
    root.title("slavery")
    root.bind("<KeyPress>", on_key_press)  # Bind key press event
    root.bind("<KeyRelease>", on_key_release)  # Bind key release event

    pygame_frame = tk.Frame(root, width=WIDTH, height=HEIGHT)
    pygame_frame.pack(side=tk.LEFT)

    # Frame for inventory
    inventory_frame = tk.Frame(root, width=200, height=HEIGHT)
    inventory_frame.pack()

    # Embed pygame into the tkinter frame
    os.environ['SDL_WINDOWID'] = str(pygame_frame.winfo_id())
    os.environ['SDL_VIDEODRIVER'] = 'windib'

    # Initialize pygame
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    pygame.init()

    # Listbox for displaying inventory
    inventory_listbox = tk.Listbox(inventory_frame)
    for item in player.inventory.slots:
        inventory_listbox.insert(tk.END, f"{item.name}: {item.count}")
    inventory_listbox.pack(fill=tk.BOTH, expand=True)

    camera_offset = pygame.Vector2(0, 0)

    running = True
    while running:
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
                    update_inventory(player, inventory_listbox)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # Right mouse button
                # Get selected item from inventory
                selected_item_index = inventory_listbox.curselection()
                if selected_item_index:
                    selected_item = player.inventory.slots[selected_item_index[0]]
                    # Check if the item has a block_form_id
                    if selected_item.block_form_id is not None:
                        # Get the block to be placed from Blocks list
                        block_to_place = Blocks[selected_item.block_form_id]

                        # Calculate the clicked block's position
                        clicked_x = int((event.pos[0] + camera_offset.x) // BLOCK_SIZE)
                        clicked_y = int((event.pos[1] + camera_offset.y) // BLOCK_SIZE)

                        # Determine the chunk and block within the chunk
                        chunk_x, chunk_y = clicked_x // 16, clicked_y // 16
                        block_x, block_y = clicked_x % 16, clicked_y % 16
                        if world.chunks[(chunk_x,chunk_y)].blocks[(block_x,block_y)].transparent:
                            if 0 <= chunk_x < world.size and 0 <= chunk_y < world.size:
                                world.chunks[(chunk_x,chunk_y)].blocks[(block_x,block_y)]=block_to_place

                            # Remove one unit of the item from the inventory
                            selected_item.count -= 1
                            if selected_item.count <= 0:
                                del player.inventory.slots[selected_item_index[0]]
                            update_inventory(player, inventory_listbox)
            if event.type == pygame.QUIT:
                running = False

        player.velocity += player_acceleration * PLAYER_SPEED

        # Apply drag
        player.velocity *= (1 - DRAG)

        player.position += player.velocity

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
            for x in range(0, (world.size+1) * 16 * BLOCK_SIZE, 16 * BLOCK_SIZE):
                pygame.draw.line(screen, GREEN, (x - camera_offset.x, 0 - camera_offset.y),
                                 (x - camera_offset.x, world.size * 16 * BLOCK_SIZE - camera_offset.y), 5)
            for y in range(0, (world.size+1) * 16 * BLOCK_SIZE, 16 * BLOCK_SIZE):
                pygame.draw.line(screen, GREEN, (0 - camera_offset.x, y - camera_offset.y),
                                 (world.size * 16 * BLOCK_SIZE - camera_offset.x, y - camera_offset.y), 5)

        # Draw player
        pygame.draw.rect(screen, RED, (player.position.x - camera_offset.x, player.position.y - camera_offset.y,
                                       PLAYER_SIZE, PLAYER_SIZE))

        pygame.display.flip()
        clock.tick(60)
        root.update()

    pygame.quit()
    sys.exit()


