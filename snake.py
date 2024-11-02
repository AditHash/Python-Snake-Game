import pygame
import random
import sys
import os

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 640, 320
MARGIN = 0  # Visible boundary margin size
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Snake Game")

# Colors and fonts
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)  # Bonus food color
font = pygame.font.SysFont(None, 35)

# Block size and speed
BLOCK_SIZE = 20
SNAKE_SPEED = 8

# Define the graphics path
GRAPHICS_PATH = os.path.join(os.getcwd(), "assets")

# Load images for snake parts
head_imgs = {
    "left": pygame.image.load(os.path.join(GRAPHICS_PATH, "head_left.png")).convert_alpha(),
    "right": pygame.image.load(os.path.join(GRAPHICS_PATH, "head_right.png")).convert_alpha(),
    "up": pygame.image.load(os.path.join(GRAPHICS_PATH, "head_up.png")).convert_alpha(),
    "down": pygame.image.load(os.path.join(GRAPHICS_PATH, "head_down.png")).convert_alpha()
}

body_imgs = {
    "horizontal": pygame.image.load(os.path.join(GRAPHICS_PATH, "body_horizontal.png")).convert_alpha(),
    "vertical": pygame.image.load(os.path.join(GRAPHICS_PATH, "body_vertical.png")).convert_alpha(),
    "top_left": pygame.image.load(os.path.join(GRAPHICS_PATH, "body_topleft.png")).convert_alpha(),
    "top_right": pygame.image.load(os.path.join(GRAPHICS_PATH, "body_topright.png")).convert_alpha(),
    "bottom_left": pygame.image.load(os.path.join(GRAPHICS_PATH, "body_bottomleft.png")).convert_alpha(),
    "bottom_right": pygame.image.load(os.path.join(GRAPHICS_PATH, "body_bottomright.png")).convert_alpha()
}

tail_imgs = {
    "left": pygame.image.load(os.path.join(GRAPHICS_PATH, "tail_left.png")).convert_alpha(),
    "right": pygame.image.load(os.path.join(GRAPHICS_PATH, "tail_right.png")).convert_alpha(),
    "up": pygame.image.load(os.path.join(GRAPHICS_PATH, "tail_up.png")).convert_alpha(),
    "down": pygame.image.load(os.path.join(GRAPHICS_PATH, "tail_down.png")).convert_alpha()
}

food_img = pygame.image.load(os.path.join(GRAPHICS_PATH, "apple.png")).convert_alpha()
bonus_food_img = pygame.image.load(os.path.join(GRAPHICS_PATH, "cookies.png")).convert_alpha()  # Load bonus food

# Scale images to fit the block size
for key in head_imgs:
    head_imgs[key] = pygame.transform.scale(head_imgs[key], (BLOCK_SIZE, BLOCK_SIZE))
for key in body_imgs:
    body_imgs[key] = pygame.transform.scale(body_imgs[key], (BLOCK_SIZE, BLOCK_SIZE))
for key in tail_imgs:
    tail_imgs[key] = pygame.transform.scale(tail_imgs[key], (BLOCK_SIZE, BLOCK_SIZE))
food_img = pygame.transform.scale(food_img, (BLOCK_SIZE, BLOCK_SIZE))
bonus_food_img = pygame.transform.scale(bonus_food_img, (BLOCK_SIZE, BLOCK_SIZE))  # Scale bonus food

# Load and scale the background image
background_img = pygame.image.load(os.path.join(GRAPHICS_PATH, "background.png")).convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

# Load eating sound
eating_sound = pygame.mixer.Sound(os.path.join(GRAPHICS_PATH, "EatSound.ogg"))

# Display score
def display_score(score):
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, [10, 10])

# Show the game over screen with score and options
def show_game_over_screen(score):
    screen.fill(WHITE)
    game_over_text = font.render("Game Over!", True, RED)
    score_text = font.render(f"Score: {score}", True, RED)
    play_again_text = font.render("C - Play Again", True, BLACK)
    quit_text = font.render("Q - Quit", True, BLACK)

    # Draw a bordered box
    box_rect = pygame.Rect(WIDTH // 4, HEIGHT // 3, WIDTH // 2, HEIGHT // 3)
    pygame.draw.rect(screen, BLACK, box_rect, 2)  # Border
    pygame.draw.rect(screen, WHITE, box_rect)      # Fill box

    # Position text
    screen.blit(game_over_text, (WIDTH // 3, HEIGHT // 3 + 10))
    screen.blit(score_text, (WIDTH // 3, HEIGHT // 3 + 50))
    screen.blit(play_again_text, (WIDTH // 3, HEIGHT // 3 + 100))
    screen.blit(quit_text, (WIDTH // 3, HEIGHT // 3 + 130))

    pygame.display.flip()

    # Wait for user input
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    waiting = False
                if event.key == pygame.K_c:
                    waiting = False
                    game_loop()  # Restart game

# Determine the correct image for each segment based on direction and position
def get_segment_image(segment, prev_segment, next_segment):
    if prev_segment is None and next_segment:  # Head
        if next_segment[0] > segment[0]: return head_imgs["left"]  # Moving right
        if next_segment[0] < segment[0]: return head_imgs["right"]  # Moving left
        if next_segment[1] > segment[1]: return head_imgs["up"]    # Moving down
        if next_segment[1] < segment[1]: return head_imgs["down"]  # Moving up
    elif next_segment is None and prev_segment:  # Tail
        if prev_segment[0] > segment[0]: return tail_imgs["left"]  # Tail points left
        if prev_segment[0] < segment[0]: return tail_imgs["right"] # Tail points right
        if prev_segment[1] > segment[1]: return tail_imgs["up"]    # Tail points up
        if prev_segment[1] < segment[1]: return tail_imgs["down"]  # Tail points down
    elif prev_segment and next_segment:  # Body
        if prev_segment[0] == next_segment[0]:  # Vertical body
            return body_imgs["vertical"]
        if prev_segment[1] == next_segment[1]:  # Horizontal body
            return body_imgs["horizontal"]
        # Determine corner segments based on relative positions
        if (prev_segment[0] < segment[0] and next_segment[1] < segment[1]) or \
           (next_segment[0] < segment[0] and prev_segment[1] < segment[1]):
            return body_imgs["top_left"]
        if (prev_segment[0] < segment[0] and next_segment[1] > segment[1]) or \
           (next_segment[0] < segment[0] and prev_segment[1] > segment[1]):
            return body_imgs["bottom_left"]
        if (prev_segment[0] > segment[0] and next_segment[1] < segment[1]) or \
           (next_segment[0] > segment[0] and prev_segment[1] < segment[1]):
            return body_imgs["top_right"]
        if (prev_segment[0] > segment[0] and next_segment[1] > segment[1]) or \
           (next_segment[0] > segment[0] and prev_segment[1] > segment[1]):
            return body_imgs["bottom_right"]

    # Default return if no condition is met
    return body_imgs["vertical"]

def game_loop():
    game_over = False
    game_close = False
    score = 0  # Initialize score

    # Start the snake at the center of the screen
    x, y = WIDTH // 2, HEIGHT // 2
    dx, dy = BLOCK_SIZE, 0  # Start moving to the right

    # Initial snake body with a length of 3
    snake_body = [[x, y], [x - BLOCK_SIZE, y], [x - 2 * BLOCK_SIZE, y]]
    snake_length = 3

    # Place food at a random location
    food_x = random.randrange(MARGIN, WIDTH - BLOCK_SIZE - MARGIN, BLOCK_SIZE)
    food_y = random.randrange(MARGIN, HEIGHT - BLOCK_SIZE - MARGIN, BLOCK_SIZE)

    # Set up bonus food parameters
    bonus_active = False
    bonus_x, bonus_y = None, None
    bonus_counter = random.randint(4, 7)  # Trigger after eating between 4 and 7 apples

    # Game clock
    clock = pygame.time.Clock()

    while not game_over:
        while game_close:
            show_game_over_screen(score)  # Show the game over screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and dx == 0:
                    dx, dy = -BLOCK_SIZE, 0
                elif event.key == pygame.K_RIGHT and dx == 0:
                    dx, dy = BLOCK_SIZE, 0
                elif event.key == pygame.K_UP and dy == 0:
                    dx, dy = 0, -BLOCK_SIZE
                elif event.key == pygame.K_DOWN and dy == 0:
                    dx, dy = 0, BLOCK_SIZE

        # Update the snake's position
        x += dx
        y += dy

        # Check for boundary collision (game over if out of bounds)
        if x >= WIDTH - MARGIN or x < MARGIN or y >= HEIGHT - MARGIN or y < MARGIN:
            game_close = True

        # Draw background and boundary
        screen.blit(background_img, (0, 0))
        pygame.draw.rect(screen, RED, (MARGIN, MARGIN, WIDTH - 2 * MARGIN, HEIGHT - 2 * MARGIN), 2)
        screen.blit(food_img, (food_x, food_y))

        # Create new head position and insert it at the start of the snake body
        snake_head = [x, y]
        snake_body.insert(0, snake_head)

        # Check if snake eats food
        if snake_head[0] == food_x and snake_head[1] == food_y:
            score += 1
            eating_sound.play()  # Play eating sound
            food_x = random.randrange(MARGIN, WIDTH - BLOCK_SIZE - MARGIN, BLOCK_SIZE)
            food_y = random.randrange(MARGIN, HEIGHT - BLOCK_SIZE - MARGIN, BLOCK_SIZE)
            bonus_counter -= 1  # Decrease the counter for bonus food
            if bonus_counter <= 0 and not bonus_active:
                # Activate bonus food
                bonus_active = True
                bonus_x = random.randrange(MARGIN, WIDTH - BLOCK_SIZE - MARGIN, BLOCK_SIZE)
                bonus_y = random.randrange(MARGIN, HEIGHT - BLOCK_SIZE - MARGIN, BLOCK_SIZE)
        else:
            # Remove last segment if not eating
            snake_body.pop()

        # Check if the snake eats the bonus food
        if bonus_active and snake_head[0] == bonus_x and snake_head[1] == bonus_y:
            score += 5  # Add 5 points for bonus food
            eating_sound.play()  # Play eating sound
            bonus_active = False  # Deactivate bonus food
            bonus_counter = random.randint(4, 7)  # Reset bonus counter

        # Draw each segment of the snake with the correct image
        for i, segment in enumerate(snake_body):
            prev_segment = snake_body[i - 1] if i > 0 else None
            next_segment = snake_body[i + 1] if i < len(snake_body) - 1 else None
            segment_image = get_segment_image(segment, prev_segment, next_segment)
            screen.blit(segment_image, segment)

        # Draw bonus food if active
        if bonus_active:
            screen.blit(bonus_food_img, (bonus_x, bonus_y))  # Display cookies.png as bonus food

        display_score(score)
        pygame.display.update()

        # Check for self-collision
        if snake_head in snake_body[1:]:
            game_close = True

        clock.tick(SNAKE_SPEED)  # Control the game speed

    pygame.quit()
    sys.exit()

# Run the game
game_loop()
