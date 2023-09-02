import socket
import socket
import subprocess
import sys

import dill
import select

from classes.player import Player


def send_large_data(sock, data):
    # Step 1: Serialize the data
    serialized_data = dill.dumps(data)

    # Step 2: Determine the size of the serialized data
    serialized_data_length = len(serialized_data)

    # Step 3: Send the size first
    sock.sendall(str(serialized_data_length).encode('utf-8'))
    sock.sendall(b'\n')  # Send a newline as a delimiter

    # Step 4: Send the actual data in chunks
    total_sent = 0
    while total_sent < serialized_data_length:
        sent = sock.send(serialized_data[total_sent:])
        if sent == 0:
            raise RuntimeError("Socket connection broken")
        total_sent += sent


def receive_large_data(sock, buffer_size=1024):
    # Step 1: Receive the size of the incoming data
    size_str = b''
    while True:
        chunk = sock.recv(1)  # Receive one byte at a time until we hit the newline
        if chunk == b'\n':
            break
        if chunk == b'':
            raise RuntimeError("Socket connection broken")
        size_str += chunk

    # Convert the size to an integer
    incoming_data_size = int(size_str.decode('utf-8'))

    # Step 2: Receive the actual data in chunks
    chunks = []
    bytes_received = 0
    while bytes_received < incoming_data_size:
        chunk = sock.recv(min(incoming_data_size - bytes_received, buffer_size))
        if chunk == b'':
            raise RuntimeError("Socket connection broken")
        chunks.append(chunk)
        bytes_received += len(chunk)

    # Combine the chunks
    serialized_data = b''.join(chunks)

    # Step 3: Deserialize the data
    original_data = dill.loads(serialized_data)

    return original_data


def initialize_server(world, players=None):
    current_id = 0
    # Initialize server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 12345))
    server_socket.listen(5)

    # List to keep track of socket descriptors
    connection_list = [server_socket]
    if not players:
        players = []

    print("Server started on port 12345")

    while True:
        read_sockets, _, _ = select.select(connection_list, [], [], 1)

        for sock in read_sockets:
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                connection_list.append(sockfd)
                print(f"Client ({addr}) connected")

                current_id += 1

                send_large_data(sockfd, [0, world, players])

                print(f"current id: {current_id}")

            else:
                try:
                    data_received = receive_large_data(sock)
                    if data_received:
                        # Forward the data to all other connected clients
                        for client_sock in connection_list:
                            if client_sock != server_socket and client_sock != sock:
                                send_large_data(client_sock, data_received)

                        update_id, *update_data = data_received

                        if update_id == 4:
                            x1, y1 = update_data[0]
                            x2, y2 = update_data[1]
                            block_type = update_data[2]

                            # Access
                            world.chunks[(x1, y1)].blocks[(x2, y2)] = block_type

                        if update_id == -1:
                            new_player = update_data[0]
                            players.append(new_player)

                            for s in connection_list:
                                if s != server_socket:
                                    send_large_data(s, [1, players])

                        if update_id == -2:
                            print("closing")
                            for s in connection_list:
                                if s != server_socket:
                                    send_large_data(s, [-404, ""])
                            sys.exit()


                except Exception as e:
                    print(f"An error occurred: {e}")
                    import traceback
                    traceback.print_exc()

                    if sock in connection_list:
                        print(f"Removing ({sock})")
                        connection_list.remove(sock)

        if connection_list == [server_socket]:
            print("closing")
            server_socket.close()
            sys.exit()
