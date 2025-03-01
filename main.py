import pygame
from sys import exit
import random
import math

# Initialize Pygame
pygame.init()

# Set up the display
screen_width = 400
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Reptile Pet Simulator")
clock = pygame.time.Clock()
test_font = pygame.font.Font(None, 24)
large_font = pygame.font.Font(None, 48)

# Game states
PLAYING = 0
GAME_OVER = 1
game_state = PLAYING

# Load and scale the background image
background_image = pygame.image.load('graphics/background.png').convert()
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

# Initialize the age of the pet
pet_age = 0
last_age_update = pygame.time.get_ticks()

# Load animation frames
teenage_frames = [
    pygame.image.load('graphics/komodoWalking1.png').convert_alpha(),
    pygame.image.load('graphics/komodoWalking2.png').convert_alpha(),
    pygame.image.load('graphics/komodoWalking3.png').convert_alpha(),
    pygame.image.load('graphics/komodoWalking4.png').convert_alpha()
]

# Load animation frames for baby Komodo
baby_komodo_frames = [
    pygame.image.load('graphics/babyKomodo1.png').convert_alpha(),
    pygame.image.load('graphics/babyKomodo2.png').convert_alpha(),
    pygame.image.load('graphics/babyKomodo3.png').convert_alpha(),
    pygame.image.load('graphics/babyKomodo4.png').convert_alpha()
]

# Scale frames to the desired size
pet_frames = [pygame.transform.scale(frame, (250, 250)) for frame in teenage_frames]
baby_komodo_frames = [pygame.transform.scale(frame, (250, 250)) for frame in baby_komodo_frames]

# Load the sprite sheet
sprite_sheet = pygame.image.load('graphics/fly.png').convert_alpha()

# Function to extract frames from the sprite sheet
def extract_frames(sheet, frame_width, frame_height, num_frames):
    sheet_width, sheet_height = sheet.get_size()
    print(f"Sprite sheet dimensions: {sheet_width}x{sheet_height}")
    frames = []
    for i in range(num_frames):
        rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
        if rect.x + rect.width <= sheet_width and rect.y + rect.height <= sheet_height:
            frame = sheet.subsurface(rect)
            frames.append(frame)
        else:
            raise ValueError(f"subsurface rectangle outside surface area. i={i}, rect={rect}, sheet_width={sheet_width}, sheet_height={sheet_height}")
    return frames

# Extract frames from the sprite sheet
try:
    fly_frames = extract_frames(sprite_sheet, 64, 64, 4)  # Assuming each frame is 64x64 pixels and there are 4 frames
    # Scale fly frames to make them smaller
    fly_frames = [pygame.transform.scale(frame, (32, 32)) for frame in fly_frames]
except ValueError as e:
    print(f"Error extracting frames: {e}")
    # Create placeholder fly frames if extraction fails
    fly_frames = []
    for _ in range(4):
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(surf, (0, 0, 0), (16, 16), 8)
        fly_frames.append(surf)

# Create an animated sprite
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, frames, x, y):
        super().__init__()
        self.frames = frames
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
        self.animation_speed = 0.1  # Adjust the speed of the animation
        self.last_update = pygame.time.get_ticks()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 100:  # Adjust the frame rate of the animation
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

# Create a fly sprite that moves around
class FlySprite(AnimatedSprite):
    def __init__(self, frames, x, y):
        super().__init__(frames, x, y)
        self.speed = 2
        self.direction = random.uniform(0, 2 * math.pi)  # Random direction in radians
        self.direction_change_time = pygame.time.get_ticks()
        
    def update(self):
        super().update()
        
        # Change direction randomly
        now = pygame.time.get_ticks()
        if now - self.direction_change_time > 500:  # Change direction every 0.5 seconds
            self.direction += random.uniform(-math.pi/4, math.pi/4)  # Add small random change
            self.direction_change_time = now
            
        # Move in current direction
        dx = self.speed * math.cos(self.direction)
        dy = self.speed * math.sin(self.direction)
        self.rect.x += dx
        self.rect.y += dy
        
        # Bounce off edges of screen
        if self.rect.left < 0:
            self.rect.left = 0
            self.direction = random.uniform(-math.pi/2, math.pi/2)
        if self.rect.right > screen_width:
            self.rect.right = screen_width
            self.direction = random.uniform(math.pi/2, 3*math.pi/2)
        if self.rect.top < 0:
            self.rect.top = 0
            self.direction = random.uniform(0, math.pi)
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            self.direction = random.uniform(math.pi, 2*math.pi)

# Create button class for Game Over screen
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.font = pygame.font.Font(None, 36)
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=12)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def is_hovered(self, pos):
        if self.rect.collidepoint(pos):
            self.current_color = self.hover_color
            return True
        self.current_color = self.color
        return False

# Create buttons for Game Over screen
retry_button = Button(screen_width//2 - 100, screen_height//2, 200, 50, "Retry", (0, 150, 0), (0, 200, 0))
exit_button = Button(screen_width//2 - 100, screen_height//2 + 70, 200, 50, "Exit", (150, 0, 0), (200, 0, 0))

# Function to reset the game
def reset_game():
    global pet_age, game_state, last_age_update
    pet_age = 0
    game_state = PLAYING
    last_age_update = pygame.time.get_ticks()
    all_sprites.empty()
    if fly_sprite:
        all_sprites.add(fly_sprite)

# Create an instance of the animated sprite
teenage_sprite = AnimatedSprite(pet_frames, screen_width // 2, screen_height // 2 + 100)
baby_komodo_sprite = AnimatedSprite(baby_komodo_frames, screen_width // 2, screen_height // 2 + 100)
fly_sprite = FlySprite(fly_frames, screen_width // 2, screen_height // 3)
all_sprites = pygame.sprite.Group()
all_sprites.add(fly_sprite)

# Need to import sprites for the food, water, play, and sleep features

# Create a surface for the food
food_surface = pygame.Surface((50, 50)) # Can add sprite later
food_surface.fill('Red')  # Fill the surface with red

# Create a surface for the Water
water_surface = pygame.Surface((50, 50)) # Can add sprite later
water_surface.fill('Blue')  # Fill the surface with blue

# Create a surface for the play feature
play_surface = pygame.Surface((50, 50)) # Can add sprite later
play_surface.fill('Green')  # Fill the surface with green

# Create a surface for the sleep feature
sleep_surface = pygame.Surface((50, 50)) # Can add sprite later
sleep_surface.fill('Purple')  # Fill the surface with purple

# Create a surface for the pet and scale it to a larger size
petEgg_surface = pygame.image.load('graphics/komodoEgg.png').convert_alpha()
petEgg_surface = pygame.transform.scale(petEgg_surface, (250, 250))  # Scale to 250x250 pixels

# Create surface for the left button
left_button_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
pygame.draw.polygon(left_button_surface, 'Red', [(25, 0), (0, 50), (50, 50)])
left_button_surface.fill('Red')

# Create surface for the right button
right_button_surface = pygame.Surface((50, 50))
right_button_surface.fill('Red')

# Create a surface for the middle button
middle_button_surface = pygame.Surface((50, 50))
middle_button_surface.fill('Red')

# Calculate positions to place surfaces evenly across the screen
surfaces = [food_surface, water_surface, play_surface, sleep_surface]
num_surfaces = len(surfaces)
spacing = screen_width // (num_surfaces + 1)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            if game_state == GAME_OVER:
                # Check if retry button is clicked
                if retry_button.rect.collidepoint(mouse_pos):
                    reset_game()
                # Check if exit button is clicked
                elif exit_button.rect.collidepoint(mouse_pos):
                    pygame.quit()
                    exit()
            else:
                # Game is playing, check normal buttons
                # Check if the left button is clicked
                left_button_points = [(screen_width // 4 - 25, 7 * screen_height // 8 + 25), 
                                    (screen_width // 4 + 25, 7 * screen_height // 8 + 25), 
                                    (screen_width // 4, 7 * screen_height // 8 - 25)]
                left_button_rect = pygame.draw.polygon(screen, 'White', left_button_points)
                if left_button_rect.collidepoint(mouse_pos):
                    print("Left button clicked")
                # Check if the right button is clicked
                right_button_points = [(3 * screen_width // 4 - 25, 7 * screen_height // 8 + 25), 
                                    (3 * screen_width // 4 + 25, 7 * screen_height // 8 + 25), 
                                    (3 * screen_width // 4, 7 * screen_height // 8 - 25)]
                right_button_rect = pygame.draw.polygon(screen, 'White', right_button_points)
                if right_button_rect.collidepoint(mouse_pos):
                    print("Right button clicked")

                # Check if the middle button is clicked
                middle_button_points = [(screen_width // 2 - 25, 7 * screen_height // 8 + 25), 
                                        (screen_width // 2 + 25, 7 * screen_height // 8 + 25), 
                                        (screen_width // 2, 7 * screen_height // 8 - 25)]
                middle_button_rect = pygame.draw.polygon(screen, 'White', middle_button_points)
                if middle_button_rect.collidepoint(mouse_pos):
                    print("Middle button clicked")
        
        # Track mouse for button hover effects
        elif event.type == pygame.MOUSEMOTION and game_state == GAME_OVER:
            mouse_pos = event.pos
            retry_button.is_hovered(mouse_pos)
            exit_button.is_hovered(mouse_pos)

    screen.fill((0, 0, 0))  # Clear the screen with a black color

    # Blit the background image
    screen.blit(background_image, (0, 0))

    if game_state == PLAYING:
        # Place four surfaces evenly across the screen for the food, water, play, and sleep features
        for i, surface in enumerate(surfaces):
            x_position = spacing * (i + 1) - surface.get_width() // 2
            y_position = screen_height // 8 - surface.get_height() // 2  # Position closer to the top
            screen.blit(surface, (x_position, y_position))

        # Update the age of the pet every 1 minute (60000 milliseconds)
        now = pygame.time.get_ticks()
        if now - last_age_update >= 1000:  # Change back to 60000
            pet_age += 1
            last_age_update = now
            print(f"Pet age: {pet_age} years")
            
            # Check if pet has reached end of life
            if pet_age >= 30:
                game_state = GAME_OVER

        # Render the age text
        age_text = test_font.render(f"Pet age: {pet_age} years", True, (255, 255, 255))
        screen.blit(age_text, (10, 10))  # Position the text at the top-left corner

        # FIXME: make if-else statement backwards
        # Display the egg image if the pet's age is less than 1
        all_sprites.empty()  # Clear reptile sprites
        all_sprites.add(fly_sprite)  # Always keep fly sprite

        if pet_age < 1:
            screen.blit(petEgg_surface, (screen_width // 2 - petEgg_surface.get_width() // 2, 
                                        screen_height // 2 - petEgg_surface.get_height() // 2))
        elif pet_age >= 1 and pet_age < 10:
            all_sprites.add(baby_komodo_sprite)
        elif pet_age >= 10 and pet_age < 30:
            all_sprites.add(teenage_sprite)
        
        # Update and draw all sprites
        all_sprites.update()
        all_sprites.draw(screen)
        
        # Place the buttons at the bottom of the screen
        left_button_x = screen_width // 4 - left_button_surface.get_width() // 2
        right_button_x = 3 * screen_width // 4 - right_button_surface.get_width() // 2
        button_y = 7 * screen_height // 8 - left_button_surface.get_height() // 2
        middle_button_x = screen_width // 2 - middle_button_surface.get_width() // 2
        middle_button_y = 7 * screen_height // 8 - middle_button_surface.get_height() // 2

        screen.blit(left_button_surface, (left_button_x, button_y))
        screen.blit(right_button_surface, (right_button_x, button_y))
        screen.blit(middle_button_surface, (middle_button_x, middle_button_y))
        
    else:  # GAME_OVER state
        # Display game over message
        game_over_text = large_font.render("Your Pet Has Died", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 3))
        screen.blit(game_over_text, game_over_rect)
        
        # Display final age
        final_age_text = test_font.render(f"Your pet lived to {pet_age} years old", True, (255, 255, 255))
        final_age_rect = final_age_text.get_rect(center=(screen_width // 2, screen_height // 3 + 50))
        screen.blit(final_age_text, final_age_rect)
        
        # Draw retry and exit buttons
        retry_button.draw(screen)
        exit_button.draw(screen)

    # Update the display
    pygame.display.flip()
    clock.tick(60)  # Limit the frame rate to 60 FPS