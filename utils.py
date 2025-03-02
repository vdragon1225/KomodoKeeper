import pygame
import random
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, BOX_SIZE, BOX_SPACING, BOX_Y

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

# Function to create a fly at a random position
def create_fly(fly_frames, fly_sprites, pet_age, max_flies):
    if len(fly_sprites) < max_flies:  # Ensure there are only up to the maximum number of flies
        from sprites import FlySprite, FLY_BOUNDARY_TOP, FLY_BOUNDARY_BOTTOM
        fly = FlySprite(
            fly_frames, 
            random.randint(50, SCREEN_WIDTH - 50), 
            random.randint(FLY_BOUNDARY_TOP + 20, FLY_BOUNDARY_BOTTOM - 20),
            pet_age
        )
        fly_sprites.add(fly)
        return fly
    return None