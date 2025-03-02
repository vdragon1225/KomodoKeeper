import pygame
import os
import random
import math
import logging
from sys import exit

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#----------------------------------------------------------------------
# CONSTANTS
#----------------------------------------------------------------------

# Screen settings
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2

# Fly boundaries
FLY_BOUNDARY_BOTTOM = 3 * SCREEN_HEIGHT // 4  # Flies can't go below this y-coordinate
FLY_BOUNDARY_TOP = SCREEN_HEIGHT // 6 + 30  # Increased to keep flies away from top boxes

# Box settings
BOX_SIZE = 50
BOX_COLORS = ['Red', 'Blue', 'Green', 'Purple']  # Colors for food, water, play, sleep
BOX_SPACING = SCREEN_WIDTH // 5
BOX_Y = SCREEN_HEIGHT // 8 - BOX_SIZE // 2  # Position closer to the top

# Font settings
TEST_FONT = None
LARGE_FONT = None
TITLE_FONT = None

# Background settings
BACKGROUND_SCROLL_SPEED = 1  # Pixels per frame - adjust for faster/slower scrolling

# Asset paths
ASSET_PATHS = {
    'background': 'graphics/background.png',
    'logo': 'graphics/startPageLogo.png',
    'fly': 'graphics/fly.png',
    'tombstone': 'graphics/tombstone.png'  # Added the tombstone path
}

# Animation timing settings
ANIMATION_SPEED = 0.1
EATING_DURATION = 500
EGG_ANIMATION_DELAY = 1500
HUNGER_UPDATE_INTERVAL = 1000  # Base interval in ms
AGE_INCREMENT_INTERVAL = 3000  # Time between age increments in ms

# Tombstone settings
TOMBSTONE_SIZE = (260, 360)  # Size for the tombstone image (2x bigger)
TOMBSTONE_FLY_RADIUS = 140  # Increased radius for flies to swarm around the larger tombstone
TOMBSTONE_FLY_COUNT = 8  # Number of flies in game over state

#----------------------------------------------------------------------
# UTILITY FUNCTIONS
#----------------------------------------------------------------------

# Function to calculate hunger interval based on age
def get_hunger_interval(age):
    if age < 10:
        return 1000  # 1 second for baby
    elif age < 20:
        return 1000  # 1 second for teenager
    else:
        return 1000  # 1 second for adult

# Function to load and scale an image
def load_image(path, scale_to=None, convert_alpha=True):
    try:
        if convert_alpha:
            image = pygame.image.load(path).convert_alpha()
        else:
            image = pygame.image.load(path).convert()
        
        if scale_to:
            image = pygame.transform.scale(image, scale_to)
        return image
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        # Create a fallback surface
        if scale_to:
            fallback = pygame.Surface(scale_to, pygame.SRCALPHA)
        else:
            fallback = pygame.Surface((100, 100), pygame.SRCALPHA)
        # Fill with a noticeable pattern
        pygame.draw.rect(fallback, (255, 0, 255), fallback.get_rect(), 2)
        pygame.draw.line(fallback, (255, 0, 255), (0, 0), fallback.get_rect().bottomright, 2)
        pygame.draw.line(fallback, (255, 0, 255), (0, fallback.get_rect().bottom), (fallback.get_rect().right, 0), 2)
        return fallback

# Function to load logo with proper aspect ratio
def load_and_scale_logo(path):
    try:
        # Load the logo image
        original_logo = pygame.image.load(path).convert_alpha()
        
        # Get original dimensions
        orig_width, orig_height = original_logo.get_size()
        
        # Calculate new width based on desired height while preserving aspect ratio
        target_height = 200  # Increased from 150
        aspect_ratio = orig_width / orig_height
        target_width = int(target_height * aspect_ratio)
        
        # Scale to new dimensions that preserve aspect ratio
        logo_image = pygame.transform.scale(original_logo, (target_width, target_height))
        print(f"Logo loaded and scaled from {orig_width}x{orig_height} to {target_width}x{target_height}")
        return logo_image
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
        return logo_image

# Function to generate box rectangles for UI
def generate_box_rects():
    box_rects = []
    for i in range(4):
        x_position = BOX_SPACING * (i + 1) - BOX_SIZE // 2
        box_rect = pygame.Rect(x_position, BOX_Y, BOX_SIZE, BOX_SIZE)
        box_rects.append(box_rect)
    return box_rects

#----------------------------------------------------------------------
# ASSET LOADER CLASS
#----------------------------------------------------------------------

class AssetLoader:
    """
    A class to handle loading and managing game assets.
    This centralizes asset loading and provides error handling.
    """
    def __init__(self):
        self.images = {}
        self.animations = {}
        self.sounds = {}
        
    def load_image(self, name, path, scale=None, convert_alpha=True):
        """Load a single image and store it under the given name."""
        try:
            if convert_alpha:
                image = pygame.image.load(path).convert_alpha()
            else:
                image = pygame.image.load(path).convert()
            
            if scale:
                image = pygame.transform.scale(image, scale)
                
            self.images[name] = image
            logger.info(f"Loaded image: {name} from {path}")
            return image
        except Exception as e:
            logger.error(f"Failed to load image {name} from {path}: {e}")
            # Create a fallback surface
            if scale:
                fallback = pygame.Surface(scale, pygame.SRCALPHA)
            else:
                fallback = pygame.Surface((100, 100), pygame.SRCALPHA)
            # Fill with a noticeable pattern
            pygame.draw.rect(fallback, (255, 0, 255), fallback.get_rect(), 2)
            pygame.draw.line(fallback, (255, 0, 255), (0, 0), fallback.get_rect().bottomright, 2)
            pygame.draw.line(fallback, (255, 0, 255), (0, fallback.get_rect().bottom), (fallback.get_rect().right, 0), 2)
            
            self.images[name] = fallback
            return fallback
            
    def load_animation_frames(self, name, folder_path, filename_pattern, frame_count, scale=None):
        """Load a sequence of images to create an animation."""
        frames = []
        
        for i in range(1, frame_count + 1):
            frame_path = os.path.join(folder_path, f"{filename_pattern}{i}.png")
            frame_name = f"{name}_{i}"
            
            frame = self.load_image(frame_name, frame_path, scale)
            frames.append(frame)
            
        self.animations[name] = frames
        logger.info(f"Loaded animation: {name} with {frame_count} frames")
        return frames
        
    def load_sound(self, name, path):
        """Load a sound file and store it under the given name."""
        try:
            sound = pygame.mixer.Sound(path)
            self.sounds[name] = sound
            logger.info(f"Loaded sound: {name} from {path}")
            return sound
        except Exception as e:
            logger.error(f"Failed to load sound {name} from {path}: {e}")
            return None
            
    def get_image(self, name):
        """Retrieve a loaded image by name."""
        if name in self.images:
            return self.images[name]
        logger.warning(f"Image '{name}' not found in loader")
        return None
        
    def get_animation(self, name):
        """Retrieve a loaded animation by name."""
        if name in self.animations:
            return self.animations[name]
        logger.warning(f"Animation '{name}' not found in loader")
        return None
        
    def get_sound(self, name):
        """Retrieve a loaded sound by name."""
        if name in self.sounds:
            return self.sounds[name]
        logger.warning(f"Sound '{name}' not found in loader")
        return None
        
    def extract_frames_from_spritesheet(self, name, sheet_path, frame_width, frame_height, frame_count, scale=None):
        """Extract frames from a spritesheet and store them as an animation."""
        try:
            sprite_sheet = pygame.image.load(sheet_path).convert_alpha()
            sheet_width, sheet_height = sprite_sheet.get_size()
            
            frames = []
            for i in range(frame_count):
                rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                if rect.x + rect.width <= sheet_width and rect.y + rect.height <= sheet_height:
                    frame = sprite_sheet.subsurface(rect)
                    if scale:
                        frame = pygame.transform.scale(frame, scale)
                    frames.append(frame)
                else:
                    raise ValueError(f"Frame {i} outside sheet area. Sheet: {sheet_width}x{sheet_height}, Frame: {frame_width}x{frame_height}")
            
            self.animations[name] = frames
            logger.info(f"Extracted {frame_count} frames from spritesheet: {name}")
            return frames
        except Exception as e:
            logger.error(f"Failed to extract frames from spritesheet {name}: {e}")
            # Create placeholder frames
            frames = []
            for i in range(frame_count):
                size = scale if scale else (frame_width, frame_height)
                surf = pygame.Surface(size, pygame.SRCALPHA)
                pygame.draw.rect(surf, (255, 0, 255), surf.get_rect(), 2)
                pygame.draw.circle(surf, (255, 0, 255), (size[0]//2, size[1]//2), min(size[0], size[1])//4)
                frames.append(surf)
            
            self.animations[name] = frames
            return frames

#----------------------------------------------------------------------
# SPRITE CLASSES
#----------------------------------------------------------------------

# Function to extract frames from a sprite sheet
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

# Tombstone sprite class
class TombstoneSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, size=TOMBSTONE_SIZE):
        super().__init__()
        # Try to load the tombstone image
        try:
            self.image = pygame.image.load('graphics/tombstone.png').convert_alpha()
            
            # Get original dimensions for proper aspect ratio scaling
            orig_width, orig_height = self.image.get_size()
            aspect_ratio = orig_width / orig_height
            
            # Determine new dimensions while preserving aspect ratio
            # If the original image is already stretched, we'll correct it
            new_width = size[0]
            new_height = size[1]
            
            # If needed, adjust based on aspect ratio to prevent distortion
            if new_width / new_height != aspect_ratio:
                # We'll prioritize the height and adjust width accordingly
                new_width = int(new_height * aspect_ratio)
                if new_width > size[0] * 1.2:  # Limit maximum width
                    new_width = size[0]
                    new_height = int(new_width / aspect_ratio)
            
            self.image = pygame.transform.scale(self.image, (new_width, new_height))
            print(f"Tombstone scaled to {new_width}x{new_height}")
            
        except Exception as e:
            print(f"Error loading tombstone image: {e}")
            # Create a placeholder tombstone
            self.image = pygame.Surface(size, pygame.SRCALPHA)
            # Draw a more tombstone-like shape
            tombstone_color = (120, 120, 120)
            # Base
            pygame.draw.rect(self.image, tombstone_color, (size[0]//4, size[1]//2, size[0]//2, size[1]//2))
            # Top rounded part
            pygame.draw.rect(self.image, tombstone_color, (size[0]//4, 0, size[0]//2, size[1]//2), border_radius=15)
            # Add some texture/details
            darker_color = (80, 80, 80)
            pygame.draw.rect(self.image, darker_color, (size[0]//4, 0, size[0]//2, size[1]//2), 3, border_radius=15)
            pygame.draw.line(self.image, darker_color, (size[0]//2, size[1]//4), (size[0]//2, size[1]//2 + size[1]//4), 2)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.death_time = pygame.time.get_ticks()
        
        # Define an invisible boundary for flies
        self.boundary_rect = self.rect.inflate(TOMBSTONE_FLY_RADIUS*2, TOMBSTONE_FLY_RADIUS*2)
        
        print(f"Tombstone created at {x}, {y}")

# Base animated sprite class
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, frames, x, y):
        super().__init__()
        self.frames = frames
        self.eating_frames = []  # Will be set separately for each age group
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

# Specialized egg sprite class
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

# Fly sprite class that moves around
class FlySprite(AnimatedSprite):
    def __init__(self, frames, x, y, pet_age):
        super().__init__(frames, x, y)
        self.speed = get_fly_speed(pet_age)  # Set initial speed based on pet's age
        self.direction = random.uniform(0, 2 * math.pi)  # Random direction in radians
        self.direction_change_time = pygame.time.get_ticks()
        self.being_dragged = False
        self.original_rect = self.rect.copy()
        self.pet_age = pet_age  # Store pet_age for speed updates
        self.game_over_mode = False  # Flag for special behavior during game over
        self.orbit_angle = random.uniform(0, 2 * math.pi)  # Starting angle for orbit
        self.orbit_speed = random.uniform(0.02, 0.05)  # Speed of orbit
        self.orbit_distance = random.uniform(TOMBSTONE_FLY_RADIUS - 20, TOMBSTONE_FLY_RADIUS + 20)  # Random orbit distance
        self.orbit_center = None  # Will be set when game over occurs
        self.orbit_height_offset = random.uniform(-30, 30)  # Vertical variation

    def update(self):
        super().update()
        
        # Update speed based on pet's age
        self.speed = get_fly_speed(self.pet_age)
        
        # Only move if not being dragged
        if not self.being_dragged:
            if self.game_over_mode and self.orbit_center:
                # Orbit around tombstone behavior
                self.orbit_angle += self.orbit_speed
                
                # Calculate position on elliptical orbit
                orbit_x = self.orbit_center[0] + math.cos(self.orbit_angle) * self.orbit_distance
                orbit_y = self.orbit_center[1] + math.sin(self.orbit_angle) * (self.orbit_distance * 0.7) + self.orbit_height_offset
                
                # Add slight random movement for more natural behavior
                orbit_x += random.uniform(-1, 1)
                orbit_y += random.uniform(-1, 1)
                
                self.rect.center = (orbit_x, orbit_y)
            else:
                # Normal movement behavior
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
                if self.rect.right > SCREEN_WIDTH:
                    self.rect.right = SCREEN_WIDTH
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
        
    def update_pet_age(self, pet_age):
        self.pet_age = pet_age
        
    def set_game_over_mode(self, enabled, center=None):
        """Set the fly to game over mode orbiting the tombstone"""
        self.game_over_mode = enabled
        if enabled and center:
            self.orbit_center = center
            # Assign a random starting position around the orbit
            self.orbit_angle = random.uniform(0, 2 * math.pi)
            # Adjust speed and distance for interesting patterns
            self.orbit_speed = random.uniform(0.01, 0.03)
            self.orbit_distance = random.uniform(TOMBSTONE_FLY_RADIUS - 10, TOMBSTONE_FLY_RADIUS + 10)

# Explosion animation sprite
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

# Function to create a fly at a random position
def create_fly(fly_frames, fly_sprites, pet_age, max_flies):
    if len(fly_sprites) < max_flies:  # Ensure there are only up to the maximum number of flies
        fly = FlySprite(
            fly_frames, 
            random.randint(50, SCREEN_WIDTH - 50), 
            random.randint(FLY_BOUNDARY_TOP + 20, FLY_BOUNDARY_BOTTOM - 20),
            pet_age
        )
        fly_sprites.add(fly)
        return fly
    return None

# Function to create flies for game over state around tombstone
def create_tombstone_flies(fly_frames, fly_sprites, tombstone_center, count=TOMBSTONE_FLY_COUNT):
    # Clear existing flies
    fly_sprites.empty()
    
    # Create new flies at positions around the tombstone
    for i in range(count):
        angle = (i * 2 * math.pi / count)
        x = tombstone_center[0] + math.cos(angle) * TOMBSTONE_FLY_RADIUS
        y = tombstone_center[1] + math.sin(angle) * TOMBSTONE_FLY_RADIUS
        
        fly = FlySprite(fly_frames, x, y, 20)  # Use adult speed for game over flies
        fly.set_game_over_mode(True, tombstone_center)
        fly_sprites.add(fly)

#----------------------------------------------------------------------
# UI CLASSES AND FUNCTIONS
#----------------------------------------------------------------------

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

# Create and return menu buttons
def create_menu_buttons():
    play_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 100, 200, 50, "Play", (0, 150, 0), (0, 200, 0))
    quit_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 170, 200, 50, "Quit", (150, 0, 0), (200, 0, 0))
    return play_button, quit_button

# Create and return game over buttons
def create_game_over_buttons():
    # Creating buttons with preset dimensions but their positions will be updated in draw_game_over
    button_width = 150  # Reduced from 200
    button_height = 40  # Reduced from 50
    retry_button = Button(0, 0, button_width, button_height, "Retry", (0, 150, 0), (0, 200, 0))
    exit_button = Button(0, 0, button_width, button_height, "Exit", (150, 0, 0), (200, 0, 0))
    return retry_button, exit_button

# Draw the menu screen
def draw_menu(screen, logo_image, play_button, quit_button, background_image=None, background_scroll=0):
    # Draw scrolling background if available
    if background_image:
        # Draw background with scrolling (draw two copies for seamless scrolling)
        screen.blit(background_image, (background_scroll, 0))
        screen.blit(background_image, (background_scroll + SCREEN_WIDTH, 0))
    
    # Draw a semi-transparent overlay with slightly less opacity
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 100))  # Reduced from 128 to 100 for better visibility
    screen.blit(overlay, (0, 0))
    
    # Draw title with adjusted font size to ensure it fits
    menu_title_font = pygame.font.Font(None, 54)  # Reduced from 72 to 54 to ensure it fits
    title_text = menu_title_font.render("Reptile Pet Simulator", True, (255, 255, 255))
    # Verify if title fits within screen width
    if title_text.get_width() > SCREEN_WIDTH - 20:  # Leave 10px margin on each side
        # If still too big, reduce further
        menu_title_font = pygame.font.Font(None, 46)
        title_text = menu_title_font.render("Reptile Pet Simulator", True, (255, 255, 255))
        
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 8))
    screen.blit(title_text, title_rect)
    
    # Draw logo below the title
    logo_rect = logo_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 30))
    screen.blit(logo_image, logo_rect)
    
    # Add game description (adjusted position for new layout)
    desc_font = pygame.font.Font(None, 24)
    desc_text = desc_font.render("Take care of your reptile pet and watch it grow!", True, (255, 255, 255))
    desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 25))
    screen.blit(desc_text, desc_rect)
    
    # Draw buttons
    play_button.draw(screen)
    quit_button.draw(screen)

# Draw the game over screen
def draw_game_over(screen, pet_age, retry_button, exit_button):
    # Display game over message - moved higher to make room
    large_font = pygame.font.Font(None, 48)
    game_over_text = large_font.render("Game Over", True, (255, 0, 0))
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5))
    screen.blit(game_over_text, game_over_rect)
    
    # Display final stats - centered
    test_font = pygame.font.Font(None, 24)
    final_age_text = test_font.render(f"Your pet lived to {pet_age} years old", True, (255, 255, 255))
    final_age_rect = final_age_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5 + 40))
    screen.blit(final_age_text, final_age_rect)
    
    # Position buttons side by side at the bottom with proper spacing - smaller buttons
    button_width = 150  # Reduced from 200
    button_height = 40  # Reduced from 50
    button_spacing = 40  # Slightly increased spacing between smaller buttons
    total_width = (button_width * 2) + button_spacing
    start_x = (SCREEN_WIDTH - total_width) // 2
    
    # Move buttons higher to avoid potential overlap with the larger tombstone
    retry_button.rect = pygame.Rect(start_x, SCREEN_HEIGHT - 120, button_width, button_height)
    exit_button.rect = pygame.Rect(start_x + button_width + button_spacing, SCREEN_HEIGHT - 120, button_width, button_height)
    
    # Add a semi-transparent background behind buttons for better visibility
    for button in [retry_button, exit_button]:
        button_bg = pygame.Surface((button.rect.width + 10, button.rect.height + 10), pygame.SRCALPHA)
        button_bg.fill((0, 0, 0, 128))
        screen.blit(button_bg, (button.rect.x - 5, button.rect.y - 5))
    
    # Draw buttons
    retry_button.draw(screen)
    exit_button.draw(screen)

# Draw the playing screen UI elements
def draw_playing_ui(screen, pet_age, pet_hunger, box_rects):
    # Render the age and hunger text
    test_font = pygame.font.Font(None, 24)
    age_text = test_font.render(f"Pet age: {pet_age} years", True, (255, 255, 255))
    hunger_text = test_font.render(f"Pet hunger: {pet_hunger}%", True, (255, 255, 255))
    screen.blit(age_text, (10, 10))
    screen.blit(hunger_text, (10, 40))
    
    # Draw the status boxes
    for i, rect in enumerate(box_rects):
        color = ['Red', 'Blue', 'Green', 'Purple'][i % 4]  # Get color from list
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, 'White', rect, 2)  # White border for visibility

#----------------------------------------------------------------------
# GAME CLASS
#----------------------------------------------------------------------

class Game:
    def __init__(self):
        self.game_state = MENU
        self.pet_age = 0
        self.pet_hunger = 100
        self.previous_pet_age = 0
        self.last_age_update = 0
        self.last_hunger_update = 0
        self.background_scroll = 0
        self.background_scroll_speed = 1
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.fly_sprites = pygame.sprite.Group()
        self.explosion_sprites = pygame.sprite.Group()
        self.tombstone_sprite = None
        
        # Game sprites
        self.egg_sprite = None
        self.baby_komodo_sprite = None
        self.teenage_sprite = None
        self.old_komodo_sprite = None
        
        # Drag and drop
        self.dragging_fly = None
        
        # UI elements
        self.box_rects = generate_box_rects()
        
        # Game over state
        self.game_over_time = 0
        
    def load_assets(self):
        # Load background
        self.background_image = load_image('graphics/background.png', (SCREEN_WIDTH, SCREEN_HEIGHT), False)
        
        # Load and create sprite frames
        self.load_sprite_frames()
        
        # Load tombstone image
        try:
            self.tombstone_image = load_image('graphics/tombstone.png', TOMBSTONE_SIZE)
            print("Tombstone image loaded successfully")
        except Exception as e:
            print(f"Error loading tombstone image: {e}")
            # Create a placeholder tombstone
            self.tombstone_image = pygame.Surface(TOMBSTONE_SIZE, pygame.SRCALPHA)
            pygame.draw.rect(self.tombstone_image, (100, 100, 100), (0, TOMBSTONE_SIZE[1]//2, TOMBSTONE_SIZE[0], TOMBSTONE_SIZE[1]//2))
            pygame.draw.rect(self.tombstone_image, (80, 80, 80), (TOMBSTONE_SIZE[0]//4, 0, TOMBSTONE_SIZE[0]//2, TOMBSTONE_SIZE[1]//2), border_radius=15)
        
        # Create sprite instances
        self.create_sprites()
        
    def load_sprite_frames(self):
        # Load sprite sheet for flies
        sprite_sheet = load_image('graphics/fly.png')
        
        # Extract and scale fly frames
        try:
            self.fly_frames = extract_frames(sprite_sheet, 32, 32, 4)
            self.fly_frames = [pygame.transform.scale(frame, (64, 64)) for frame in self.fly_frames]
        except ValueError as e:
            print(f"Error extracting frames: {e}")
            # Create placeholder fly frames if extraction fails
            self.fly_frames = []
            for _ in range(4):
                surf = pygame.Surface((32, 32), pygame.SRCALPHA)
                pygame.draw.circle(surf, (0, 0, 0), (16, 16), 8)
                self.fly_frames.append(surf)
        
        # Load teenage komodo frames
        teenage_frames = [
            load_image(f'graphics/midkomodowalking/komodoWalking{i}.png') for i in range(1, 5)
        ]
        self.teenage_frames = [pygame.transform.scale(frame, (250, 250)) for frame in teenage_frames]
        
        # Load baby komodo frames
        baby_komodo_frames = [
            load_image(f'graphics/Baby/babyKomodo{i}.png') for i in range(1, 5)
        ]
        self.baby_komodo_frames = [pygame.transform.scale(frame, (250, 250)) for frame in baby_komodo_frames]
        
        # Load old komodo frames
        old_komodo_frames = [
            load_image(f'graphics/oldkomodo/oldKomodo{i}.png') for i in range(1, 7)
        ]
        self.old_komodo_frames = [pygame.transform.scale(frame, (250, 250)) for frame in old_komodo_frames]
        
        # Load eating animation frames
        komodo_eating_frames = [
            load_image(f'graphics/midkomodoeating/komodoEating{i}.png') for i in range(1, 9)
        ]
        self.komodo_eating_frames = [pygame.transform.scale(frame, (250, 250)) for frame in komodo_eating_frames]
        
        baby_komodo_eating_frames = [
            load_image(f'graphics/baby/babyKomodoEating{i}.png') for i in range(1, 5)
        ]
        self.baby_komodo_eating_frames = [pygame.transform.scale(frame, (250, 250)) for frame in baby_komodo_eating_frames]
        
        old_komodo_eating_frames = [
            load_image(f'graphics/oldKomodoEating{i}.png') for i in range(1, 3)
        ]
        self.old_komodo_eating_frames = [pygame.transform.scale(frame, (250, 250)) for frame in old_komodo_eating_frames]
        
        # Load egg frames
        try:
            egg_frames = [
                load_image(f'graphics/egg/komodoEgg{i}.png') for i in range(1, 4)
            ]
            print("Egg frames loaded successfully:")
            for i, frame in enumerate(egg_frames):
                print(f"Frame {i}: size={frame.get_size()}")
            
            self.egg_frames = [pygame.transform.scale(frame, (250, 250)) for frame in egg_frames]
        except Exception as e:
            print(f"Error loading egg frames: {e}")
            # Create placeholder egg frames
            self.egg_frames = []
            base_egg = pygame.Surface((250, 250), pygame.SRCALPHA)
            pygame.draw.ellipse(base_egg, (255, 255, 200), (50, 50, 150, 200))  # Base egg shape
            
            self.egg_frames.append(base_egg.copy())  # Frame 1: intact egg
            
            crack_egg = base_egg.copy()
            pygame.draw.line(crack_egg, (0, 0, 0), (100, 100), (150, 150), 3)  # Frame 2: egg with crack
            self.egg_frames.append(crack_egg)
            
            hatching_egg = base_egg.copy()
            pygame.draw.polygon(hatching_egg, (0, 0, 0), [(80, 80), (120, 70), (160, 90), (170, 130)], 3)  # Frame 3: egg hatching
            self.egg_frames.append(hatching_egg)
            
            print("Created placeholder egg frames")
        
    def create_sprites(self):
        # Create animated sprites
        self.teenage_sprite = AnimatedSprite(self.teenage_frames, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
        self.teenage_sprite.eating_frames = self.komodo_eating_frames
        
        self.baby_komodo_sprite = AnimatedSprite(self.baby_komodo_frames, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
        self.baby_komodo_sprite.eating_frames = self.baby_komodo_eating_frames
        
        self.old_komodo_sprite = AnimatedSprite(self.old_komodo_frames, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
        self.old_komodo_sprite.eating_frames = self.old_komodo_eating_frames
        
        # Create egg sprite
        print("Creating new egg sprite during game initialization")
        self.egg_sprite = EggSprite(self.egg_frames, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
        self.all_sprites.add(self.egg_sprite)
        
    def create_tombstone(self):
        """Create a tombstone at the position of the current pet"""
        # First, clear all lizard sprites to ensure they disappear
        self.all_sprites.empty()
        
        # Create the tombstone - position it lower on the screen
        tombstone_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120)
        self.tombstone_sprite = TombstoneSprite(tombstone_pos[0], tombstone_pos[1])
        self.all_sprites.add(self.tombstone_sprite)
        
        # Create the flies that swarm around the tombstone
        create_tombstone_flies(self.fly_frames, self.fly_sprites, tombstone_pos)
        
        # Set game over time for timing effects
        self.game_over_time = pygame.time.get_ticks()
        
        # Create an explosion effect where the pet died
        explosion = ExplosionSprite(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
        self.explosion_sprites.add(explosion)
        
        print("Tombstone created - pet has died")
        
    def reset_game(self):
        self.previous_pet_age = 0
        self.pet_age = 0
        self.pet_hunger = 100
        self.game_state = PLAYING
        
        # Set up the time values for age/hunger updates
        current_time = pygame.time.get_ticks()
        self.last_age_update = current_time + 5000  # 5 second delay before first age increment
        self.last_hunger_update = current_time
        
        # Create a new egg sprite
        print("Creating new egg sprite during game reset")
        self.egg_sprite = EggSprite(self.egg_frames, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
        
        # Clear all sprites and add the new egg sprite
        self.all_sprites.empty()
        self.all_sprites.add(self.egg_sprite)
        
        # Clear existing tombstone
        self.tombstone_sprite = None
        
        # Clear existing flies and create new ones
        self.fly_sprites.empty()
        max_flies = get_max_flies(self.pet_age)
        for _ in range(max_flies):
            create_fly(self.fly_frames, self.fly_sprites, self.pet_age, max_flies)
        
        # Clear any existing explosions
        self.explosion_sprites.empty()
        
    def update(self):
        now = pygame.time.get_ticks()
        
        # Update background scroll
        self.update_background_scroll()
            
        # Only update game logic if in PLAYING state
        if self.game_state == PLAYING:
            # Store the previous age to detect transitions
            self.previous_pet_age = self.pet_age
            
            # Check if egg has just hatched - trigger immediate transition
            if self.pet_age == 0 and self.egg_sprite.animation_completed:
                if self.egg_sprite.just_hatched or now - self.last_age_update >= 1500:
                    # Force immediate transition to baby komodo
                    self.pet_age = 1
                    self.last_age_update = now
                    print(f"Egg hatched! Pet age advanced to {self.pet_age} years")
                    # Create an explosion effect at the egg position
                    explosion = ExplosionSprite(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
                    self.explosion_sprites.add(explosion)
            # Regular age updates for older pets
            elif now - self.last_age_update >= 3000:
                self.pet_age += 1
                self.last_age_update = now
                print(f"Pet age: {self.pet_age} years")
                
                # Check for transitions and create explosions
                if self.previous_pet_age < 10 and self.pet_age >= 10:
                    # Transition from baby to teenage
                    print("Transforming from baby to teenage komodo!")
                    explosion = ExplosionSprite(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
                    self.explosion_sprites.add(explosion)
                elif self.previous_pet_age < 20 and self.pet_age >= 20:
                    # Transition from teenage to old
                    print("Transforming from teenage to old komodo!")
                    explosion = ExplosionSprite(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
                    self.explosion_sprites.add(explosion)
            
            # Update the hunger level - only when the egg has hatched
            hunger_interval = get_hunger_interval(self.pet_age)
            if self.pet_age >= 1:  # Only decrease hunger if egg has hatched
                if now - self.last_hunger_update >= hunger_interval:
                    self.pet_hunger = max(0, self.pet_hunger - 10)
                    self.last_hunger_update = now
                    print(f"Pet hunger: {self.pet_hunger}%")
                    
                    # Check if pet has starved
                    if self.pet_hunger <= 0:
                        self.game_state = GAME_OVER
                        self.create_tombstone()  # Create tombstone when pet dies
            else:
                # Ensure hunger stays at 100% while in egg stage
                self.pet_hunger = 100
                
            # Update active sprite based on age
            # Only update living sprites if still playing and not transitioning to game over
            if self.game_state == PLAYING and self.pet_hunger > 0:
                self.all_sprites.empty()
                
                if self.pet_age < 1:
                    # Add egg sprite to be rendered
                    self.all_sprites.add(self.egg_sprite)
                elif self.pet_age < 10:
                    self.all_sprites.add(self.baby_komodo_sprite)
                elif self.pet_age < 20:
                    self.all_sprites.add(self.teenage_sprite)
                else:
                    self.all_sprites.add(self.old_komodo_sprite)
            
            # Update flies' pet_age to adjust their behavior
            for fly in self.fly_sprites:
                fly.update_pet_age(self.pet_age)
        
        # Special animation for game over state with the tombstone
        if self.game_state == GAME_OVER and self.tombstone_sprite:
            # Make sure flies are in game over mode
            for fly in self.fly_sprites:
                if not fly.game_over_mode:
                    fly.set_game_over_mode(True, self.tombstone_sprite.rect.center)
                
        # Update all sprite groups
        self.all_sprites.update()
        self.fly_sprites.update()
        self.explosion_sprites.update()
        
    def draw(self, screen):
        # Draw scrolling background
        screen.blit(self.background_image, (self.background_scroll, 0))
        screen.blit(self.background_image, (self.background_scroll + SCREEN_WIDTH, 0))
        
        # Draw all sprites
        self.all_sprites.draw(screen)
        self.fly_sprites.draw(screen)
        self.explosion_sprites.draw(screen)
        
        # For debugging - visualize the fly boundary around tombstone
        if self.game_state == GAME_OVER and self.tombstone_sprite and False:  # Set to True to enable debug visualization
            pygame.draw.circle(screen, (255, 0, 0), self.tombstone_sprite.rect.center, TOMBSTONE_FLY_RADIUS, 1)
        
    def handle_mouse_down(self, mouse_pos):
        if self.game_state == PLAYING:
            # Check if a fly is clicked
            for fly in self.fly_sprites:
                if fly.rect.collidepoint(mouse_pos):
                    self.dragging_fly = fly
                    fly.start_drag()
                    break
                    
    def handle_mouse_up(self, mouse_pos):
        if self.dragging_fly and self.game_state == PLAYING:
            # Check if the fly is dropped over the lizard
            current_lizard = None
            if self.pet_age < 1:
                # Use the animated egg sprite for collision detection
                if self.egg_sprite.rect.collidepoint(mouse_pos):
                    print("Fed the egg!")
                    self.pet_hunger = min(self.pet_hunger + 20, 100)
                    self.dragging_fly.kill()
                    # Only create a new fly if there are fewer than max allowed flies
                    max_flies = get_max_flies(self.pet_age)
                    if len(self.fly_sprites) < max_flies:
                        create_fly(self.fly_frames, self.fly_sprites, self.pet_age, max_flies)
                    self.dragging_fly = None
                    
                    # Trigger a shake effect when the egg is fed
                    self.egg_sprite.shake_amount = 5
            else:
                # Check which lizard sprite to use based on age
                if self.pet_age < 10:
                    current_lizard = self.baby_komodo_sprite
                    print("Baby komodo will eat")
                elif self.pet_age < 20:
                    current_lizard = self.teenage_sprite
                    print("Teenage komodo will eat")
                else:
                    current_lizard = self.old_komodo_sprite
                    print("Old komodo will eat")
                
                if current_lizard and current_lizard.rect.collidepoint(mouse_pos):
                    print(f"Fed the lizard! (Age: {self.pet_age})")
                    # Explicitly trigger eating animation with debug
                    current_lizard.start_eating()
                    self.pet_hunger = min(self.pet_hunger + 20, 100)
                    self.dragging_fly.kill()
                    # Create a new fly to replace the eaten one if not exceeding max
                    max_flies = get_max_flies(self.pet_age)
                    if len(self.fly_sprites) < max_flies:
                        create_fly(self.fly_frames, self.fly_sprites, self.pet_age, max_flies)
                    self.dragging_fly = None
            
            # If not dropped on lizard, return fly to original position
            if self.dragging_fly:
                self.dragging_fly.stop_drag()
                self.dragging_fly = None
                
    def handle_mouse_motion(self, mouse_pos):
        # Update dragged fly position
        if self.dragging_fly:
            self.dragging_fly.update_drag_position(mouse_pos)
            
    def update_background_scroll(self):
        # Update background position for scrolling effect regardless of game state
        self.background_scroll -= self.background_scroll_speed
        # Reset when the first background has completely scrolled off-screen
        if self.background_scroll <= -SCREEN_WIDTH:
            self.background_scroll = 0

#----------------------------------------------------------------------
# MAIN GAME LOOP
#----------------------------------------------------------------------

def main():
    # Initialize Pygame
    pygame.init()
    
    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Reptile Pet Simulator")
    clock = pygame.time.Clock()
    
    # Create UI elements
    play_button, quit_button = create_menu_buttons()
    retry_button, exit_button = create_game_over_buttons()
    box_rects = generate_box_rects()
    
    # Load logo
    logo_image = load_and_scale_logo('graphics/startPageLogo.png')
    
    # Create game instance
    game = Game()
    game.load_assets()
    
    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                if game.game_state == MENU:
                    # Check menu buttons
                    if play_button.rect.collidepoint(mouse_pos):
                        game.game_state = PLAYING
                        game.reset_game()
                    elif quit_button.rect.collidepoint(mouse_pos):
                        pygame.quit()
                        exit()
                
                elif game.game_state == GAME_OVER:
                    # Check game over buttons
                    if retry_button.rect.collidepoint(mouse_pos):
                        game.reset_game()
                    elif exit_button.rect.collidepoint(mouse_pos):
                        pygame.quit()
                        exit()
                
                elif game.game_state == PLAYING:
                    # Handle game play mouse down
                    game.handle_mouse_down(mouse_pos)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                # Handle game play mouse up
                if game.game_state == PLAYING:
                    game.handle_mouse_up(event.pos)
            
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                
                # Update button hover states
                if game.game_state == MENU:
                    play_button.is_hovered(mouse_pos)
                    quit_button.is_hovered(mouse_pos)
                elif game.game_state == GAME_OVER:
                    retry_button.is_hovered(mouse_pos)
                    exit_button.is_hovered(mouse_pos)
                
                # Update dragged fly position
                if game.game_state == PLAYING:
                    game.handle_mouse_motion(mouse_pos)
        
        # Clear the screen
        screen.fill((0, 0, 0))
        
        # Update game logic
        game.update()
        
        # Draw game elements based on game state
        if game.game_state == MENU:
            # Update menu background scroll
            game.update_background_scroll()
            # Draw menu with scrolling background
            draw_menu(screen, logo_image, play_button, quit_button, 
                     background_image=game.background_image, 
                     background_scroll=game.background_scroll)
            
        elif game.game_state == PLAYING:
            # Draw game background and sprites
            game.draw(screen)
            
            # Draw game UI
            draw_playing_ui(screen, game.pet_age, game.pet_hunger, box_rects)
            
        elif game.game_state == GAME_OVER:
            # Draw game background
            game.draw(screen)
            
            # Draw game over screen
            draw_game_over(screen, game.pet_age, retry_button, exit_button)
        
        # Update the display
        pygame.display.flip()
        clock.tick(60)  # Limit the frame rate to 60 FPS

if __name__ == "__main__":
    main()