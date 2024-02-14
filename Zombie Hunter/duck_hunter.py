import pygame
import random
import sys
from pygame.locals import *

# Initialize pygame
pygame.init()

# Set up screen
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Duck Hunter")

# Set up colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)

# Load images and resize
background_img = pygame.image.load('background.png').convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
duck_img = pygame.image.load('duck.png').convert_alpha()
duck_img = pygame.transform.scale(duck_img, (100, 100))
crosshair_img = pygame.image.load('crosshair.png').convert_alpha()
crosshair_img = pygame.transform.scale(crosshair_img, (100, 100))

# Set up game variables
max_duck_speed = 10  # Maximum duck speed
duck_speed = 5
score = 0
font = pygame.font.Font(None, 36)
duck_list = []
killing_spree = False
game_over_sound_played = False  # Initialize flag
game_over_sound = pygame.mixer.Sound("game_over.mp3")  # Load game over sound
hit_sound = pygame.mixer.Sound("hit.mp3")  # Load hit sound
hit_sound.set_volume(0.25)  # Set hit sound volume to 25%
miss_sound = pygame.mixer.Sound("miss.mp3")  # Load miss sound
miss_sound.set_volume(0.1)  # Set miss sound volume to 10%
spawn_delay = 30  # Initial spawn delay
background_music = pygame.mixer.Sound("background_noise.mp3")  # Load background noise
background_music.set_volume(0.1)  # Set background noise volume to 10%
background_music.play(-1)  # Play background noise continuously
killing_spree_sound = pygame.mixer.Sound("killing_spree.mp3")  # Load killing spree sound

# Function to create a duck
def create_duck():
    duck_x = random.randint(0, WIDTH - duck_img.get_width())
    duck_y = random.randint(0, HEIGHT - duck_img.get_height())
    return {'x': duck_x, 'y': duck_y, 'speed': duck_speed}

# Function to draw text on screen
def draw_text(text, font, color, surface, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    pygame.draw.rect(surface, BLACK, (x, y, text_rect.width, text_rect.height))
    surface.blit(text_surface, text_rect)

# Function to draw menu
def draw_menu():
    give_up_rect = pygame.Rect(20, 20, 180, 30)
    pygame.draw.rect(screen, BLACK, give_up_rect)
    draw_text("Give Up", font, WHITE, screen, 30, 25)

# Function to display game over popup
def display_game_over_popup():
    popup_font = pygame.font.Font(None, 48)
    popup_text = popup_font.render("You Died!", True, WHITE)
    popup_rect = popup_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    pygame.draw.rect(screen, BLACK, (popup_rect.x - 10, popup_rect.y - 10, popup_rect.width + 20, popup_rect.height + 20))
    screen.blit(popup_text, popup_rect)

# Function to check if the given position is inside the give up button area
def is_inside_give_up_button(pos):
    return 20 < pos[0] < 200 and 20 < pos[1] < 50

# Game loop
running = True
while running:
    screen.fill(BLACK)
    screen.blit(background_img, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    screen.blit(crosshair_img, (mouse_pos[0] - crosshair_img.get_width() // 2, mouse_pos[1] - crosshair_img.get_height() // 2))

    # Check events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.mixer.quit()  # Stop the mixer before exiting
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button clicked
                mouse_pos = pygame.mouse.get_pos()
                if is_inside_give_up_button(mouse_pos):
                    # Give Up button clicked
                    game_over_sound.play()
                    display_game_over_popup()
                    pygame.display.flip()
                    pygame.time.delay(2000)  # Display the popup for 2 seconds
                    running = False  # End the game after game over sound is played
                else:
                    hit = False
                    for duck in duck_list:
                        duck_rect = duck_img.get_rect(topleft=(duck['x'], duck['y']))
                        if duck_rect.collidepoint(mouse_pos):
                            duck_list.remove(duck)
                            score += 1
                            hit_sound.play()  # Play hit sound
                            hit = True
                            if score % 100 == 0:
                                killing_spree = True
                                killing_spree_sound.play()  # Play killing spree sound
                            break  # Exit the loop once a duck is hit
                    if not hit:  # If no duck was hit
                        miss_sound.play()  # Play miss sound
                        if score == 0:  # If score is zero after a miss
                            game_over_sound.play()  # Play game over sound
                            display_game_over_popup()  # Display game over popup
                            pygame.display.flip()
                            pygame.time.delay(2000)  # Display the popup for 2 seconds
                            running = False  # End the game after game over sound is played
                        else:
                            score = 0  # Set score back to zero
                            duck_speed = 5  # Reset duck speed to default value



    # Draw menu
    draw_menu()

    # Increase spawn rate based on score
    if score > 0 and score % 10 == 0:
        spawn_delay -= 1

    # Limit duck speed based on score
    duck_speed = min(score // 5 + 5, max_duck_speed)

    # Spawn ducks
    if len(duck_list) < 5:
        if random.randint(0, max(1, spawn_delay)) == 0:
            duck_list.append(create_duck())

    # Move ducks
    for duck in duck_list:
        duck['x'] += duck['speed']
        duck['y'] += random.randint(-3, 3)  # Move ducks up and down randomly
        screen.blit(duck_img, (duck['x'], duck['y']))

        # Slow down duck if it crosses the screen
        if duck['x'] > WIDTH:
            duck['speed'] *= 0.9  # Slow down by 10%
            duck['x'] = -duck_img.get_width()  # Reset duck position
            duck['y'] = random.randint(0, HEIGHT - duck_img.get_height())  # Randomize duck y position

    # Remove ducks that are out of bounds
    duck_list = [duck for duck in duck_list if duck['x'] < WIDTH]

    # Display score in a black box with white lettering
    draw_text(f"Score: {score}", font, WHITE, screen, WIDTH - 150, 10)

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()
