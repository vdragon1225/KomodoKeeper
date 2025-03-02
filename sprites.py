import pygame
import random
import math
from constants import FLY_BOUNDARY_TOP, FLY_BOUNDARY_BOTTOM, SCREEN_WIDTH

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

    def update(self):
        super().update()
        
        # Update speed based on pet's age
        self.speed = get_fly_speed(self.pet_age)
        
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