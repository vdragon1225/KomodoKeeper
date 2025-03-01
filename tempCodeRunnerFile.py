if game_state == PLAYING:
            y_position = screen_height // 8 - surface.get_height() // 2  # Position closer to the top
            screen.blit(surface, (x_position, y_position))
