import pygame
import random
import sys
from question_manager import QuestionManager
from button import SimpleButton

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# --- CYBERPUNK PALETTE ---
BG_COLOR = (5, 5, 12)           # Very Dark Blue/Black
NEON_GREEN = (0, 255, 65)       # Matrix Green
NEON_PINK = (255, 0, 110)       # Cyber Pink
NEON_BLUE = (0, 243, 255)       # Tron Blue
NEON_YELLOW = (255, 230, 0)     # Cyber Yellow (Score)
NEON_RED = (255, 50, 50)        # Danger Red
WHITE_GLOW = (220, 240, 255)    # Text
GREY_PASSIVE = (60, 60, 70)     # Passive UI

# Setup Display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mind Defender")
clock = pygame.time.Clock()

# Load Fonts
def get_font(size, bold=False):
    # Trying specific fonts first
    fonts = ["Consolas", "Courier New", "Lucida Console", "Fira Code", "Roboto Mono"]
    for f in fonts:
        if f in pygame.font.get_fonts(): 
            return pygame.font.SysFont(f, size, bold=bold)
    
    # Fallback
    return pygame.font.SysFont("arial", size, bold=bold)

font_small = get_font(18)   # For buttons
font_medium = get_font(28, bold=True) # For questions/inputs (slightly smaller to fit frames)
font_large = get_font(60, bold=True)

# --- VISUAL EFFECTS CLASSES ---

class MatrixRain:
    def __init__(self):
        self.drops = []
        self.columns = WIDTH // 15
        for i in range(self.columns):
            self.drops.append({
                'x': i * 15,
                'y': random.randint(-HEIGHT, 0),
                'speed': random.randint(3, 8),
                'chars': [str(random.randint(0, 1)) for _ in range(5)], # Trail of chars
                'alpha': random.randint(20, 80) # Very faint
            })
            
    def update(self):
        for drop in self.drops:
            drop['y'] += drop['speed']
            # Randomly change characters
            if random.random() < 0.1:
                drop['chars'] = [str(random.randint(0, 1)) for _ in range(5)]
                
            if drop['y'] > HEIGHT + 100:
                drop['y'] = random.randint(-200, -50)
                drop['speed'] = random.randint(3, 8)

    def draw(self, surface):
        # To optimize, we don't draw every char in the trail, just a lead and fading tail
        # or just simple low-opacity text for the 'feeling'
        for drop in self.drops:
            # Draw the stream
            color = (0, 255, 0) # Green base
            # Create a localized surface for alpha if needed, or just use colored text
            # Since we want it faint:
            # We map alpha 20-80 to RGB brightness for simple performance on main surface
            # (0, alpha*2, 0) roughly
            
            brightness = drop['alpha'] * 2
            if brightness > 255: brightness = 255
            color = (0, brightness, 0)
            
            # Draw lead character
            char_surf = font_small.render(drop['chars'][0], True, color)
            surface.blit(char_surf, (drop['x'], drop['y']))
            
            # Simple trail visual (fading lines for performance instead of text stream)
            # pygame.draw.line(surface, (0, brightness//2, 0), (drop['x']+5, drop['y']), (drop['x']+5, drop['y']-30), 1)


class Enemy:
    def __init__(self, question, answer, speed=1.0):
        self.question = question
        self.answer = answer
        self.speed = speed
        self.x = 0 # assigned later
        self.y = -60
        self.color = random.choice([NEON_GREEN, NEON_PINK, NEON_BLUE])
        
        # Pre-render text
        self.text_surf = font_medium.render(self.question, True, WHITE_GLOW)
        self.rect = self.text_surf.get_rect()
        # Inflate for frame
        self.rect.inflate_ip(30, 20)
        
    def update(self):
        self.y += self.speed
        self.rect.y = int(self.y)

    def draw(self, surface):
        # 1. Transparent Fill
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        r, g, b = self.color
        s.fill((r, g, b, 50)) # ~20% opacity
        surface.blit(s, (self.rect.x, self.rect.y))
        
        # 2. Main Border
        pygame.draw.rect(surface, self.color, self.rect, 2)
        
        # 3. Glow Border (faint outer)
        pygame.draw.rect(surface, self.color, self.rect.inflate(4, 4), 1)
        
        # 4. Text
        text_rect = self.text_surf.get_rect(center=self.rect.center)
        surface.blit(self.text_surf, text_rect)


# --- UI SETUP ---
# Colors
BTN_BASE = GREY_PASSIVE
BTN_HOVER = NEON_BLUE 
BTN_SELECTED = NEON_GREEN

cat_buttons = []
diff_buttons = []
CATEGORIES = ["matematik", "ingilizce", "almanca", "baskentler", "tarih"]
DIFFICULTIES = ["dinamik", "kolay", "orta", "zor"]

# Dynamic Layout Calculation
total_categories = len(CATEGORIES)
margin_x = 20
total_width = WIDTH - (margin_x * 2)
# Gap between buttons
gap = 10
# Calculate button width: (Total Space - (Total Gaps)) / Count
btn_width = (total_width - (gap * (total_categories - 1))) // total_categories
# Ensure it's not too small or big
btn_width = max(100, min(150, btn_width))

# Align center
total_block_width = (btn_width * total_categories) + (gap * (total_categories - 1))
start_x = (WIDTH - total_block_width) // 2

for i, cat in enumerate(CATEGORIES):
    x_pos = start_x + (i * (btn_width + gap))
    btn = SimpleButton(x_pos, 250, btn_width, 45, cat.upper(), font_small, BTN_BASE, BTN_HOVER, BTN_SELECTED)
    if i == 0: btn.is_selected = True
    cat_buttons.append(btn)

# Diff Buttons Layout
total_diffs = len(DIFFICULTIES)
btn_width_diff = 160
total_block_width_diff = (btn_width_diff * total_diffs) + (gap * (total_diffs - 1))
start_x_diff = (WIDTH - total_block_width_diff) // 2

for i, diff in enumerate(DIFFICULTIES):
    x_pos = start_x_diff + (i * (btn_width_diff + gap))
    btn = SimpleButton(x_pos, 330, btn_width_diff, 45, diff.upper(), font_small, BTN_BASE, BTN_HOVER, BTN_SELECTED)
    if i == 0: btn.is_selected = True
    diff_buttons.append(btn)

# Start Button - Sized normally
play_button = SimpleButton((WIDTH - 200)//2, 450, 200, 60, "BAŞLAT [ENTER]", font_medium, BTN_BASE, NEON_PINK, NEON_PINK)

# --- GLOBAL STATE ---
qm = QuestionManager()
matrix_bg = MatrixRain()

STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAMEOVER = 2
current_state = STATE_MENU

selected_cat_idx = 0
selected_diff_idx = 0

enemies = []
user_text = ""
score = 0
lives = 3
spawn_interval = 2000
wrong_answer_feedback = 0

SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, spawn_interval)

def get_difficulty(current_score, selected_mode):
    if selected_mode != "dinamik":
        return selected_mode
    if current_score < 50: return "kolay"
    elif current_score < 150: return "orta"
    else: return "zor"

def reset_game():
    global score, lives, enemies, user_text, spawn_interval
    score = 0
    lives = 3
    enemies = []
    user_text = ""
    spawn_interval = 2000
    pygame.time.set_timer(SPAWN_EVENT, spawn_interval)

def draw_background():
    screen.fill(BG_COLOR)
    matrix_bg.update()
    matrix_bg.draw(screen)

def draw_menu():
    draw_background()
    
    # Title
    title_text = "MIND DEFENDER"
    # Faint glow backing
    glow = font_large.render(title_text, True, (0, 50, 0))
    # Main title
    title = font_large.render(title_text, True, NEON_GREEN)
    
    cx = WIDTH//2
    # Draw glow offsets
    screen.blit(glow, (cx - title.get_width()//2 - 2, 100 - 2))
    screen.blit(glow, (cx - title.get_width()//2 + 2, 100 + 2))
    # Main
    screen.blit(title, (cx - title.get_width()//2, 100))
    
    # Section Labels
    # Use center alignment logic
    # pygame can't center easily without rects
    lbl_cat = font_small.render("- VERİ KATEGORİSİ -", True, (150, 200, 255))
    screen.blit(lbl_cat, (WIDTH//2 - lbl_cat.get_width()//2, 215))

    lbl_diff = font_small.render("- ZORLUK SEVİYESİ -", True, (150, 200, 255))
    screen.blit(lbl_diff, (WIDTH//2 - lbl_diff.get_width()//2, 305))

    mouse_pos = pygame.mouse.get_pos()
    
    for btn in cat_buttons:
        btn.check_hover(mouse_pos)
        btn.draw(screen)
    for btn in diff_buttons:
        btn.check_hover(mouse_pos)
        btn.draw(screen)
        
    play_button.check_hover(mouse_pos)
    play_button.draw(screen)

    pygame.display.flip()

def draw_game():
    draw_background()
    
    # Draw top header bar background
    header_surf = pygame.Surface((WIDTH, 60), pygame.SRCALPHA)
    header_surf.fill((10, 20, 40, 200)) # Semi-transparent dark blue
    screen.blit(header_surf, (0,0))
    pygame.draw.line(screen, NEON_BLUE, (0, 60), (WIDTH, 60), 2)

    # UI Stats
    # Score
    score_txt = font_medium.render(f"PUAN: {score}", True, NEON_YELLOW)
    screen.blit(score_txt, (20, 15))
    
    # Difficulty
    mode = DIFFICULTIES[selected_diff_idx]
    curr_diff = get_difficulty(score, mode).upper()
    diff_txt = font_medium.render(f"MOD: {curr_diff}", True, NEON_BLUE)
    screen.blit(diff_txt, (WIDTH//2 - diff_txt.get_width()//2, 15))
    
    # Lives (Draw hearts or just text)
    lives_txt = font_medium.render(f"CAN: {lives}", True, NEON_RED)
    screen.blit(lives_txt, (WIDTH - 140, 15))

    # Enemies
    for enemy in enemies:
        enemy.draw(screen)

    # Input Box Area
    input_box_height = 70
    input_y = HEIGHT - input_box_height - 20
    input_rect = pygame.Rect(WIDTH//2 - 300, input_y, 600, 50)
    
    # Box Fill
    fill_surf = pygame.Surface((input_rect.width, input_rect.height), pygame.SRCALPHA)
    fill_surf.fill((20, 30, 50, 200))
    screen.blit(fill_surf, input_rect.topleft)

    # Border Color
    if wrong_answer_feedback > 0:
        border_col = NEON_RED
        glow_col = (150, 0, 0)
    elif len(user_text) > 0:
        border_col = NEON_GREEN
        glow_col = (0, 100, 0)
    else:
        border_col = (100, 100, 120)
        glow_col = None

    pygame.draw.rect(screen, border_col, input_rect, 2, border_radius=5)
    
    if glow_col:
        pygame.draw.rect(screen, glow_col, input_rect.inflate(6,6), 1, border_radius=8)

    # Render User Text centered in box
    if len(user_text) > 0:
        text_surf = font_medium.render(user_text, True, WHITE_GLOW)
        text_rect = text_surf.get_rect(center=input_rect.center)
        screen.blit(text_surf, text_rect)
    else:
        # Placeholder
        ph_surf = font_medium.render("...", True, (80, 80, 100))
        ph_rect = ph_surf.get_rect(center=input_rect.center)
        screen.blit(ph_surf, ph_rect)

    pygame.display.flip()

def draw_gameover():
    # Overlay
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 150))
    screen.blit(s, (0,0))
    
    title = font_large.render("BAĞLANTI KESİLDİ", True, NEON_RED)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 100))
    
    info = font_medium.render(f"SONUÇ: {score} PUAN", True, NEON_YELLOW)
    screen.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT//2))
    
    sub = font_small.render("[R] YENİDEN BAĞLAN | [M] ANA MENÜ", True, WHITE_GLOW)
    screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 80))
    
    pygame.display.flip()


# Main Loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # STATE: MENU
        if current_state == STATE_MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                for i, btn in enumerate(cat_buttons):
                    if btn.check_click(mouse_pos):
                        selected_cat_idx = i
                        for b in cat_buttons: b.is_selected = False
                        btn.is_selected = True
                
                for i, btn in enumerate(diff_buttons):
                    if btn.check_click(mouse_pos):
                        selected_diff_idx = i
                        for b in diff_buttons: b.is_selected = False
                        btn.is_selected = True
                
                if play_button.check_click(mouse_pos):
                    reset_game()
                    current_state = STATE_PLAYING

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    reset_game()
                    current_state = STATE_PLAYING
        
        # STATE: PLAYING
        elif current_state == STATE_PLAYING:
            if event.type == SPAWN_EVENT:
                mode = DIFFICULTIES[selected_diff_idx]
                curr_diff = get_difficulty(score, mode)
                category = CATEGORIES[selected_cat_idx]
                
                qa = None
                for _ in range(5):
                    candidate_qa = qm.get_question(category, curr_diff)
                    if candidate_qa:
                        is_duplicate = False
                        for e in enemies:
                            if e.question == candidate_qa[0]:
                                is_duplicate = True
                                break
                        if not is_duplicate:
                            qa = candidate_qa
                            break
                
                if qa:
                    temp_text_surf = font_medium.render(qa[0], True, (255,255,255))
                    w, h = temp_text_surf.get_size()
                    w += 54
                    h += 24
                    
                    final_x = -1
                    for _ in range(10):
                        candidate_x = random.randint(20, WIDTH - 20 - w)
                        candidate_rect = pygame.Rect(candidate_x, -60, w, h)
                        collision = False
                        for e in enemies:
                            if candidate_rect.colliderect(e.rect):
                                collision = True
                                break
                        if not collision:
                            final_x = candidate_x
                            break
                    
                    if final_x != -1:
                        speed_multiplier = 1.0 + (score // 50) * 0.1
                        base_speed = random.uniform(0.5, 1.5)
                        final_speed = min(base_speed * speed_multiplier, 5.0)
                        
                        new_enemy = Enemy(qa[0], qa[1], final_speed)
                        new_enemy.x = final_x
                        new_enemy.rect.x = final_x 
                        
                        enemies.append(new_enemy)
                        
                        new_interval = max(600, 2000 - (score // 50) * 100)
                        if new_interval != spawn_interval:
                            spawn_interval = new_interval
                            pygame.time.set_timer(SPAWN_EVENT, spawn_interval)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Match Logic
                    matched_enemy = None
                    for enemy in enemies:
                        if user_text.strip().lower() == enemy.answer.lower():
                            matched_enemy = enemy
                            break
                    if matched_enemy:
                        enemies.remove(matched_enemy)
                        user_text = ""
                        score += 10
                    else:
                        if len(user_text) > 0: # Only punish if typed something
                             wrong_answer_feedback = 15
                             user_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                elif event.key == pygame.K_ESCAPE:
                    current_state = STATE_MENU
                else:
                    user_text += event.unicode
        
        elif current_state == STATE_GAMEOVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                    current_state = STATE_PLAYING
                elif event.key == pygame.K_m:
                    current_state = STATE_MENU

    # Loop updates
    if current_state == STATE_PLAYING:
        for enemy in enemies[:]:
            enemy.update()
            if enemy.y > HEIGHT - 90: # Hit area
                enemies.remove(enemy)
                lives -= 1
                if lives <= 0:
                    current_state = STATE_GAMEOVER
        if wrong_answer_feedback > 0:
            wrong_answer_feedback -= 1

    if current_state == STATE_MENU:
        draw_menu()
    elif current_state == STATE_PLAYING:
        draw_game()
    elif current_state == STATE_GAMEOVER:
        draw_gameover()

    clock.tick(FPS)

pygame.quit()
sys.exit()
