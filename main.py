import re
import socket
import subprocess
import threading

import dill
import pygame
import tkinter as tk
from tkinter import messagebox, simpledialog
import sys

from classes.game_loop import game_loop
from classes.player import Player
from classes.server import initialize_server, receive_large_data
from classes.world import World

rule_in_name = "BuyLabour"
rule_out_name = "SellLabour"
command_in = f"netsh advfirewall firewall add rule name={rule_in_name} dir=in action=allow protocol=TCP localport={12345}"
command_out = f"netsh advfirewall firewall add rule name={rule_out_name} dir=out action=allow protocol=TCP localport={12345}"
subprocess.run(command_in, shell=True)
subprocess.run(command_out, shell=True)

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

# Create multiplayer selection menu frame
multiplayer_selection_frame = tk.Frame(root)

# Create multiplayer join menu frame
multiplayer_join_frame = tk.Frame(root)

# Button click functions
def create_world():
    create_world_button.config(command=confirm_creation)
    main_menu_frame.pack_forget()  # Hide the main menu
    creation_menu_frame.pack()  # Show the creation menu

def multiplayer_select():
    main_menu_frame.pack_forget()  # Hide the main menu
    multiplayer_selection_frame.pack()  # Show the creation menu

def exit_creation():
    creation_menu_frame.pack_forget()  # Hide the creation menu
    multiplayer_selection_frame.pack_forget()
    multiplayer_join_frame.pack_forget()
    main_menu_frame.pack()  # Show the main menu

def join_multiplayer_world():
    multiplayer_selection_frame.pack_forget()
    multiplayer_join_frame.pack()

def multiplayer_create():
    create_world_button.config(command=confirm_multiplayer_create)
    multiplayer_selection_frame.pack_forget()  # Hide the main menu
    creation_menu_frame.pack()  # Show the creation menu
def multiplayer_join():
    player = Player(800 // 2, 600 // 2)
    # Initialize client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((ip_entry.get(), int(port_entry.get())))
    except Exception as e:
        print(e)
        messagebox.showerror("showerror", "Failed to connect to the server")
        return

    # Receive initial world state
    data_received = receive_large_data(client_socket)
    if data_received:
        update_id, *update_data = data_received
        if update_id == 0:  # Initial world state
            world = update_data[0]
            player = update_data[1]
            # Start the game loop in a separate thread
            game_thread = threading.Thread(target=game_loop, args=(world, player, client_socket))
            game_thread.start()
            root.destroy()

def confirm_multiplayer_create():
    world = World(int(size_entry.get()), hash(seed_entry.get()))
    world.generate_world()
    player = Player(800 // 2, 600 // 2)
    server_thread = threading.Thread(target=initialize_server, args=[world])
    server_thread.start()

    # Connect to the server
    server_address = ('localhost', 12345)  # Replace with the actual server IP and port
    # Initialize client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect(server_address)
    # Receive initial world state
    data_received = receive_large_data(client_socket)
    if data_received:
        update_id, *update_data = data_received
        if update_id == 0:  # Initial world state
            world = update_data[0]
            player = update_data[1]
            # Start the game loop in a separate thread
            game_thread = threading.Thread(target=game_loop, args=(world, player, client_socket))
            game_thread.start()
            root.destroy()

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

        game_thread = threading.Thread(target=game_loop, args=(world, player))
        game_thread.start()

        root.destroy()  # Destroy the creation menu

    else:
        messagebox.showerror("Invalid Input", "Please fill in the correct information.")

def validate_entries_creation(event):
    world_name = name_entry.get()
    chunk_size = size_entry.get()

    if world_name and chunk_size.isdigit() and int(chunk_size) > 0:
        create_world_button.config(state=tk.NORMAL)
    else:
        create_world_button.config(state=tk.DISABLED)


def validate_entries_join(event):
    ip_value = ip_entry.get()
    port_value = port_entry.get()

    if bool(re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip_value)) and port_value.isdigit() and int(port_value) in range(1, 65535):
        join_multiplayer_world_button.config(state=tk.NORMAL)
    else:
        join_multiplayer_world_button.config(state=tk.DISABLED)


# Create buttons in the main menu frame
create_button = tk.Button(main_menu_frame, text="Create World", command=create_world)
load_button = tk.Button(main_menu_frame, text="Load World", command=lambda: None)  # Placeholder function
multiplayer_button = tk.Button(main_menu_frame, text="Multiplayer", command=multiplayer_select)  # Placeholder function
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
name_entry.bind("<KeyRelease>", validate_entries_creation)
size_entry.bind("<KeyRelease>", validate_entries_creation)

# Create and place widgets in the multiplayer selection menu frame
multiplayer_label = tk.Label(multiplayer_selection_frame, text="Multiplayer")
create_multiplayer_button = tk.Button(multiplayer_selection_frame, text="Create", command=multiplayer_create)
join_multiplayer_button = tk.Button(multiplayer_selection_frame, text="Join", command=join_multiplayer_world)
exit_multiplayer_creation_button = tk.Button(multiplayer_selection_frame, text="Back", command=exit_creation)

# Place widgets in the multiplayer selection menu frame
multiplayer_label.pack(pady=5)
create_multiplayer_button.pack(pady=10)
join_multiplayer_button.pack(pady=10)
exit_multiplayer_creation_button.pack(pady=15)

# Create and place widgets in the multiplayer join menu frame
join_multiplayer_label = tk.Label(multiplayer_join_frame, text="Multiplayer")
ip_label = tk.Label(multiplayer_join_frame, text="IP address")
ip_entry = tk.Entry(multiplayer_join_frame)
port_label = tk.Label(multiplayer_join_frame, text="Port")
port_entry = tk.Entry(multiplayer_join_frame)
join_multiplayer_world_button = tk.Button(multiplayer_join_frame, text="Join", state=tk.DISABLED, command=multiplayer_join)
exit_multiplayer_join_button = tk.Button(multiplayer_join_frame, text="Exit", command=exit_creation)

# Place widgets in the multiplayer selection menu frame
join_multiplayer_label.pack(pady=5)
ip_label.pack(pady=15)
ip_entry.pack(pady=5)
port_label.pack(pady=5)
port_entry.pack(pady=5)
join_multiplayer_world_button.pack(pady=10)
exit_multiplayer_join_button.pack(pady=5)

# Bind validate_entries_creation function to the Entry widgets
ip_entry.bind("<KeyRelease>", validate_entries_join)
port_entry.bind("<KeyRelease>", validate_entries_join)

# Start the main loop
root.mainloop()
