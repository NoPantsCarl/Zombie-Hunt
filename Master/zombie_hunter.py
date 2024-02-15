import pygame
import random
import sys
import os
from pygame.locals import *

# Initialize pygame
pygame.init()

# Set up screen
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Zombie Hunter")

# Set up colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)

# Load images and resize
assets_folder = os.path.join(os.path.dirname(__file__), 'assets')
background_img = pygame.image.load(os.path.join(assets_folder, 'background.png')).convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
crosshair_img = pygame.image.load(os.path.join(assets_folder, 'crosshair.png')).convert_alpha()
crosshair_img = pygame.transform.scale(crosshair_img, (100, 100))

# Load zombie images
zombie_images = [pygame.image.load(os.path.join(assets_folder, f'zombie_{i}.png')).convert_alpha() for i in range(1, 14)]

# Set up game variables
max_zombie_speed = 10  # Maximum zombie speed
zombie_speed = 5
score = 0
kills = 0  # Track the number of kills
font_size = 36
font = pygame.font.Font(None, font_size)
high_score_font = pygame.font.Font(None, font_size)  # Adjusted high score font size
zombie_list = []
killing_spree = False
game_over_sound_played = False  # Initialize flag
game_over_sound = pygame.mixer.Sound(os.path.join(assets_folder, "game_over.mp3"))  # Load game over sound
hit_sound = pygame.mixer.Sound(os.path.join(assets_folder, "hit.mp3"))  # Load hit sound
hit_sound.set_volume(0.25)  # Set hit sound volume to 25%
miss_sound = pygame.mixer.Sound(os.path.join(assets_folder, "miss.mp3"))  # Load miss sound
miss_sound.set_volume(0.1)  # Set miss sound volume to 10%
spawn_delay = 30  # Initial spawn delay
background_music = pygame.mixer.Sound(os.path.join(assets_folder, "background_noise.mp3"))  # Load background noise
background_music.set_volume(0.1)  # Set background noise volume to 10%
background_music.play(-1)  # Play background noise continuously
killing_spree_sound = pygame.mixer.Sound(os.path.join(assets_folder, "killing_spree.mp3"))  # Load killing spree sound

# Load high score from file
sav_folder = os.path.join(os.path.dirname(__file__), 'sav')
high_score_file = os.path.join(sav_folder, 'high_score.txt')
try:
    with open(high_score_file, 'r') as f:
        high_score = int(f.read())
except FileNotFoundError:
    high_score = 0

# Function to save the high score to a text file
def save_high_score(score):
    with open(high_score_file, 'w') as f:
        f.write(str(score))

# Function to create a zombie
def create_zombie():
    zombie_img = random.choice(zombie_images)  # Randomly select a zombie image
    original_width, original_height = zombie_img.get_size()
    scaled_width = original_width // 5
    scaled_height = original_height // 5
    zombie_img = pygame.transform.scale(zombie_img, (scaled_width, scaled_height))
    zombie_x = random.randint(0, WIDTH - scaled_width)
    zombie_y = random.randint(0, HEIGHT - scaled_height)
    return {'x': zombie_x, 'y': zombie_y, 'speed': zombie_speed, 'image': zombie_img}

# Function to draw text on screen
def draw_text(text, font, color, surface, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))  # Center the text
    pygame.draw.rect(surface, BLACK, (text_rect.left - 5, text_rect.top - 5, text_rect.width + 10, text_rect.height + 10))  # Add black box background
    surface.blit(text_surface, text_rect)

# Function to display game over popup
def display_game_over_popup():
    popup_font = pygame.font.Font(None, 48)
    popup_text = popup_font.render("You Died!", True, WHITE)
    popup_rect = popup_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))  # Center "You Died"
    popup_box_width = popup_rect.width + 20
    popup_box_height = popup_rect.height + 20
    pygame.draw.rect(screen, BLACK, (popup_rect.centerx - popup_box_width // 2, popup_rect.centery - popup_box_height // 2, popup_box_width, popup_box_height))  # Draw black box
    screen.blit(popup_text, popup_rect)

    # Display high score below "You Died"
    draw_text(f"High Score: {high_score}", high_score_font, WHITE, screen, WIDTH // 2, popup_rect.bottom + 50)  # Adjusted y-coordinate

    # Draw start over button
    start_over_rect = pygame.Rect(WIDTH // 2 - 100, popup_rect.bottom + 100, 200, 50)  # Increased button height for better readability
    pygame.draw.rect(screen, BLACK, start_over_rect)
    draw_text("Start Over", font, WHITE, screen, start_over_rect.centerx, start_over_rect.centery)

    # Draw give up button
    give_up_rect = pygame.Rect(WIDTH // 2 - 100, start_over_rect.bottom + 20, 200, 50)  # Increased button height for better readability
    pygame.draw.rect(screen, BLACK, give_up_rect)
    draw_text("Give Up", font, WHITE, screen, give_up_rect.centerx, give_up_rect.centery)

    return start_over_rect, give_up_rect

# Function to check if the given position is inside the start over button area
def is_inside_start_over_button(pos, start_over_rect):
    return start_over_rect.collidepoint(pos)

# Function to check if the given position is inside the give up button area
def is_inside_give_up_button(pos, give_up_rect):
    return give_up_rect.collidepoint(pos)

# Initialize timer
timer = 0
game_over_timer = 0  # Timer for game over screen

# Game loop
running = True
game_over = False  # Initialize game over flag
while running:
    screen.fill(BLACK)
    screen.blit(background_img, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    screen.blit(crosshair_img, (mouse_pos[0] - crosshair_img.get_width() // 2, mouse_pos[1] - crosshair_img.get_height() // 2))

    # Display score and high score in upper-right corner
    draw_text(f"Score: {score}", font, WHITE, screen, WIDTH - 150, 50)  # Original y-coordinate
    draw_text(f"High Score: {high_score}", high_score_font, WHITE, screen, WIDTH - 150, 100)  # Original y-coordinate

    # Check events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_over:
                start_over_rect, give_up_rect = display_game_over_popup()
                if is_inside_start_over_button(mouse_pos, start_over_rect):
                    # Start Over button clicked
                    timer = 0  # Reset timer
                    game_over = False  # Reset game over flag
                    zombie_list = []  # Clear zombie list
                    score = 0  # Reset score
                elif is_inside_give_up_button(mouse_pos, give_up_rect):
                    running = False  # Exit game if "Give Up" button clicked
            else:
                if event.button == 1:  # Left mouse button clicked
                    mouse_pos = pygame.mouse.get_pos()
                    hit = False
                    for zombie in zombie_list:
                        zombie_rect = zombie['image'].get_rect(topleft=(zombie['x'], zombie['y']))
                        if zombie_rect.collidepoint(mouse_pos):
                            zombie_list.remove(zombie)
                            score += 1
                            hit_sound.play()  # Play hit sound
                            hit = True
                            kills += 1  # Increment kills
                            if kills % 5 == 0:  # Increase zombie speed every 5 kills
                                zombie_speed *= 1.1  # Increase zombie speed by 10%
                            if score % 100 == 0:
                                killing_spree = True
                                killing_spree_sound.play()  # Play killing spree sound
                            break  # Exit the loop once a zombie is hit
                    if not hit:  # If no zombie was hit
                        miss_sound.play()  # Play miss sound
                        if score == 0:  # If score is zero after a miss
                            game_over_sound.play()  # Play game over sound
                            game_over = True  # Set game over flag
                        else:
                            # Update high score if necessary
                            if score > high_score:
                                high_score = score
                                save_high_score(high_score)
                            score = 0  # Set score back to zero
                            zombie_speed = 5  # Reset zombie speed to default value

    if game_over:
        # Increment game over timer
        game_over_timer += pygame.time.get_ticks()

        # Display game over popup
        start_over_rect, give_up_rect = display_game_over_popup()

        # Restart the game after 24 hours (86400000 milliseconds)
        if game_over_timer >= 86400000:
            game_over = False
            zombie_list = []
            score = 0
            game_over_timer = 0
            pygame.display.flip()
            continue

    # Spawn zombies continuously
    if not game_over and random.randint(0, spawn_delay) == 0:
        zombie_list.append(create_zombie())

    # Update zombie positions
    for zombie in zombie_list:
        zombie['x'] += zombie['speed']
        if zombie['x'] > WIDTH:
            zombie_list.remove(zombie)

    # Draw zombies
    for zombie in zombie_list:
        screen.blit(zombie['image'], (zombie['x'], zombie['y']))

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()
