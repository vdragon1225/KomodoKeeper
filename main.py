import pygame
from sys import exit

# Initialize Pygame
pygame.init()

# Set up the display
screen_width = 400
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Reptile Pet Simulator")
clock = pygame.time.Clock()
test_font = pygame.font.Font(None, 24)

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

# Create an instance of the animated sprite
teenage_sprite = AnimatedSprite(pet_frames, screen_width // 2, screen_height // 2 + 100)
baby_komodo_sprite = AnimatedSprite(baby_komodo_frames, screen_width // 2, screen_height // 2 + 100)
all_sprites = pygame.sprite.Group()

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
petEgg_surface = pygame.transform.scale(petEgg_surface, (250, 250))  # Scale to 100x100 pixels

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

    screen.fill((0, 0, 0))  # Clear the screen with a black color

    # Blit the background image
    screen.blit(background_image, (0, 0))

    # Place four surfaces evenly across the screen for the food, water, play, and sleep features
    for i, surface in enumerate(surfaces):
        x_position = spacing * (i + 1) - surface.get_width() // 2
        y_position = screen_height // 8 - surface.get_height() // 2  # Position closer to the top
        screen.blit(surface, (x_position, y_position))

    # Update the age of the pet every 1 minute (60000 milliseconds)
    now = pygame.time.get_ticks()
    if now - last_age_update >= 1000: # Change back to 60000
        pet_age += 1
        last_age_update = now
        print(f"Pet age: {pet_age} years")

    # Render the age text
    age_text = test_font.render(f"Pet age: {pet_age} years", True, (255, 255, 255))
    screen.blit(age_text, (10, 10))  # Position the text at the top-left corner

    # FIXME: make if-else statement backwards
    # Display the egg image if the pet's age is less than 1
    all_sprites.empty()  # Clear all sprites from the group

    if pet_age < 1:
        screen.blit(petEgg_surface, (screen_width // 2 - petEgg_surface.get_width() // 2, screen_height // 2 - petEgg_surface.get_height() // 2))
    elif pet_age >= 1 and pet_age < 10:
        all_sprites.add(baby_komodo_sprite)
        all_sprites.update()
        all_sprites.draw(screen)
    elif pet_age >= 10 and pet_age < 20:
        print("Pet is now a teenager!")
        all_sprites.add(teenage_sprite)
        all_sprites.update()
        all_sprites.draw(screen)
    elif pet_age >= 20 and pet_age <= 30:
        print("Pet is now an adult!")
        # Add adult sprite handling here if needed
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

    # Update the display
    pygame.display.flip()
    clock.tick(60)  # Limit the frame rate to 60 FPS