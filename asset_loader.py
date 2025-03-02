import pygame
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AssetLoader:
    """
    A class to handle loading and managing game assets.
    This centralizes asset loading and provides error handling.
    """
    def __init__(self):
        self.images = {}
        self.animations = {}
        self.sounds = {}
        
    def load_image(self, name, path, scale=None, convert_alpha=True):
        """Load a single image and store it under the given name."""
        try:
            if convert_alpha:
                image = pygame.image.load(path).convert_alpha()
            else:
                image = pygame.image.load(path).convert()
            
            if scale:
                image = pygame.transform.scale(image, scale)
                
            self.images[name] = image
            logger.info(f"Loaded image: {name} from {path}")
            return image
        except Exception as e:
            logger.error(f"Failed to load image {name} from {path}: {e}")
            # Create a fallback surface
            if scale:
                fallback = pygame.Surface(scale, pygame.SRCALPHA)
            else:
                fallback = pygame.Surface((100, 100), pygame.SRCALPHA)
            # Fill with a noticeable pattern
            pygame.draw.rect(fallback, (255, 0, 255), fallback.get_rect(), 2)
            pygame.draw.line(fallback, (255, 0, 255), (0, 0), fallback.get_rect().bottomright, 2)
            pygame.draw.line(fallback, (255, 0, 255), (0, fallback.get_rect().bottom), (fallback.get_rect().right, 0), 2)
            
            self.images[name] = fallback
            return fallback
            
    def load_animation_frames(self, name, folder_path, filename_pattern, frame_count, scale=None):
        """Load a sequence of images to create an animation."""
        frames = []
        
        for i in range(1, frame_count + 1):
            frame_path = os.path.join(folder_path, f"{filename_pattern}{i}.png")
            frame_name = f"{name}_{i}"
            
            frame = self.load_image(frame_name, frame_path, scale)
            frames.append(frame)
            
        self.animations[name] = frames
        logger.info(f"Loaded animation: {name} with {frame_count} frames")
        return frames
        
    def load_sound(self, name, path):
        """Load a sound file and store it under the given name."""
        try:
            sound = pygame.mixer.Sound(path)
            self.sounds[name] = sound
            logger.info(f"Loaded sound: {name} from {path}")
            return sound
        except Exception as e:
            logger.error(f"Failed to load sound {name} from {path}: {e}")
            return None
            
    def get_image(self, name):
        """Retrieve a loaded image by name."""
        if name in self.images:
            return self.images[name]
        logger.warning(f"Image '{name}' not found in loader")
        return None
        
    def get_animation(self, name):
        """Retrieve a loaded animation by name."""
        if name in self.animations:
            return self.animations[name]
        logger.warning(f"Animation '{name}' not found in loader")
        return None
        
    def get_sound(self, name):
        """Retrieve a loaded sound by name."""
        if name in self.sounds:
            return self.sounds[name]
        logger.warning(f"Sound '{name}' not found in loader")
        return None
        
    def extract_frames_from_spritesheet(self, name, sheet_path, frame_width, frame_height, frame_count, scale=None):
        """Extract frames from a spritesheet and store them as an animation."""
        try:
            sprite_sheet = pygame.image.load(sheet_path).convert_alpha()
            sheet_width, sheet_height = sprite_sheet.get_size()
            
            frames = []
            for i in range(frame_count):
                rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                if rect.x + rect.width <= sheet_width and rect.y + rect.height <= sheet_height:
                    frame = sprite_sheet.subsurface(rect)
                    if scale:
                        frame = pygame.transform.scale(frame, scale)
                    frames.append(frame)
                else:
                    raise ValueError(f"Frame {i} outside sheet area. Sheet: {sheet_width}x{sheet_height}, Frame: {frame_width}x{frame_height}")
            
            self.animations[name] = frames
            logger.info(f"Extracted {frame_count} frames from spritesheet: {name}")
            return frames
        except Exception as e:
            logger.error(f"Failed to extract frames from spritesheet {name}: {e}")
            # Create placeholder frames
            frames = []
            for i in range(frame_count):
                size = scale if scale else (frame_width, frame_height)
                surf = pygame.Surface(size, pygame.SRCALPHA)
                pygame.draw.rect(surf, (255, 0, 255), surf.get_rect(), 2)
                pygame.draw.circle(surf, (255, 0, 255), (size[0]//2, size[1]//2), min(size[0], size[1])//4)
                frames.append(surf)
            
            self.animations[name] = frames
            return frames