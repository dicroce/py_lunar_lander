import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lunar Lander")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (150, 150, 150)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255)
DARK_GRAY = (50, 50, 50)

# Fonts
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# Level settings
LEVELS = [
    {"gravity": 0.03, "thrust": 0.15, "fuel": 1000, "pad_width": 150, "fuel_rate": 3, "wind": 0},
    {"gravity": 0.04, "thrust": 0.14, "fuel": 900, "pad_width": 130, "fuel_rate": 4, "wind": 0.01},
    {"gravity": 0.045, "thrust": 0.13, "fuel": 800, "pad_width": 110, "fuel_rate": 4, "wind": 0.02},
    {"gravity": 0.05, "thrust": 0.12, "fuel": 700, "pad_width": 90, "fuel_rate": 5, "wind": 0.03},
    {"gravity": 0.052, "thrust": 0.115, "fuel": 650, "pad_width": 80, "fuel_rate": 5, "wind": 0.035}
]

current_level = 0
lives = 5
game_over = False
death_screen = False

def generate_level_background(level):
    random.seed(level)
    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(100)]
    moon_x = random.randint(WIDTH // 2, WIDTH - 100)
    moon_y = random.randint(50, HEIGHT // 2)
    moon_radius = 50
    
    craters = []
    for _ in range(10):
        while True:
            crater_radius = random.randint(3, 15)
            # Generate random angle and distance from center
            angle = random.uniform(0, 2 * math.pi)
            # Ensure the crater is at least half its radius away from the edge
            max_distance = moon_radius - 1.5 * crater_radius
            distance = random.uniform(0, max_distance)
            
            crater_x = int(distance * math.cos(angle))
            crater_y = int(distance * math.sin(angle))
            
            # Check if the crater overlaps with existing craters
            if all((crater_x - c[0])**2 + (crater_y - c[1])**2 > (crater_radius + c[2])**2 for c in craters):
                craters.append((crater_x, crater_y, crater_radius))
                break
    
    return stars, moon_x, moon_y, craters

def draw_background(surface, level):
    stars, moon_x, moon_y, craters = generate_level_background(level)
    
    # Fill the background with black
    surface.fill(BLACK)
    
    # Draw stars
    for star in stars:
        pygame.draw.circle(surface, WHITE, star, 1)
    
    # Draw the moon
    pygame.draw.circle(surface, GRAY, (moon_x, moon_y), 50)
    
    # Add craters to the moon
    for crater in craters:
        crater_x = moon_x + crater[0]
        crater_y = moon_y + crater[1]
        crater_radius = crater[2]
        
        pygame.draw.circle(surface, DARK_GRAY, (crater_x, crater_y), crater_radius)
        
        # Add a highlight to give the crater some depth
        highlight_x = crater_x + 1
        highlight_y = crater_y + 1
        highlight_radius = max(1, crater_radius - 2)
        pygame.draw.circle(surface, GRAY, (highlight_x, highlight_y), highlight_radius)

def draw_lander(surface, x, y, thrusting):
    # Main body
    pygame.draw.rect(surface, WHITE, (x, y, 20, 30))
    
    # Left leg
    pygame.draw.rect(surface, WHITE, (x - 10, y + 30, 5, 10))
    pygame.draw.rect(surface, WHITE, (x - 15, y + 40, 10, 3))
    
    # Right leg
    pygame.draw.rect(surface, WHITE, (x + 25, y + 30, 5, 10))
    pygame.draw.rect(surface, WHITE, (x + 25, y + 40, 10, 3))
    
    # Cockpit
    pygame.draw.rect(surface, GRAY, (x + 5, y + 5, 10, 10))
    
    # Thruster
    if thrusting:
        pygame.draw.rect(surface, RED, (x + 5, y + 30, 10, 5))
        # Flame effect
        pygame.draw.polygon(surface, ORANGE, [(x + 5, y + 35), (x + 10, y + 45), (x + 15, y + 35)])

def draw_wind_indicator(surface, wind):
    arrow_x = WIDTH - 100
    arrow_y = 180
    arrow_length = abs(wind) * 1000  # Scale the arrow length based on wind strength
    max_length = 50  # Maximum arrow length
    min_length = 10  # Minimum arrow length
    arrow_length = max(min(arrow_length, max_length), min_length)
    
    if wind != 0:
        direction = 1 if wind > 0 else -1  # Positive wind goes right, negative goes left
        pygame.draw.line(surface, BLUE, (arrow_x, arrow_y), (arrow_x + arrow_length * direction, arrow_y), 3)
        pygame.draw.polygon(surface, BLUE, [
            (arrow_x + arrow_length * direction, arrow_y),
            (arrow_x + (arrow_length - 10) * direction, arrow_y - 5),
            (arrow_x + (arrow_length - 10) * direction, arrow_y + 5)
        ])
    else:
        # Draw a circle for no wind
        pygame.draw.circle(surface, BLUE, (arrow_x, arrow_y), 5)

    # Draw wind speed text
    wind_text = f"Wind: {abs(wind):.3f}"
    wind_surface = font.render(wind_text, True, BLUE)
    surface.blit(wind_surface, (WIDTH - 150, 200))

def reset_level():
    global lander_x, lander_y, lander_dx, lander_dy, fuel, pad_x, landed, death_screen
    random.seed(current_level)  # Set seed for consistent level generation
    lander_x = WIDTH // 2
    lander_y = 50
    lander_dx = 0
    lander_dy = 0
    fuel = LEVELS[current_level]["fuel"]
    pad_x = random.randint(0, WIDTH - LEVELS[current_level]["pad_width"])
    landed = False
    death_screen = False

def reset_game():
    global current_level, lives, game_over
    current_level = 0
    lives = 5
    game_over = False
    reset_level()

# Lander properties
lander_width, lander_height = 40, 43  # Adjusted for the new lander design

# Landing pad
pad_height = 10
pad_y = HEIGHT - pad_height

# Initialize game state
reset_game()

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    thrusting = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_over:
                    reset_game()
                elif landed:
                    current_level = min(current_level + 1, len(LEVELS) - 1)
                    reset_level()
                elif death_screen:
                    reset_level()
            elif event.key == pygame.K_q and game_over:
                running = False

    if not game_over and not landed and not death_screen:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and fuel > 0:
            lander_dx -= LEVELS[current_level]["thrust"]
            fuel -= LEVELS[current_level]["fuel_rate"]
        if keys[pygame.K_RIGHT] and fuel > 0:
            lander_dx += LEVELS[current_level]["thrust"]
            fuel -= LEVELS[current_level]["fuel_rate"]
        if keys[pygame.K_UP] and fuel > 0:
            lander_dy -= LEVELS[current_level]["thrust"]
            fuel -= LEVELS[current_level]["fuel_rate"]
            thrusting = True

        fuel = max(0, fuel)  # Ensure fuel doesn't go negative

        # Apply gravity and wind
        lander_dy += LEVELS[current_level]["gravity"]
        lander_dx += LEVELS[current_level]["wind"]

        # Update lander position
        lander_x += lander_dx
        lander_y += lander_dy

        # Wrap around screen edges
        lander_x = lander_x % WIDTH

        # Check for landing or crash
        if lander_y + lander_height >= pad_y:
            if pad_x < lander_x < pad_x + LEVELS[current_level]["pad_width"] - lander_width and lander_dy < 1.5:
                landed = True
            else:
                lives -= 1
                if lives > 0:
                    death_screen = True
                else:
                    game_over = True

    # Draw everything
    draw_background(screen, current_level)
    draw_lander(screen, lander_x, lander_y, thrusting)
    pygame.draw.rect(screen, GREEN, (pad_x, pad_y, LEVELS[current_level]["pad_width"], pad_height))
    draw_wind_indicator(screen, LEVELS[current_level]["wind"])

    # Display velocity
    velocity = math.sqrt(lander_dx**2 + lander_dy**2)
    velocity_text = f"Velocity: {velocity:.2f}"
    text = font.render(velocity_text, True, WHITE)
    screen.blit(text, (10, 10))

    # Display fuel
    fuel_percentage = (fuel / LEVELS[current_level]["fuel"]) * 100
    fuel_text = f"Fuel: {fuel_percentage:.1f}%"
    fuel_color = GREEN if fuel_percentage > 50 else YELLOW if fuel_percentage > 25 else RED
    fuel_surface = font.render(fuel_text, True, fuel_color)
    screen.blit(fuel_surface, (10, 50))

    # Display current level
    level_text = f"Level: {current_level + 1}"
    level_surface = font.render(level_text, True, WHITE)
    screen.blit(level_surface, (WIDTH - level_surface.get_width() - 10, 10))

    # Display lives
    lives_text = f"Lives: {lives}"
    lives_surface = font.render(lives_text, True, WHITE)
    screen.blit(lives_surface, (WIDTH - lives_surface.get_width() - 10, 50))

    if game_over:
        end_text = "GAME OVER"
        text_color = RED
        end_surface = large_font.render(end_text, True, text_color)
        screen.blit(end_surface, (WIDTH//2 - end_surface.get_width()//2, HEIGHT//2 - 50))
        
        play_again_text = "Press SPACE to Play Again or Q to Quit"
        play_again_surface = font.render(play_again_text, True, WHITE)
        screen.blit(play_again_surface, (WIDTH//2 - play_again_surface.get_width()//2, HEIGHT//2 + 50))
    elif death_screen:
        death_text = "You Died!"
        text_color = RED
        death_surface = large_font.render(death_text, True, text_color)
        screen.blit(death_surface, (WIDTH//2 - death_surface.get_width()//2, HEIGHT//2 - 50))
        
        continue_text = "Press SPACE to Continue"
        continue_surface = font.render(continue_text, True, WHITE)
        screen.blit(continue_surface, (WIDTH//2 - continue_surface.get_width()//2, HEIGHT//2 + 50))
    elif landed:
        if current_level < len(LEVELS) - 1:
            end_text = "Level Complete!"
            text_color = GREEN
            end_surface = large_font.render(end_text, True, text_color)
            screen.blit(end_surface, (WIDTH//2 - end_surface.get_width()//2, HEIGHT//2 - 50))
            
            continue_text = "Press SPACE to Continue"
            continue_surface = font.render(continue_text, True, WHITE)
            screen.blit(continue_surface, (WIDTH//2 - continue_surface.get_width()//2, HEIGHT//2 + 50))
        else:
            end_text = "You Win!"
            text_color = GREEN
            end_surface = large_font.render(end_text, True, text_color)
            screen.blit(end_surface, (WIDTH//2 - end_surface.get_width()//2, HEIGHT//2 - 50))
            
            play_again_text = "Press SPACE to Play Again or Q to Quit"
            play_again_surface = font.render(play_again_text, True, WHITE)
            screen.blit(play_again_surface, (WIDTH//2 - play_again_surface.get_width()//2, HEIGHT//2 + 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
