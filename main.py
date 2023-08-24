import threading

import pygame
import tkinter as tk
from tkinter import messagebox, simpledialog
import sys

from classes.game_loop import game_loop
from classes.player import Player
from classes.world import World

# Initialize Pygame
pygame.init()

# Create the main window
root = tk.Tk()
root.title("Main Menu")
root.geometry("400x300")

# Create the main menu frame
main_menu_frame = tk.Frame(root)
main_menu_frame.pack()

# Create the creation menu frame
creation_menu_frame = tk.Frame(root)

# Button click functions
def create_world():
    main_menu_frame.pack_forget()  # Hide the main menu
    creation_menu_frame.pack()  # Show the creation menu

def exit_creation():
    creation_menu_frame.pack_forget()  # Hide the creation menu
    main_menu_frame.pack()  # Show the main menu

def confirm_creation():
    world_name = name_entry.get()
    chunk_size = size_entry.get()
    seed = hash(seed_entry.get())
    print(seed)

    if world_name and chunk_size.isdigit() and int(chunk_size) > 0:
        # Generate the world based on the provided information
        world = World(int(chunk_size), seed)
        world.generate_world()
        player = Player(800 // 2, 600 // 2)

        # Start the game loop in a separate thread
        game_thread = threading.Thread(target=game_loop, args=(world, player))
        game_thread.start()
        root.destroy()  # Destroy the creation menu

    else:
        messagebox.showerror("Invalid Input", "Please fill in the correct information.")

def validate_entries(event):
    world_name = name_entry.get()
    chunk_size = size_entry.get()

    if world_name and chunk_size.isdigit() and int(chunk_size) > 0:
        create_world_button.config(state=tk.NORMAL)
    else:
        create_world_button.config(state=tk.DISABLED)



# Create buttons in the main menu frame
create_button = tk.Button(main_menu_frame, text="Create World", command=create_world)
load_button = tk.Button(main_menu_frame, text="Load World", command=lambda: None)  # Placeholder function
multiplayer_button = tk.Button(main_menu_frame, text="Multiplayer", command=lambda: None)  # Placeholder function
exit_button = tk.Button(main_menu_frame, text="Exit", command=root.quit)  # Use root.quit

# Place buttons in the main menu frame
create_button.pack(pady=10)
load_button.pack(pady=10)
multiplayer_button.pack(pady=10)
exit_button.pack(pady=10)

# Create and place widgets in the creation menu frame
name_label = tk.Label(creation_menu_frame, text="World Name:")
name_entry = tk.Entry(creation_menu_frame)
size_label = tk.Label(creation_menu_frame, text="Chunk Size:")
size_entry = tk.Entry(creation_menu_frame)
seed_label = tk.Label(creation_menu_frame, text="Seed:")
seed_entry = tk.Entry(creation_menu_frame)
exit_creation_button = tk.Button(creation_menu_frame, text="Exit", command=exit_creation)
create_world_button = tk.Button(creation_menu_frame, text="Create World", state=tk.DISABLED, command=confirm_creation)

# Place widgets in the creation menu frame
name_label.pack(pady=5)
name_entry.pack(pady=5)
size_label.pack(pady=5)
size_entry.pack(pady=5)
seed_label.pack(pady=5)
seed_entry.pack(pady=5)
exit_creation_button.pack(pady=10)
create_world_button.pack(pady=10)

# Bind validate_entries function to the Entry widgets
name_entry.bind("<KeyRelease>", validate_entries)
size_entry.bind("<KeyRelease>", validate_entries)

# Start the main loop
root.mainloop()
