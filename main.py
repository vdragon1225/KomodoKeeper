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
pet_surface = pygame.image.load('graphics/komodoEgg.png').convert_alpha()
pet_surface = pygame.transform.scale(pet_surface, (250, 250))  # Scale to 100x100 pixels

# Create surface for the left button
left_button_surface = pygame.Surface((50, 50))
left_button_surface.fill('Red')

#
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

    # Place four surfaces evenly across the screen for the food, water, play, and sleep features
    for i, surface in enumerate(surfaces):
        x_position = spacing * (i + 1) - surface.get_width() // 2
        y_position = screen_height // 8 - surface.get_height() // 2  # Position closer to the top
        screen.blit(surface, (x_position, y_position))

    # Place the pet in the center of the screen
    x_position = screen_width // 2 - pet_surface.get_width() // 2
    y_position = screen_height // 2 - pet_surface.get_height() // 2
    screen.blit(pet_surface, (x_position, y_position)) # Place the pet on the screen

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
