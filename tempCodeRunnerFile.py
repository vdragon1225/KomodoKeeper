if active_sprite:
            if hasattr(active_sprite, 'is_eating') and active_sprite.is_eating:
                print(f"Active sprite is eating, frame: {active_sprite.current_frame}")
