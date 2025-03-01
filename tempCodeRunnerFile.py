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
