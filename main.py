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

# Add these variables after loading the background image
background_scroll = 0
background_scroll_speed = 1  # Pixels per frame - adjust for faster/slower scrolling

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

# Load animation frames for egg cracking - add verification
try:
    egg_frames = [
        pygame.image.load('graphics/egg/komodoEgg1.png').convert_alpha(),
        pygame.image.load('graphics/egg/komodoEgg2.png').convert_alpha(),
        pygame.image.load('graphics/egg/komodoEgg3.png').convert_alpha()
    ]
    print("Egg frames loaded successfully:")
    for i, frame in enumerate(egg_frames):
        print(f"Frame {i}: size={frame.get_size()}")
    
    # Scale frames to the desired size
    egg_frames = [pygame.transform.scale(frame, (250, 250)) for frame in egg_frames]
except Exception as e:
    print(f"Error loading egg frames: {e}")
    # Create placeholder egg frames if loading fails
    egg_frames = []
    base_egg = pygame.Surface((250, 250), pygame.SRCALPHA)
    pygame.draw.ellipse(base_egg, (255, 255, 200), (50, 50, 150, 200))  # Base egg shape
    
    egg_frames.append(base_egg.copy())  # Frame 1: intact egg
    
    crack_egg = base_egg.copy()
    pygame.draw.line(crack_egg, (0, 0, 0), (100, 100), (150, 150), 3)  # Frame 2: egg with crack
    egg_frames.append(crack_egg)
    
    hatching_egg = base_egg.copy()
    pygame.draw.polygon(hatching_egg, (0, 0, 0), [(80, 80), (120, 70), (160, 90), (170, 130)], 3)  # Frame 3: egg hatching
    egg_frames.append(hatching_egg)
    
    print("Created placeholder egg frames")

# Scale frames to the desired size
pet_frames = [pygame.transform.scale(frame, (250, 250)) for frame in teenage_frames]
baby_komodo_frames = [pygame.transform.scale(frame, (250, 250)) for frame in baby_komodo_frames]
old_komodo_frames = [pygame.transform.scale(frame, (250, 250)) for frame in old_komodo_frames]
komodo_eating_frames = [pygame.transform.scale(frame, (250, 250)) for frame in komodo_eating_frames]
baby_komodo_eating_frames = [pygame.transform.scale(frame, (250, 250)) for frame in baby_komodo_eating_frames]
old_komodo_eating_frames = [pygame.transform.scale(frame, (250, 250)) for frame in old_komodo_eating_frames]
egg_frames = [pygame.transform.scale(frame, (250, 250)) for frame in egg_frames]

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

# Create a specialized egg sprite that runs slowly and only once
class EggSprite(pygame.sprite.Sprite):
    def __init__(self, frames, x, y):
        super().__init__()
        # Verify we have frames
        if not frames:
            raise ValueError("No egg frames provided")
        
        self.frames = frames
        print(f"EggSprite initialized with {len(self.frames)} frames")
        
        # Set initial state
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
        self.animation_completed = False
        self.animation_started = False
        self.frame_delay = 1000  # Reduced from 2000 to 1000 ms - faster frame rate
        self.start_delay = 1500  # Reduced from 3000 to 1500 ms - starts sooner
        self.last_update = pygame.time.get_ticks()
        self.start_time = pygame.time.get_ticks()
        
        # Shake effect
        self.shake_amount = 0
        self.original_pos = (x, y)
        print(f"New egg sprite created at position {(x, y)}")
        self.just_hatched = False  # New flag to indicate when hatching just completed
    
    def update(self):
        now = pygame.time.get_ticks()
        
        # Reset the just_hatched flag at the start of each update
        self.just_hatched = False
        
        # Don't update if animation is completed
        if self.animation_completed:
            return
        
        # Wait for start delay before beginning animation
        if not self.animation_started:
            if now - self.start_time > self.start_delay:
                self.animation_started = True
                self.last_update = now
                self.shake_amount = 3
                print("Egg animation starting now!")
            return
        
        # Update frame if enough time has passed
        if now - self.last_update > self.frame_delay:
            self.current_frame += 1
            print(f"Advancing to egg frame {self.current_frame}")
            
            # Add shake effect when changing frames
            self.shake_amount = 5
            
            # Check if we've reached the end
            if self.current_frame >= len(self.frames):
                self.current_frame = len(self.frames) - 1
                if not self.animation_completed:  # Only set just_hatched if this is the first time completing
                    self.animation_completed = True
                    self.just_hatched = True  # Signal that we just hatched this frame
                    print("Egg just hatched! Ready for baby komodo.")
            
            # Update the image and timestamp
            self.image = self.frames[self.current_frame]
            self.last_update = now
        
        # Apply shake effect
        if self.shake_amount > 0:
            shake_x = random.randint(-self.shake_amount, self.shake_amount)
            shake_y = random.randint(-self.shake_amount, self.shake_amount)
            self.rect.center = (self.original_pos[0] + shake_x, self.original_pos[1] + shake_y)
            
            # Gradually reduce shake
            if random.random() > 0.8:  # 20% chance each frame to reduce shake
                self.shake_amount = max(0, self.shake_amount - 1)

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
play_button = Button(screen_width//2 - 100, screen_height//2 + 100, 200, 50, "Play", (0, 150, 0), (0, 200, 0))
quit_button = Button(screen_width//2 - 100, screen_height//2 + 170, 200, 50, "Quit", (150, 0, 0), (200, 0, 0))

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
    global pet_age, pet_hunger, game_state, last_age_update, last_hunger_update, egg_sprite, all_sprites, previous_pet_age
    previous_pet_age = 0
    pet_age = 0
    pet_hunger = 100
    game_state = PLAYING
    
    # Set up the time values for age/hunger updates
    current_time = pygame.time.get_ticks()
    last_age_update = current_time + 5000  # 5 second delay before first age increment
    last_hunger_update = current_time
    
    # Create a new egg sprite
    print("Creating new egg sprite during game reset")
    egg_sprite = EggSprite(egg_frames, screen_width // 2, screen_height // 2 + 100)
    
    # Clear all sprites and add the new egg sprite
    all_sprites.empty()
    all_sprites.add(egg_sprite)
    
    # Create initial flies
    fly_sprites.empty()
    max_flies = get_max_flies(pet_age)
    for _ in range(max_flies):
        create_fly()
    
    # Clear any existing explosions
    explosion_sprites.empty()

# Create a surface for the pet and scale it to a larger size
petEgg_surface = pygame.image.load('graphics/komodoEgg.png').convert_alpha()
petEgg_surface = pygame.transform.scale(petEgg_surface, (250, 250))  # Scale to 250x250 pixels

# Add logo image for menu screen - with aspect ratio preservation
try:
    # Load the logo image
    original_logo = pygame.image.load('graphics/startPageLogo.png').convert_alpha()
    
    # Get original dimensions
    orig_width, orig_height = original_logo.get_size()
    
    # Calculate new width based on desired height while preserving aspect ratio
    target_height = 200  # Increased from 150 to 200 for an even bigger logo
    aspect_ratio = orig_width / orig_height
    target_width = int(target_height * aspect_ratio)
    
    # Scale to new dimensions that preserve aspect ratio
    logo_image = pygame.transform.scale(original_logo, (target_width, target_height))
    print(f"Logo loaded and scaled from {orig_width}x{orig_height} to {target_width}x{target_height}")
except Exception as e:
    # Create a fallback logo if image loading fails
    print(f"Error loading logo: {e}")
    # Adjust fallback logo size to match new dimensions
    logo_image = pygame.Surface((600, 200), pygame.SRCALPHA)  # Increased size for bigger logo
    # Draw a simple text-based logo
    logo_font = pygame.font.Font(None, 100)  # Increased font size to match larger logo
    logo_text = logo_font.render("REPTILE SIM", True, (50, 220, 50))
    logo_shadow = logo_font.render("REPTILE SIM", True, (20, 100, 20))
    logo_image.blit(logo_shadow, (7, 7))  # Shadow effect
    logo_image.blit(logo_text, (5, 5))     # Main text
    
    # Add a simple graphical element
    pygame.draw.rect(logo_image, (30, 150, 30), (20, 80, 260, 30), border_radius=15)
    pygame.draw.rect(logo_image, (60, 200, 60), (20, 80, 260, 30), 3, border_radius=15)

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

# Initialize the egg sprite
# Create an animated sprite for the egg
print("Creating initial egg sprite")
egg_sprite = EggSprite(egg_frames, screen_width // 2, screen_height // 2 + 100)
all_sprites.add(egg_sprite)

# Add code for explosion animation after the other sprite classes
class ExplosionSprite(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Generate explosion animation frames programmatically
        self.frames = []
        
        # Create 8 frames of explosion
        colors = [(255, 255, 0), (255, 165, 0), (255, 69, 0), (255, 0, 0)]  # Yellow, orange, dark orange, red
        for i in range(8):
            # Size increases then decreases
            size = 100 if i < 4 else 100 - (i - 3) * 20
            
            frame = pygame.Surface((size, size), pygame.SRCALPHA)
            
            # Draw explosion parts (particles)
            num_particles = 16
            color = colors[min(i // 2, len(colors) - 1)]
            
            for p in range(num_particles):
                angle = p * (2 * math.pi / num_particles)
                dist = size // 2 - 5 - random.randint(0, 10)
                pos_x = size // 2 + int(dist * math.cos(angle))
                pos_y = size // 2 + int(dist * math.sin(angle))
                radius = max(2, (8 - i) * 2) + random.randint(-2, 2)
                pygame.draw.circle(frame, color, (pos_x, pos_y), radius)
            
            # Add white center
            center_size = max(5, 25 - i * 3)
            pygame.draw.circle(frame, (255, 255, 255), (size // 2, size // 2), center_size)
            
            self.frames.append(frame)
        
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
        self.animation_speed = 100  # ms per frame
        self.last_update = pygame.time.get_ticks()
    
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                self.kill()  # Remove explosion when animation is complete
            else:
                self.image = self.frames[self.current_frame]
                self.rect = self.image.get_rect(center=self.rect.center)

# Create a group for explosions
explosion_sprites = pygame.sprite.Group()

# Track the previous age to detect transitions
previous_pet_age = 0

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
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging_fly:
                # Check if the fly is dropped over the lizard
                current_lizard = None
                if pet_age < 1:
                    # Use the animated egg sprite for collision detection instead of static petEgg_surface
                    if egg_sprite.rect.collidepoint(mouse_pos):
                        print("Fed the egg!")
                        pet_hunger = min(pet_hunger + 20, 100)
                        dragging_fly.kill()
                        # Only create a new fly if there are fewer than max allowed flies
                        max_flies = get_max_flies(pet_age)
                        if len(fly_sprites) < max_flies:
                            create_fly()
                        dragging_fly = None
                        
                        # Trigger a shake effect when the egg is fed
                        egg_sprite.shake_amount = 5
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
    
    # Update background position for scrolling effect
    background_scroll -= background_scroll_speed
    # Reset when the first background has completely scrolled off-screen
    if background_scroll <= -screen_width:
        background_scroll = 0
        
    # Draw background with scrolling (draw two copies for seamless scrolling)
    screen.blit(background_image, (background_scroll, 0))
    screen.blit(background_image, (background_scroll + screen_width, 0))
    
    # Menu state
    if game_state == MENU:
        # NO menu flies as per requirement
        
        # Draw a semi-transparent overlay to make text more readable
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        # Option A: Draw title with adjusted font size to ensure it fits
        menu_title_font = pygame.font.Font(None, 54)  # Reduced from 72 to 54 to ensure it fits
        title_text = menu_title_font.render("Reptile Pet Simulator", True, (255, 255, 255))
        # Verify if title fits within screen width
        if title_text.get_width() > screen_width - 20:  # Leave 10px margin on each side
            # If still too big, reduce further
            menu_title_font = pygame.font.Font(None, 46)
            title_text = menu_title_font.render("Reptile Pet Simulator", True, (255, 255, 255))
            
        title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 8))
        screen.blit(title_text, title_rect)
        
        # Alternative Option B (commented out):
        # Use two lines for title to fit better (uncomment if preferred)
        # menu_title_font = pygame.font.Font(None, 60)  # Can be larger for two lines
        # title_text1 = menu_title_font.render("Reptile Pet", True, (255, 255, 255))
        # title_text2 = menu_title_font.render("Simulator", True, (255, 255, 255))
        # title_rect1 = title_text1.get_rect(center=(screen_width // 2, screen_height // 10))
        # title_rect2 = title_text2.get_rect(center=(screen_width // 2, screen_height // 10 + 50))
        # screen.blit(title_text1, title_rect1)
        # screen.blit(title_text2, title_rect2)
        
        # Draw logo below the title
        logo_rect = logo_image.get_rect(center=(screen_width // 2, screen_height // 4 + 30))
        screen.blit(logo_image, logo_rect)
        
        # Add game description (adjusted position for new layout)
        desc_text = test_font.render("Take care of your reptile pet and watch it grow!", True, (255, 255, 255))
        desc_rect = desc_text.get_rect(center=(screen_width // 2, screen_height // 2 - 25))
        screen.blit(desc_text, desc_rect)
        
        # Draw buttons (keep at the same position)
        play_button.draw(screen)
        quit_button.draw(screen)
    
    # Playing state
    elif game_state == PLAYING:
        # Update the age of the pet every 3 seconds (3000 milliseconds)
        now = pygame.time.get_ticks()
        
        # Store the previous age to detect transitions
        previous_pet_age = pet_age
        
        # Check if egg has just hatched - trigger immediate transition
        if pet_age == 0 and egg_sprite.animation_completed:
            if egg_sprite.just_hatched or now - last_age_update >= 1500:  # If just hatched or waited enough time
                # Force immediate transition to baby komodo
                pet_age = 1
                last_age_update = now
                print(f"Egg hatched! Pet age advanced to {pet_age} years")
                # Create an explosion effect at the egg position
                explosion = ExplosionSprite(screen_width // 2, screen_height // 2 + 100)
                explosion_sprites.add(explosion)
        # Regular age updates for older pets
        elif now - last_age_update >= 3000:
            pet_age += 1
            last_age_update = now
            print(f"Pet age: {pet_age} years")
            
            # Check for transitions and create explosions
            if previous_pet_age < 10 and pet_age >= 10:
                # Transition from baby to teenage
                print("Transforming from baby to teenage komodo!")
                explosion = ExplosionSprite(screen_width // 2, screen_height // 2 + 100)
                explosion_sprites.add(explosion)
            elif previous_pet_age < 20 and pet_age >= 20:
                # Transition from teenage to old
                print("Transforming from teenage to old komodo!")
                explosion = ExplosionSprite(screen_width // 2, screen_height // 2 + 100)
                explosion_sprites.add(explosion)
        
        # Update the hunger level - only when the egg has hatched
        hunger_interval = get_hunger_interval(pet_age)
        if pet_age >= 1:  # Only decrease hunger if egg has hatched
            if now - last_hunger_update >= hunger_interval:
                pet_hunger = max(0, pet_hunger - 10)
                last_hunger_update = now
                print(f"Pet hunger: {pet_hunger}%")
                
                # Check if pet has starved
                if pet_hunger <= 0:
                    game_state = GAME_OVER
        else:
            # Ensure hunger stays at 100% while in egg stage
            pet_hunger = 100
        
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
            # Add egg sprite to be rendered
            all_sprites.add(egg_sprite)
        elif pet_age < 10:
            all_sprites.add(baby_komodo_sprite)
        elif pet_age < 20:
            all_sprites.add(teenage_sprite)
        else:
            all_sprites.add(old_komodo_sprite)
        
        # Debug info
        if pet_age < 1:
            print(f"Egg animation state - frame: {egg_sprite.current_frame}, started: {egg_sprite.animation_started}, completed: {egg_sprite.animation_completed}")
        
        # Update and draw all sprites - make sure this is called for animation to work
        all_sprites.update()
        all_sprites.draw(screen)
        
        # Update and draw flies
        fly_sprites.update()
        fly_sprites.draw(screen)
        
        # Update and draw explosions
        explosion_sprites.update()
        explosion_sprites.draw(screen)
    
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