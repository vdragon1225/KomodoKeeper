if game_state == PLAYING:
        age_text = test_font.render(f"Pet age: {pet_age} years", True, (255, 255, 255))
        screen.blit(age_text, (10, 10))  # Position the text at the top-left corner
