import pygame
from sprites import (
    AnimatedSprite, EggSprite, ExplosionSprite, 
    get_max_flies, extract_frames
)
from utils import (
    get_hunger_interval, load_image, 
    generate_box_rects, create_fly
)
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BOX_COLORS,
    MENU, PLAYING, GAME_OVER
)

class Game:
    def __init__(self):
        self.game_state = MENU
        self.pet_age = 0
        self.pet_hunger = 100
        self.previous_pet_age = 0
        self.last_age_update = 0
        self.last_hunger_update = 0
        self.background_scroll = 0
        self.background_scroll_speed = 1
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.fly_sprites = pygame.sprite.Group()
        self.explosion_sprites = pygame.sprite.Group()
        
        # Game sprites
        self.egg_sprite = None
        self.baby_komodo_sprite = None
        self.teenage_sprite = None
        self.old_komodo_sprite = None
        
        # Drag and drop
        self.dragging_fly = None
        
        # UI elements
        self.box_rects = generate_box_rects()
        
    def load_assets(self):
        # Load background
        self.background_image = load_image('graphics/background.png', (SCREEN_WIDTH, SCREEN_HEIGHT), False)
        
        # Load and create sprite frames
        self.load_sprite_frames()
        
        # Create sprite instances
        self.create_sprites()
        
    def load_sprite_frames(self):
        # Load sprite sheet for flies
        sprite_sheet = load_image('graphics/fly.png')
        
        # Extract and scale fly frames
        try:
            self.fly_frames = extract_frames(sprite_sheet, 32, 32, 4)
            self.fly_frames = [pygame.transform.scale(frame, (64, 64)) for frame in self.fly_frames]
        except ValueError as e:
            print(f"Error extracting frames: {e}")
            # Create placeholder fly frames if extraction fails
            self.fly_frames = []
            for _ in range(4):
                surf = pygame.Surface((32, 32), pygame.SRCALPHA)
                pygame.draw.circle(surf, (0, 0, 0), (16, 16), 8)
                self.fly_frames.append(surf)
        
        # Load teenage komodo frames
        teenage_frames = [
            load_image(f'graphics/midkomodowalking/komodoWalking{i}.png') for i in range(1, 5)
        ]
        self.teenage_frames = [pygame.transform.scale(frame, (250, 250)) for frame in teenage_frames]
        
        # Load baby komodo frames
        baby_komodo_frames = [
            load_image(f'graphics/Baby/babyKomodo{i}.png') for i in range(1, 5)
        ]
        self.baby_komodo_frames = [pygame.transform.scale(frame, (250, 250)) for frame in baby_komodo_frames]
        
        # Load old komodo frames
        old_komodo_frames = [
            load_image(f'graphics/oldkomodo/oldKomodo{i}.png') for i in range(1, 7)
        ]
        self.old_komodo_frames = [pygame.transform.scale(frame, (250, 250)) for frame in old_komodo_frames]
        
        # Load eating animation frames
        komodo_eating_frames = [
            load_image(f'graphics/midkomodoeating/komodoEating{i}.png') for i in range(1, 9)
        ]
        self.komodo_eating_frames = [pygame.transform.scale(frame, (250, 250)) for frame in komodo_eating_frames]
        
        baby_komodo_eating_frames = [
            load_image(f'graphics/baby/babyKomodoEating{i}.png') for i in range(1, 5)
        ]
        self.baby_komodo_eating_frames = [pygame.transform.scale(frame, (250, 250)) for frame in baby_komodo_eating_frames]
        
        old_komodo_eating_frames = [
            load_image(f'graphics/oldKomodoEating{i}.png') for i in range(1, 3)
        ]
        self.old_komodo_eating_frames = [pygame.transform.scale(frame, (250, 250)) for frame in old_komodo_eating_frames]
        
        # Load egg frames
        try:
            egg_frames = [
                load_image(f'graphics/egg/komodoEgg{i}.png') for i in range(1, 4)
            ]
            print("Egg frames loaded successfully:")
            for i, frame in enumerate(egg_frames):
                print(f"Frame {i}: size={frame.get_size()}")
            
            self.egg_frames = [pygame.transform.scale(frame, (250, 250)) for frame in egg_frames]
        except Exception as e:
            print(f"Error loading egg frames: {e}")
            # Create placeholder egg frames
            self.egg_frames = []
            base_egg = pygame.Surface((250, 250), pygame.SRCALPHA)
            pygame.draw.ellipse(base_egg, (255, 255, 200), (50, 50, 150, 200))  # Base egg shape
            
            self.egg_frames.append(base_egg.copy())  # Frame 1: intact egg
            
            crack_egg = base_egg.copy()
            pygame.draw.line(crack_egg, (0, 0, 0), (100, 100), (150, 150), 3)  # Frame 2: egg with crack
            self.egg_frames.append(crack_egg)
            
            hatching_egg = base_egg.copy()
            pygame.draw.polygon(hatching_egg, (0, 0, 0), [(80, 80), (120, 70), (160, 90), (170, 130)], 3)  # Frame 3: egg hatching
            self.egg_frames.append(hatching_egg)
            
            print("Created placeholder egg frames")
        
    def create_sprites(self):
        # Create animated sprites
        self.teenage_sprite = AnimatedSprite(self.teenage_frames, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
        self.teenage_sprite.eating_frames = self.komodo_eating_frames
        
        self.baby_komodo_sprite = AnimatedSprite(self.baby_komodo_frames, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
        self.baby_komodo_sprite.eating_frames = self.baby_komodo_eating_frames
        
        self.old_komodo_sprite = AnimatedSprite(self.old_komodo_frames, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
        self.old_komodo_sprite.eating_frames = self.old_komodo_eating_frames
        
        # Create egg sprite
        print("Creating new egg sprite during game initialization")
        self.egg_sprite = EggSprite(self.egg_frames, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
        self.all_sprites.add(self.egg_sprite)
        
    def reset_game(self):
        self.previous_pet_age = 0
        self.pet_age = 0
        self.pet_hunger = 100
        self.game_state = PLAYING
        
        # Set up the time values for age/hunger updates
        current_time = pygame.time.get_ticks()
        self.last_age_update = current_time + 5000  # 5 second delay before first age increment
        self.last_hunger_update = current_time
        
        # Create a new egg sprite
        print("Creating new egg sprite during game reset")
        self.egg_sprite = EggSprite(self.egg_frames, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
        
        # Clear all sprites and add the new egg sprite
        self.all_sprites.empty()
        self.all_sprites.add(self.egg_sprite)
        
        # Clear existing flies and create new ones
        self.fly_sprites.empty()
        max_flies = get_max_flies(self.pet_age)
        for _ in range(max_flies):
            create_fly(self.fly_frames, self.fly_sprites, self.pet_age, max_flies)
        
        # Clear any existing explosions
        self.explosion_sprites.empty()
        
    def update(self):
        now = pygame.time.get_ticks()
        
        # Update background scroll
        self.background_scroll -= self.background_scroll_speed
        if self.background_scroll <= -SCREEN_WIDTH:
            self.background_scroll = 0
            
        # Only update game logic if in PLAYING state
        if self.game_state == PLAYING:
            # Store the previous age to detect transitions
            self.previous_pet_age = self.pet_age
            
            # Check if egg has just hatched - trigger immediate transition
            if self.pet_age == 0 and self.egg_sprite.animation_completed:
                if self.egg_sprite.just_hatched or now - self.last_age_update >= 1500:
                    # Force immediate transition to baby komodo
                    self.pet_age = 1
                    self.last_age_update = now
                    print(f"Egg hatched! Pet age advanced to {self.pet_age} years")
                    # Create an explosion effect at the egg position
                    explosion = ExplosionSprite(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
                    self.explosion_sprites.add(explosion)
            # Regular age updates for older pets
            elif now - self.last_age_update >= 3000:
                self.pet_age += 1
                self.last_age_update = now
                print(f"Pet age: {self.pet_age} years")
                
                # Check for transitions and create explosions
                if self.previous_pet_age < 10 and self.pet_age >= 10:
                    # Transition from baby to teenage
                    print("Transforming from baby to teenage komodo!")
                    explosion = ExplosionSprite(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
                    self.explosion_sprites.add(explosion)
                elif self.previous_pet_age < 20 and self.pet_age >= 20:
                    # Transition from teenage to old
                    print("Transforming from teenage to old komodo!")
                    explosion = ExplosionSprite(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
                    self.explosion_sprites.add(explosion)
            
            # Update the hunger level - only when the egg has hatched
            hunger_interval = get_hunger_interval(self.pet_age)
            if self.pet_age >= 1:  # Only decrease hunger if egg has hatched
                if now - self.last_hunger_update >= hunger_interval:
                    self.pet_hunger = max(0, self.pet_hunger - 10)
                    self.last_hunger_update = now
                    print(f"Pet hunger: {self.pet_hunger}%")
                    
                    # Check if pet has starved
                    if self.pet_hunger <= 0:
                        self.game_state = GAME_OVER
            else:
                # Ensure hunger stays at 100% while in egg stage
                self.pet_hunger = 100
                
            # Update active sprite based on age
            self.all_sprites.empty()
            
            if self.pet_age < 1:
                # Add egg sprite to be rendered
                self.all_sprites.add(self.egg_sprite)
            elif self.pet_age < 10:
                self.all_sprites.add(self.baby_komodo_sprite)
            elif self.pet_age < 20:
                self.all_sprites.add(self.teenage_sprite)
            else:
                self.all_sprites.add(self.old_komodo_sprite)
            
            # Update flies' pet_age to adjust their behavior
            for fly in self.fly_sprites:
                fly.update_pet_age(self.pet_age)
                
        # Update all sprite groups
        self.all_sprites.update()
        self.fly_sprites.update()
        self.explosion_sprites.update()
        
    def draw(self, screen):
        # Draw scrolling background
        screen.blit(self.background_image, (self.background_scroll, 0))
        screen.blit(self.background_image, (self.background_scroll + SCREEN_WIDTH, 0))
        
        # Draw all sprites
        self.all_sprites.draw(screen)
        self.fly_sprites.draw(screen)
        self.explosion_sprites.draw(screen)
        
    def handle_mouse_down(self, mouse_pos):
        if self.game_state == PLAYING:
            # Check if a fly is clicked
            for fly in self.fly_sprites:
                if fly.rect.collidepoint(mouse_pos):
                    self.dragging_fly = fly
                    fly.start_drag()
                    break
                    
    def handle_mouse_up(self, mouse_pos):
        if self.dragging_fly and self.game_state == PLAYING:
            # Check if the fly is dropped over the lizard
            current_lizard = None
            if self.pet_age < 1:
                # Use the animated egg sprite for collision detection
                if self.egg_sprite.rect.collidepoint(mouse_pos):
                    print("Fed the egg!")
                    self.pet_hunger = min(self.pet_hunger + 20, 100)
                    self.dragging_fly.kill()
                    # Only create a new fly if there are fewer than max allowed flies
                    max_flies = get_max_flies(self.pet_age)
                    if len(self.fly_sprites) < max_flies:
                        create_fly(self.fly_frames, self.fly_sprites, self.pet_age, max_flies)
                    self.dragging_fly = None
                    
                    # Trigger a shake effect when the egg is fed
                    self.egg_sprite.shake_amount = 5
            else:
                # Check which lizard sprite to use based on age
                if self.pet_age < 10:
                    current_lizard = self.baby_komodo_sprite
                    print("Baby komodo will eat")
                elif self.pet_age < 20:
                    current_lizard = self.teenage_sprite
                    print("Teenage komodo will eat")
                else:
                    current_lizard = self.old_komodo_sprite
                    print("Old komodo will eat")
                
                if current_lizard and current_lizard.rect.collidepoint(mouse_pos):
                    print(f"Fed the lizard! (Age: {self.pet_age})")
                    # Explicitly trigger eating animation with debug
                    current_lizard.start_eating()
                    self.pet_hunger = min(self.pet_hunger + 20, 100)
                    self.dragging_fly.kill()
                    # Create a new fly to replace the eaten one if not exceeding max
                    max_flies = get_max_flies(self.pet_age)
                    if len(self.fly_sprites) < max_flies:
                        create_fly(self.fly_frames, self.fly_sprites, self.pet_age, max_flies)
                    self.dragging_fly = None
            
            # If not dropped on lizard, return fly to original position
            if self.dragging_fly:
                self.dragging_fly.stop_drag()
                self.dragging_fly = None
                
    def handle_mouse_motion(self, mouse_pos):
        # Update dragged fly position
        if self.dragging_fly:
            self.dragging_fly.update_drag_position(mouse_pos)