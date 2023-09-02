import re
import socket
import subprocess
import threading

from elevate import elevate
import dill
import pygame
import tkinter as tk
from tkinter import messagebox, filedialog

from classes.game_loop import game_loop
from classes.player import Player
from classes.server import initialize_server, receive_large_data, send_large_data
from classes.world import World

elevate(False)
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

# Create singleplayer selection menu frame
singleplayer_selection_frame = tk.Frame(root)

# Create the creation menu frame
creation_menu_frame = tk.Frame(root)

# Create multiplayer selection menu frame
multiplayer_selection_frame = tk.Frame(root)

# Create multiplayer join menu frame
multiplayer_join_frame = tk.Frame(root)

# Create the load menu frame
load_menu_frame = tk.Frame(root)

file_location = ""


# Button click functions

def singleplayer_select():

    main_menu_frame.pack_forget()  # Hide the main menu
    singleplayer_selection_frame.pack()


def create_world():
    singleplayer_selection_frame.pack_forget()
    create_world_button.config(command=confirm_creation)
    creation_menu_frame.pack()


def load_world():
    singleplayer_selection_frame.pack_forget()
    load_world_button.config(command=confirm_load)
    load_menu_frame.pack()


def load_multiplayer_world():
    load_world_button.config(command=confirm_multiplayer_load)
    multiplayer_selection_frame.pack_forget()
    load_menu_frame.pack()


def multiplayer_select():
    main_menu_frame.pack_forget()  # Hide the main menu
    multiplayer_selection_frame.pack()


def back_to_main_menu():
    for e in root.winfo_children():
        e.pack_forget()
    main_menu_frame.pack()  # Show the main menu


def join_multiplayer_world():
    multiplayer_selection_frame.pack_forget()
    multiplayer_join_frame.pack()


def multiplayer_create():
    create_world_button.config(command=confirm_multiplayer_create)
    multiplayer_selection_frame.pack_forget()  # Hide the main menu
    creation_menu_frame.pack()  # Show the creation menu


def confirm_load():
    with open(file_location, 'rb') as file:
        world = dill.load(file)
        players = dill.load(file)

    id = int(player_id_entry.get())
    player = Player(800//2, 600//2, id)
    for p in players:
        if p.id == id:
            player = p
            players.remove(p)
            break

    game_thread = threading.Thread(target=game_loop, args=(world, player, None, players))
    game_thread.start()
    root.destroy()


def confirm_multiplayer_load():
    with open(file_location, 'rb') as file:
        world = dill.load(file)
        players = dill.load(file)

    id = int(player_id_entry.get())
    for p in players:
        if p.id == id:
            player = p
            break
    else:
        player = Player(800 // 2, 600 // 2, id)

    server_thread = threading.Thread(target=initialize_server, args=[world, players])
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
            players = update_data[1]
            # Start the game loop in a separate thread
            game_thread = threading.Thread(target=game_loop, args=(world, player, client_socket, players))
            game_thread.start()
            send_large_data(client_socket, [-1, player])
            root.destroy()



def multiplayer_join():
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
            players = update_data[1]
            id = int(id_entry.get())
            for p in players:
                if p.id == id:
                    player = p
                    break
            else:
                player = Player(800 // 2, 600 // 2, id)

            send_large_data(client_socket, [-1, player])

            # Start the game loop in a separate thread
            game_thread = threading.Thread(target=game_loop, args=(world, player, client_socket, players))
            game_thread.start()
            root.destroy()


def confirm_multiplayer_create():
    world = World(int(size_entry.get()), hash(seed_entry.get()), name_entry.get())
    world.generate_world()
    player = Player(800 // 2, 600 // 2, 0)
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
            send_large_data(client_socket, [-1, player])
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
        world = World(int(chunk_size), seed, world_name)
        world.generate_world()
        player = Player(800 // 2, 600 // 2, 0)

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
    id_value = id_entry.get()

    if bool(re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip_value)) and port_value.isdigit() and int(port_value) in range(1,
                                                                                                                  65535)\
            and id_value.isdigit() and int(id_value) >= 0:
        join_multiplayer_world_button.config(state=tk.NORMAL)
    else:
        join_multiplayer_world_button.config(state=tk.DISABLED)


def validate_entries_load(event):
    player_id = player_id_entry.get()
    if player_id.isdigit() and int(player_id) >= 0 and selected_location is not None:
        load_world_button.config(state=tk.NORMAL)
    else:
        load_world_button.config(state=tk.DISABLED)


# Create buttons in the main menu frame
singleplayer_button = tk.Button(main_menu_frame, text="Singleplayer", command=singleplayer_select)
multiplayer_button = tk.Button(main_menu_frame, text="Multiplayer", command=multiplayer_select)
exit_button = tk.Button(main_menu_frame, text="Exit", command=root.quit)  # Use root.quit

# Place buttons in the main menu frame
singleplayer_button.pack(pady=10)
multiplayer_button.pack(pady=10)
exit_button.pack(pady=10)

# Create widgets in the singleplayer selection menu
singleplayer_label = tk.Label(singleplayer_selection_frame, text="Singleplayer")
create_button = tk.Button(singleplayer_selection_frame, text="Create World", command=create_world)
load_button = tk.Button(singleplayer_selection_frame, text="Load World", command=load_world)
singleplayer_exit_button = tk.Button(singleplayer_selection_frame, text="Back", command=back_to_main_menu)

# Place widgets in the singleplayer selection menu frame
singleplayer_label.pack(pady=5)
create_button.pack(pady=5)
load_button.pack(pady=5)
singleplayer_exit_button.pack(pady=5)

# Create widgets in the creation menu frame
name_label = tk.Label(creation_menu_frame, text="World Name:")
name_entry = tk.Entry(creation_menu_frame)
size_label = tk.Label(creation_menu_frame, text="Chunk Size:")
size_entry = tk.Entry(creation_menu_frame)
seed_label = tk.Label(creation_menu_frame, text="Seed:")
seed_entry = tk.Entry(creation_menu_frame)
exit_creation_button = tk.Button(creation_menu_frame, text="Exit", command=back_to_main_menu)
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


def update_location():
    global file_location
    file_location = filedialog.askopenfilename(filetypes=[("World files", "*.wrd")])
    selected_location.config(text=f"Selected location: {file_location}")


# Create and place widgets in the load menu frame
load_label = tk.Label(load_menu_frame, text="Load in a saved world")
selected_location = tk.Label(load_menu_frame, text=f"Selected file: {file_location}")
select_button = tk.Button(load_menu_frame, text="Select", command=update_location)
player_id_label = tk.Label(load_menu_frame, text="Player ID")
player_id_entry = tk.Entry(load_menu_frame)
load_world_button = tk.Button(load_menu_frame, text="Load", command=confirm_load, state=tk.DISABLED)
back_load_button = tk.Button(load_menu_frame, text="Exit", command=back_to_main_menu)

# Place widgets in the creation menu frame
load_label.pack(pady=5)
selected_location.pack(pady=5)
select_button.pack(pady=5)
player_id_label.pack(pady=5)
player_id_entry.pack(pady=5)
load_world_button.pack(pady=5)
back_load_button.pack(pady=5)

# Bind validate_entries function to the Entry widgets
player_id_entry.bind("<KeyRelease>", validate_entries_load)

# Create and place widgets in the multiplayer selection menu frame
multiplayer_label = tk.Label(multiplayer_selection_frame, text="Multiplayer")
create_multiplayer_button = tk.Button(multiplayer_selection_frame, text="Create", command=multiplayer_create)
load_multiplayer_button = tk.Button(multiplayer_selection_frame, text="Load", command=load_multiplayer_world)
join_multiplayer_button = tk.Button(multiplayer_selection_frame, text="Join", command=join_multiplayer_world)
exit_multiplayer_creation_button = tk.Button(multiplayer_selection_frame, text="Back", command=back_to_main_menu)

# Place widgets in the multiplayer selection menu frame
multiplayer_label.pack(pady=5)
create_multiplayer_button.pack(pady=5)
load_multiplayer_button.pack(pady=5)
join_multiplayer_button.pack(pady=5)
exit_multiplayer_creation_button.pack(pady=10)

# Create and place widgets in the multiplayer join menu frame
join_multiplayer_label = tk.Label(multiplayer_join_frame, text="Join")
ip_label = tk.Label(multiplayer_join_frame, text="IP address")
ip_entry = tk.Entry(multiplayer_join_frame)
port_label = tk.Label(multiplayer_join_frame, text="Port")
port_entry = tk.Entry(multiplayer_join_frame)
id_label = tk.Label(multiplayer_join_frame, text="Player ID")
id_entry = tk.Entry(multiplayer_join_frame)
join_multiplayer_world_button = tk.Button(multiplayer_join_frame, text="Join", state=tk.DISABLED,
                                          command=multiplayer_join)
exit_multiplayer_join_button = tk.Button(multiplayer_join_frame, text="Exit", command=back_to_main_menu)

# Place widgets in the multiplayer selection menu frame
join_multiplayer_label.pack(pady=5)
ip_label.pack(pady=5)
ip_entry.pack(pady=5)
port_label.pack(pady=5)
port_entry.pack(pady=5)
id_label.pack(pady=5)
id_entry.pack(pady=5)
join_multiplayer_world_button.pack(pady=5)
exit_multiplayer_join_button.pack(pady=5)

# Bind validate_entries_creation function to the Entry widgets
ip_entry.bind("<KeyRelease>", validate_entries_join)
port_entry.bind("<KeyRelease>", validate_entries_join)
id_entry.bind("<KeyRelease>", validate_entries_join)

# Start the main loop
root.mainloop()
