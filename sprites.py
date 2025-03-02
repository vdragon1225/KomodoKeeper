import pygame
import random
from constants import FLY_BOUNDARY_TOP, FLY_BOUNDARY_BOTTOM, SCREEN_WIDTH

# Function to extract frames from a sprite sheet
def extract_frames(sheet, frame_width, frame_height, num_frames):
    sheet_width, sheet_height = sheet.get_size()
    print(f"Sprite sheet dimensions: {sheet_width}x{sheet_height}")
    frames = []
    for i in range(num_frames):
        rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
        if rect.x + rect.width <= sheet_width and rect.y + rect.height <= sheet_height:
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), rect)
            frames.append(frame)
        else:
            print(f"Warning: Frame {i} is outside sprite sheet boundaries")
            # Create fallback frame
            fallback = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            pygame.draw.rect(fallback, (255, 0, 255), fallback.get_rect(), 2)
            frames.append(fallback)
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
        
        # Handle eating animation if active
        if self.is_eating:
            if now - self.eating_timer >= self.eating_duration:
                self.is_eating = False
                self.current_frame = 0
                self.image = self.frames[self.current_frame]
            else:
                # Animate eating
                if now - self.last_update > 100:
                    self.last_update = now
                    self.current_frame = (self.current_frame + 1) % len(self.eating_frames)
                    self.image = self.eating_frames[self.current_frame]
        else:
            # Regular animation
            if now - self.last_update > 100:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]

    def start_eating(self):
        self.is_eating = True
        self.eating_timer = pygame.time.get_ticks()
        self.current_frame = 0
        # Use eating frames if available, otherwise use regular frames
        if len(self.eating_frames) > 0:
            self.image = self.eating_frames[self.current_frame]
        else:
            self.image = self.frames[self.current_frame]

# Specialized egg sprite class
class EggSprite(pygame.sprite.Sprite):
    def __init__(self, frames, x, y):
        super().__init__()
        self.frames = frames
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
        self.animation_speed = 0.05  # Slower animation for egg
        self.last_update = pygame.time.get_ticks()
    
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 200:  # Slower animation rate
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

# Tombstone sprite class for game over state
class TombstoneSprite(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((60, 80), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (120, 120, 120), (0, 20, 60, 60), border_radius=5)
        pygame.draw.rect(self.image, (100, 100, 100), (10, 0, 40, 30), border_radius=10)
        self.rect = self.image.get_rect(center=(x, y))
        
    def update(self):
        # Tombstones don't animate, so this is empty
        pass

# Fly sprite class that moves around
class FlySprite(AnimatedSprite):
    def __init__(self, frames, x, y, pet_age):
        super().__init__(frames, x, y)
        self.speed = get_fly_speed(pet_age)
        self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        self.dragging = False
        self.original_speed = self.speed

    def update(self):
        if not self.dragging:
            # Move in current direction
            self.rect.x += self.direction.x * self.speed
            self.rect.y += self.direction.y * self.speed
            
            # Bounce off screen edges
            if self.rect.left < 0:
                self.rect.left = 0
                self.direction.x *= -1
            elif self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH
                self.direction.x *= -1
            
            # Bounce off top/bottom boundaries
            if self.rect.top < FLY_BOUNDARY_TOP:
                self.rect.top = FLY_BOUNDARY_TOP
                self.direction.y *= -1
            elif self.rect.bottom > FLY_BOUNDARY_BOTTOM:
                self.rect.bottom = FLY_BOUNDARY_BOTTOM
                self.direction.y *= -1
                
            # Occasionally change direction slightly
            if random.random() < 0.02:  # 2% chance per frame
                self.direction = pygame.math.Vector2(
                    self.direction.x + random.uniform(-0.2, 0.2),
                    self.direction.y + random.uniform(-0.2, 0.2)
                ).normalize()
        
        # Continue with animation
        super().update()

    def start_drag(self):
        self.dragging = True
        self.speed = 0
    
    def update_drag_position(self, pos):
        if self.dragging:
            self.rect.center = pos
    
    def stop_drag(self):
        self.dragging = False
        self.speed = self.original_speed
        # Randomize direction when dropped
        self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        
    def update_pet_age(self, pet_age):
        self.original_speed = get_fly_speed(pet_age)
        if not self.dragging:
            self.speed = self.original_speed

# Explosion animation sprite
class ExplosionSprite(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Create simple explosion animation frames
        self.frames = []
        sizes = [10, 20, 30, 40, 50, 40, 30, 20, 10]
        for size in sizes:
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 200, 0, 200), (size//2, size//2), size//2)  # Orange-yellow
            self.frames.append(surf)
            
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
        self.last_update = pygame.time.get_ticks()
    
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 60:  # Fast animation
            self.last_update = now
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                self.kill()  # Remove when animation is complete
            else:
                self.image = self.frames[self.current_frame]
                self.rect = self.image.get_rect(center=self.rect.center)