import pygame

class SimpleButton:
    def __init__(self, x, y, width, height, text, font, base_color, hover_color, selected_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        # Text color for passive state (lighter grey for readability)
        self.text_color_passive = (180, 180, 180) 
        self.selected_color = selected_color if selected_color else hover_color
        self.is_selected = False
        self.current_color = base_color
        
        # Create surfaces for transparent fill
        self.surface_normal = pygame.Surface((width, height), pygame.SRCALPHA)
        self.surface_normal.fill((50, 50, 50, 30)) # Greyish, 12% opacity (30/255)
        
        self.surface_active = pygame.Surface((width, height), pygame.SRCALPHA)
        # We will set the active fill color dynamically in draw based on color, 
        # or simplified here to a generic tint. 
        # Let's handle dynamic color fill in draw for "neon" effect.

    def draw_glow_rect(self, surface, color, rect, radius=3):
        """Simulates a glow by drawing decreasingly opaque rectangles outwards"""
        # Inner fill (semi-transparent)
        fill_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        r, g, b = color
        fill_surf.fill((r, g, b, 50)) # 20% opacity fill
        surface.blit(fill_surf, rect.topleft)
        
        # Border
        pygame.draw.rect(surface, color, rect, 2, border_radius=8)
        
        # Outer Glow (faint lines)
        for i in range(1, radius + 1):
             alpha = 100 - (i * (100 // radius))
             if alpha < 0: alpha = 0
             # We can't draw direct alpha lines easily on main surface without a temp surface, 
             # but drawing thin lines works well enough for pixel art neon style.
             # Alternatively, just draw a wider rect with thinner width but it looks blocky.
             # Let's rely on the fill + bright border.
             pass

    def draw(self, screen):
        # Determine Color
        if self.is_selected:
            draw_color = self.selected_color
            fill_alpha = 60 # Higher opacity for selected
        elif self.current_color == self.hover_color:
            draw_color = self.hover_color
            fill_alpha = 40
        else:
            draw_color = self.base_color
            fill_alpha = 20

        # Create a temporary surface for the fill (to support alpha)
        fill_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        if self.is_selected or self.current_color == self.hover_color:
            # Active/Hover: Fill with tint of the draw_color
            r, g, b = draw_color
            fill_surf.fill((r, g, b, fill_alpha))
            screen.blit(fill_surf, self.rect.topleft)
            
            # Draw Border with nice solid color
            pygame.draw.rect(screen, draw_color, self.rect, 2, border_radius=8)
            
            # Simple Glow Effect: Draw a slightly larger, thinner rect
            glow_rect = self.rect.inflate(4, 4)
            pygame.draw.rect(screen, draw_color, glow_rect, 1, border_radius=10)
            
            text_col = draw_color # Scanline/Neon match
        else:
            # Passive: Grey fill
            fill_surf.fill((100, 100, 100, 15)) # Very faint grey fill
            screen.blit(fill_surf, self.rect.topleft)
            
            # Passive Border
            pygame.draw.rect(screen, (80, 80, 90), self.rect, 1, border_radius=8)
            text_col = self.text_color_passive

        # Draw text
        text_surf = self.font.render(self.text, True, text_col)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
        else:
            self.current_color = self.base_color

    def check_click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
