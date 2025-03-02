    hunger_text_width = hunger_text.get_width()

    # Calculate position (screen width - text width - margin)
    hunger_text_x = screen.get_width() - hunger_text_width - 10

    # Display the text
    screen.blit(hunger_text, (hunger_text_x, 10))