import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

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
    retry_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 50, "Retry", (0, 150, 0), (0, 200, 0))
    exit_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 70, 200, 50, "Exit", (150, 0, 0), (200, 0, 0))
    return retry_button, exit_button

# Draw the menu screen
def draw_menu(screen, logo_image, play_button, quit_button):
    # Draw a semi-transparent overlay to make text more readable
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # Semi-transparent black
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
    # Display game over message
    large_font = pygame.font.Font(None, 48)
    game_over_text = large_font.render("Game Over", True, (255, 0, 0))
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
    screen.blit(game_over_text, game_over_rect)
    
    # Display final stats
    test_font = pygame.font.Font(None, 24)
    final_age_text = test_font.render(f"Your pet lived to {pet_age} years old", True, (255, 255, 255))
    final_age_rect = final_age_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    screen.blit(final_age_text, final_age_rect)
    
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