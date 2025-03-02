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
title_font = pygame.font.Font(None, 64)

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
game_state = MENU

# Add fly boundaries
FLY_BOUNDARY_BOTTOM = 3 * screen_height // 4  # Flies can't go below this y-coordinate
FLY_BOUNDARY_TOP = screen_height // 6 + 30  # Updated: Increased to keep flies away from top boxes

# Load and scale the background image
background_image = pygame.image.load('graphics/background.png').convert()
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

# Initialize the age of the pet
pet_age = 0
last_age_update = pygame.time.get_ticks()

# Initialize the hunger level of the pet
pet_hunger = 100  # Hunger level starts at 100 (full)
last_hunger_update = pygame.time.get_ticks()

# Load animation frames
teenage_frames = [
    pygame.image.load('graphics/midkomodowalking/komodoWalking1.png').convert_alpha(),
    pygame.image.load('graphics/midkomodowalking/komodoWalking2.png').convert_alpha(),
    pygame.image.load('graphics/midkomodowalking/komodoWalking3.png').convert_alpha(),
    pygame.image.load('graphics/midkomodowalking/komodoWalking4.png').convert_alpha()
]

# Load animation frames for baby Komodo
baby_komodo_frames = [
    pygame.image.load('graphics/Baby/babyKomodo1.png').convert_alpha(),
    pygame.image.load('graphics/Baby/babyKomodo2.png').convert_alpha(),
    pygame.image.load('graphics/Baby/babyKomodo3.png').convert_alpha(),
    pygame.image.load('graphics/Baby/babyKomodo4.png').convert_alpha()
]


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
    fly_frames = extract_frames(sprite_sheet, 32, 32, 4)  # Assuming each frame is 64x64 pixels and there are 4 frames
    # Scale fly frames to make them smaller
    fly_frames = [pygame.transform.scale(frame, (64, 64)) for frame in fly_frames]
except ValueError as e:
    print(f"Error extracting frames: {e}")
    # Create placeholder fly frames if extraction fails
    fly_frames = []
    for _ in range(4):
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(surf, (0, 0, 0), (16, 16), 8)
        fly_frames.append(surf)

# Load animation frames for old komodo
old_komodo_frames = [
    pygame.image.load('graphics/oldkomodo/oldKomodo1.png').convert_alpha(),
    pygame.image.load('graphics/oldkomodo/oldKomodo2.png').convert_alpha(),
    pygame.image.load('graphics/oldkomodo/oldKomodo3.png').convert_alpha(),
    pygame.image.load('graphics/oldkomodo/oldKomodo4.png').convert_alpha(),
    pygame.image.load('graphics/oldkomodo/oldKomodo5.png').convert_alpha(),
    pygame.image.load('graphics/oldkomodo/oldKomodo6.png').convert_alpha()
]

# Load animation frames for komodo eating
komodo_eating_frames = [
    pygame.image.load('graphics/midkomodoeating/komodoEating1.png').convert_alpha(),
    pygame.image.load('graphics/midkomodoeating/komodoEating2.png').convert_alpha(),
    pygame.image.load('graphics/midkomodoeating/komodoEating3.png').convert_alpha(),
    pygame.image.load('graphics/midkomodoeating/komodoEating4.png').convert_alpha(),
    pygame.image.load('graphics/midkomodoeating/komodoEating5.png').convert_alpha(),
    pygame.image.load('graphics/midkomodoeating/komodoEating6.png').convert_alpha(),
    pygame.image.load('graphics/midkomodoeating/komodoEating7.png').convert_alpha(),
    pygame.image.load('graphics/midkomodoeating/komodoEating8.png').convert_alpha()
]

# Load animation frames for baby komodo eating
baby_komodo_eating_frames = [
    pygame.image.load('graphics/baby/babyKomodoEating1.png').convert_alpha(),
    pygame.image.load('graphics/baby/babyKomodoEating2.png').convert_alpha(),
    pygame.image.load('graphics/baby/babyKomodoEating3.png').convert_alpha(),
    pygame.image.load('graphics/baby/babyKomodoEating4.png').convert_alpha()
]

# Load animation frames for old komodo eating
old_komodo_eating_frames = [
    pygame.image.load('graphics/oldKomodoEating1.png').convert_alpha(),
    pygame.image.load('graphics/oldKomodoEating2.png').convert_alpha()
]

<<<<<<< Updated upstream
=======
# Load animation frames for egg cracking
egg_frames = [
    pygame.image.load('graphics/egg/komodoEgg1.png').convert_alpha(),
    pygame.image.load('graphics/egg/komodoEgg2.png').convert_alpha(),
    pygame.image.load('graphics/egg/komodoEgg3.png').convert_alpha()
]

>>>>>>> Stashed changes
# Scale frames to the desired size
pet_frames = [pygame.transform.scale(frame, (250, 250)) for frame in teenage_frames]
baby_komodo_frames = [pygame.transform.scale(frame, (250, 250)) for frame in baby_komodo_frames]
old_komodo_frames = [pygame.transform.scale(frame, (250, 250)) for frame in old_komodo_frames]
komodo_eating_frames = [pygame.transform.scale(frame, (250, 250)) for frame in komodo_eating_frames]
baby_komodo_eating_frames = [pygame.transform.scale(frame, (250, 250)) for frame in baby_komodo_eating_frames]
old_komodo_eating_frames = [pygame.transform.scale(frame, (250, 250)) for frame in old_komodo_eating_frames]

# Create an animated sprite
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, frames, x, y):
        super().__init__()
        self.frames = frames
        self.eating_frames = komodo_eating_frames  # Add eating frames
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
        self.animation_speed = 0.1  # Adjust the speed of the animation
        self.last_update = pygame.time.get_ticks()
        self.is_eating = False
        self.eating_timer = 0
        self.eating_duration = 500

    def update(self):
        now = pygame.time.get_ticks()
        # If eating animation is active
        if self.is_eating:
            if now - self.last_update > 100:  # Faster animation for eating
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.eating_frames)
                self.image = self.eating_frames[self.current_frame]
                # Debug: Print current eating frame
                print(f"Eating frame: {self.current_frame}")
            
            # Check if eating animation should end
            if now - self.eating_timer > self.eating_duration:
                print("Eating animation finished")
                self.is_eating = False
                self.current_frame = 0
        else:
            # Regular animation
            if now - self.last_update > 100:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]

    def start_eating(self):
        print("Starting eating animation")  # Debug print
        self.is_eating = True
        self.eating_timer = pygame.time.get_ticks()
        self.current_frame = 0
        # Ensure we immediately show the first eating frame
        self.image = self.eating_frames[0]

# Function to calculate fly speed based on pet's age
def get_fly_speed(age):
    if age < 10:
        return 3  # Reduced speed for baby
    elif age < 20:
        return 4.5  # Reduced speed for teenager
    else:
        return 6  # Reduced speed for adult

# Function to calculate the maximum number of flies based on pet's age
def get_max_flies(age):
    if age < 10:
        return 3  # Maximum 3 flies for baby
    elif age < 20:
        return 2  # Maximum 2 flies for teenager
    else:
        return 1  # Maximum 1 fly for adult

# Create a fly sprite that moves around
class FlySprite(AnimatedSprite):
    def __init__(self, frames, x, y):
        super().__init__(frames, x, y)
        self.speed = get_fly_speed(pet_age)  # Set initial speed based on pet's age
        self.direction = random.uniform(0, 2 * math.pi)  # Random direction in radians
        self.direction_change_time = pygame.time.get_ticks()
        self.being_dragged = False
        self.original_rect = self.rect.copy()

    def update(self):
        super().update()
        
        # Update speed based on pet's age
        self.speed = get_fly_speed(pet_age)
        
        # Only move if not being dragged
        if not self.being_dragged:
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

            # Bounce off edges of screen and boundaries
            if self.rect.left < 0:
                self.rect.left = 0
                self.direction = random.uniform(-math.pi/2, math.pi/2)
            if self.rect.right > screen_width:
                self.rect.right = screen_width
                self.direction = random.uniform(math.pi/2, 3*math.pi/2)
            if self.rect.top < FLY_BOUNDARY_TOP:
                self.rect.top = FLY_BOUNDARY_TOP
                self.direction = random.uniform(0, math.pi)  # Force direction downward
            if self.rect.bottom > FLY_BOUNDARY_BOTTOM:
                self.rect.bottom = FLY_BOUNDARY_BOTTOM
                self.direction = random.uniform(math.pi, 2*math.pi)  # Force direction upward

    def start_drag(self):
        self.being_dragged = True
        self.original_rect = self.rect.copy()
    
    def update_drag_position(self, pos):
        if self.being_dragged:
            self.rect.center = pos
    
    def stop_drag(self):
        self.being_dragged = False

# Create button class for Menu and Game Over screens
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

# Create buttons for Menu screen
play_button = Button(screen_width//2 - 100, screen_height//2, 200, 50, "Play", (0, 150, 0), (0, 200, 0))
quit_button = Button(screen_width//2 - 100, screen_height//2 + 70, 200, 50, "Quit", (150, 0, 0), (200, 0, 0))

# Create buttons for Game Over screen
retry_button = Button(screen_width//2 - 100, screen_height//2, 200, 50, "Retry", (0, 150, 0), (0, 200, 0))
exit_button = Button(screen_width//2 - 100, screen_height//2 + 70, 200, 50, "Exit", (150, 0, 0), (200, 0, 0))

# Create an instance of the animated sprite with explicitly assigned eating frames
teenage_sprite = AnimatedSprite(pet_frames, screen_width // 2, screen_height // 2 + 100)
teenage_sprite.eating_frames = komodo_eating_frames

baby_komodo_sprite = AnimatedSprite(baby_komodo_frames, screen_width // 2, screen_height // 2 + 100)
baby_komodo_sprite.eating_frames = baby_komodo_eating_frames  # Changed to use baby-specific eating frames

old_komodo_sprite = AnimatedSprite(old_komodo_frames, screen_width // 2, screen_height // 2 + 100)
old_komodo_sprite.eating_frames = old_komodo_eating_frames  # Changed to use old-specific eating frames

# Create fly sprites
fly_sprites = pygame.sprite.Group()

def create_fly():
    max_flies = get_max_flies(pet_age)
    if len(fly_sprites) < max_flies:  # Ensure there are only up to the maximum number of flies
        fly = FlySprite(fly_frames, 
                        random.randint(50, screen_width - 50), 
                        random.randint(FLY_BOUNDARY_TOP + 20, FLY_BOUNDARY_BOTTOM - 20))
        fly_sprites.add(fly)

# No menu flies as per requirement
menu_flies = pygame.sprite.Group()

all_sprites = pygame.sprite.Group()

# Define box sizes and colors for the top boxes
box_size = 50
box_colors = ['Red', 'Blue', 'Green', 'Purple']  # Colors for food, water, play, sleep
box_rects = []

# Calculate positions to place boxes evenly across the screen
box_spacing = screen_width // 5
box_y = screen_height // 8 - box_size // 2  # Position closer to the top

# Function to reset the game
def reset_game():
    global pet_age, pet_hunger, game_state, last_age_update, last_hunger_update
    pet_age = 0
    pet_hunger = 100
    game_state = PLAYING
    last_age_update = pygame.time.get_ticks()
    last_hunger_update = pygame.time.get_ticks()
    
    # Clear and create flies based on the initial maximum number of flies
    fly_sprites.empty()
    max_flies = get_max_flies(pet_age)
    for _ in range(max_flies):
        create_fly()

# Create a surface for the pet and scale it to a larger size
petEgg_surface = pygame.image.load('graphics/komodoEgg.png').convert_alpha()
petEgg_surface = pygame.transform.scale(petEgg_surface, (250, 250))  # Scale to 250x250 pixels

# Variables for drag and drop functionality
dragging_fly = None

# Function to calculate hunger interval based on age
def get_hunger_interval(age):
    if age < 10:
        return 1000  # 1 second for baby
    elif age < 20:
        return 1000  # 1 second for teenager
    else:
        return 1000  # 1 second for adult

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            if game_state == MENU:
                # Check menu buttons
                if play_button.rect.collidepoint(mouse_pos):
                    game_state = PLAYING
                    reset_game()
                elif quit_button.rect.collidepoint(mouse_pos):
                    pygame.quit()
                    exit()
            
            elif game_state == GAME_OVER:
                # Check game over buttons
                if retry_button.rect.collidepoint(mouse_pos):
                    reset_game()
                elif exit_button.rect.collidepoint(mouse_pos):
                    pygame.quit()
                    exit()
            
            elif game_state == PLAYING:
                # Check if a fly is clicked
                for fly in fly_sprites:
                    if fly.rect.collidepoint(mouse_pos):
                        dragging_fly = fly
                        fly.start_drag()
                        break
                
                # If not dragging a fly, check if control buttons are clicked
                if not dragging_fly:
                    # Left arrow button
                    left_arrow_rect = pygame.Rect(screen_width // 4 - 20, 7 * screen_height // 8 - 15, 40, 30)
                    if left_arrow_rect.collidepoint(mouse_pos):
                        print("Left arrow clicked")
                    
                    # Circle button
                    circle_center = (screen_width // 2, 7 * screen_height // 8)
                    if math.sqrt((mouse_pos[0] - circle_center[0])**2 + (mouse_pos[1] - circle_center[1])**2) < 20:
                        print("Circle button clicked")
                    
                    # Right arrow button
                    right_arrow_rect = pygame.Rect(3 * screen_width // 4 - 20, 7 * screen_height // 8 - 15, 40, 30)
                    if right_arrow_rect.collidepoint(mouse_pos):
                        print("Right arrow clicked")
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging_fly:
                # Check if the fly is dropped over the lizard
                current_lizard = None
                if pet_age < 1:
                    # Can't feed the egg
                    lizard_rect = petEgg_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 100))
                    if lizard_rect.collidepoint(mouse_pos):
                        print("Fed the egg!")
                        pet_hunger = min(pet_hunger + 20, 100)
                        dragging_fly.kill()
                        # Only create a new fly if there are fewer than max allowed flies
                        max_flies = get_max_flies(pet_age)
                        if len(fly_sprites) < max_flies:
                            create_fly()
                        dragging_fly = None
                else:
                    # Check which lizard sprite to use based on age
                    if pet_age < 10:
                        current_lizard = baby_komodo_sprite
                        print("Baby komodo will eat")
                    elif pet_age < 20:
                        current_lizard = teenage_sprite
                        print("Teenage komodo will eat")
                    else:
                        current_lizard = old_komodo_sprite
                        print("Old komodo will eat")
                    
                    if current_lizard and current_lizard.rect.collidepoint(mouse_pos):
                        print(f"Fed the lizard! (Age: {pet_age})")
                        # Explicitly trigger eating animation with debug
                        current_lizard.start_eating()
                        pet_hunger = min(pet_hunger + 20, 100)
                        dragging_fly.kill()
                        # Create a new fly to replace the eaten one if not exceeding max
                        max_flies = get_max_flies(pet_age)
                        if len(fly_sprites) < max_flies:
                            create_fly()
                        dragging_fly = None
                
                # If not dropped on lizard, return fly to original position
                if dragging_fly:
                    dragging_fly.stop_drag()
                    dragging_fly = None
        
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            
            # Update button hover states
            if game_state == MENU:
                play_button.is_hovered(mouse_pos)
                quit_button.is_hovered(mouse_pos)
            elif game_state == GAME_OVER:
                retry_button.is_hovered(mouse_pos)
                exit_button.is_hovered(mouse_pos)
            
            # Update dragged fly position
            if dragging_fly:
                dragging_fly.update_drag_position(mouse_pos)
    
    # Clear the screen
    screen.fill((0, 0, 0))
    
    # Draw background
    screen.blit(background_image, (0, 0))
    
    # Menu state
    if game_state == MENU:
        # NO menu flies as per requirement
        
        # Draw a semi-transparent overlay to make text more readable
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        # Draw title
        smaller_title_font = pygame.font.Font(None, 48)  # Smaller than the original 64
        title_text = smaller_title_font.render("Reptile Pet Simulator", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 4))
        screen.blit(title_text, title_rect)
        
        # Draw pet egg for decoration
        menu_pet = pygame.transform.scale(petEgg_surface, (150, 150))
        screen.blit(menu_pet, menu_pet.get_rect(center=(screen_width // 2, screen_height // 3 + 50)))
        
        # Add game description
        desc_text = test_font.render("Take care of your reptile pet and watch it grow!", True, (255, 255, 255))
        desc_rect = desc_text.get_rect(center=(screen_width // 2, screen_height // 2 - 105))
        screen.blit(desc_text, desc_rect)
        
        # Draw buttons
        play_button.draw(screen)
        quit_button.draw(screen)
    
    # Playing state
    elif game_state == PLAYING:
        # Update the age of the pet every 3 seconds (3000 milliseconds)
        now = pygame.time.get_ticks()
        if now - last_age_update >= 3000:
            pet_age += 1
            last_age_update = now
            print(f"Pet age: {pet_age} years")
        
        # Update the hunger level
        hunger_interval = get_hunger_interval(pet_age)
        if now - last_hunger_update >= hunger_interval:
            pet_hunger = max(0, pet_hunger - 10)
            last_hunger_update = now
            print(f"Pet hunger: {pet_hunger}%")
            
            # Check if pet has starved
            if pet_hunger <= 0:
                game_state = GAME_OVER
        
        # Render the age and hunger text
        age_text = test_font.render(f"Pet age: {pet_age} years", True, (255, 255, 255))
        hunger_text = test_font.render(f"Pet hunger: {pet_hunger}%", True, (255, 255, 255))
        screen.blit(age_text, (10, 10))
        screen.blit(hunger_text, (10, 40))
        
        # Place four boxes evenly across the screen
        box_rects = []
        for i in range(4):
            x_position = box_spacing * (i + 1) - box_size // 2
            box_rect = pygame.Rect(x_position, box_y, box_size, box_size)
            box_rects.append(box_rect)
            pygame.draw.rect(screen, box_colors[i], box_rect)
            pygame.draw.rect(screen, 'White', box_rect, 2)  # White border for visibility
        
        # Display the appropriate pet sprite based on age
        all_sprites.empty()
        
        if pet_age < 1:
            screen.blit(petEgg_surface, petEgg_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 100)))
        elif pet_age < 10:
            all_sprites.add(baby_komodo_sprite)
        elif pet_age < 20:
            all_sprites.add(teenage_sprite)
        else:
            all_sprites.add(old_komodo_sprite)
        
        # Debug: Show which sprite is active and if it's eating
        active_sprite = None
        if pet_age < 1:
            print("Showing egg")
        elif pet_age < 10:
            active_sprite = baby_komodo_sprite
        elif pet_age < 20:
            active_sprite = teenage_sprite
        else:
            active_sprite = old_komodo_sprite
            
        if active_sprite:
            if active_sprite.is_eating:
                print(f"Active sprite is eating, frame: {active_sprite.current_frame}")
        
        # Update and draw all sprites - make sure this is called for animation to work
        all_sprites.update()
        all_sprites.draw(screen)
        
        # Update and draw flies
        fly_sprites.update()
        fly_sprites.draw(screen)
        
        # Optionally draw boundaries for debugging
        # pygame.draw.line(screen, (255, 0, 0), (0, FLY_BOUNDARY_TOP), (screen_width, FLY_BOUNDARY_TOP), 1)
        # pygame.draw.line(screen, (255, 0, 0), (0, FLY_BOUNDARY_BOTTOM), (screen_width, FLY_BOUNDARY_BOTTOM), 1)
        pygame.draw.polygon(screen, 'White', [
            (screen_width // 4 - 20, 7 * screen_height // 8),  # Left point
            (screen_width // 4 + 10, 7 * screen_height // 8 - 15),  # Top-right
            (screen_width // 4 + 10, 7 * screen_height // 8 + 15)   # Bottom-right
        ])

        # Middle circle
        pygame.draw.circle(screen, 'White', (screen_width // 2, 7 * screen_height // 8), 20)

        # Right arrow (pointing right)
        pygame.draw.polygon(screen, 'White', [
            (3 * screen_width // 4 + 20, 7 * screen_height // 8),  # Right point
            (3 * screen_width // 4 - 10, 7 * screen_height // 8 - 15),  # Top-left
            (3 * screen_width // 4 - 10, 7 * screen_height // 8 + 15)   # Bottom-left
        ])
    
    # Game over state
    elif game_state == GAME_OVER:
        # Display game over message
        game_over_text = large_font.render("Game Over", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(screen_width // 2, screen_height // 4))
        screen.blit(game_over_text, game_over_rect)
        
        # Display final stats
        final_age_text = test_font.render(f"Your pet lived to {pet_age} years old", True, (255, 255, 255))
        final_age_rect = final_age_text.get_rect(center=(screen_width // 2, screen_height // 3))
        screen.blit(final_age_text, final_age_rect)
        
        # Draw buttons
        retry_button.draw(screen)
        exit_button.draw(screen)
    
    # Update the display
    pygame.display.flip()
    clock.tick(60)  # Limit the frame rate to 60 FPS