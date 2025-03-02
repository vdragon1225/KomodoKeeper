import pygame
from sys import exit
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, MENU, PLAYING, GAME_OVER
from ui import (
    create_menu_buttons, create_game_over_buttons, 
    draw_menu, draw_game_over, draw_playing_ui
)
from utils import load_and_scale_logo, generate_box_rects
from game import Game

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