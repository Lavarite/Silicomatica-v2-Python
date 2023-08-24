import sys

import pygame

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

def game_loop(world, player):
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Game Title")
    clock = pygame.time.Clock()
    camera_offset = pygame.Vector2(0, 0)
    chunk_borders = False

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
                    print(str(player.inventory))
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and pygame.key.get_pressed()[pygame.K_b]:
                chunk_borders = not chunk_borders

        # Player movement using vectors
        keys = pygame.key.get_pressed()
        player_acceleration = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_acceleration.x = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_acceleration.x = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player_acceleration.y = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player_acceleration.y = 1

        if player_acceleration.length() > 0:
            player_acceleration.normalize_ip()

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

    pygame.quit()
    sys.exit()


