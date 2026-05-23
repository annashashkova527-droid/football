import pygame
import sys
import math
import random

# Инициализация Pygame и звука
pygame.init()
pygame.mixer.init()

# Размеры окна
WIDTH, HEIGHT = 1200, 700
FIELD_MARGIN = 50
GOAL_WIDTH = 150
PLAYER_RADIUS = 20
BALL_RADIUS = 10

# Цвета (синяя тема меню, зелёное поле)
DARK_BLUE = (20, 30, 70)
LIGHT_BLUE = (50, 80, 150)
GRASS_GREEN = (40, 120, 40)
GRASS_LIGHT = (60, 140, 60)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 50)
BLUE = (80, 120, 255)
RED = (255, 80, 80)
BLACK = (0, 0, 0)
PINK = (255, 180, 180)
ORANGE = (255, 140, 40)
GOLD = (255, 215, 0)

# Физические параметры
PLAYER_SPEED = 7
BALL_HIT_FORCE = 12
MAX_SPEED = 12
FRICTION = 0.98

# Статистика за сессию (сохраняется между матчами)
session_stats = {
    "games_played": 0,
    "left_wins": 0,
    "right_wins": 0,
    "ties": 0
}

# Стартовые позиции
LEFT_START_X = 150
RIGHT_START_X = WIDTH - 150
CENTER_Y = HEIGHT // 2

music_on = True  # Флаг включения музыки


# ---------------------- КЛАСС МЯЧА ----------------------
class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = BALL_RADIUS

    def reset(self):
        """Сброс мяча в центр с нулевой скоростью"""
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.vx = 0
        self.vy = 0

    def update(self):
        """Движение, трение, столкновение со стенами, ограничение скорости"""
        self.x += self.vx
        self.y += self.vy
        self.vx *= FRICTION
        self.vy *= FRICTION
        if abs(self.vx) < 0.1:
            self.vx = 0
        if abs(self.vy) < 0.1:
            self.vy = 0

        # Столкновения с границами поля
        if self.x - self.radius < FIELD_MARGIN:
            self.x = FIELD_MARGIN + self.radius
            self.vx = -self.vx * 0.95
        if self.x + self.radius > WIDTH - FIELD_MARGIN:
            self.x = WIDTH - FIELD_MARGIN - self.radius
            self.vx = -self.vx * 0.95
        if self.y - self.radius < FIELD_MARGIN:
            self.y = FIELD_MARGIN + self.radius
            self.vy = -self.vy * 0.95
        if self.y + self.radius > HEIGHT - FIELD_MARGIN:
            self.y = HEIGHT - FIELD_MARGIN - self.radius
            self.vy = -self.vy * 0.95

        # Ограничение максимальной скорости
        if abs(self.vx) > MAX_SPEED:
            self.vx = MAX_SPEED if self.vx > 0 else -MAX_SPEED
        if abs(self.vy) > MAX_SPEED:
            self.vy = MAX_SPEED if self.vy > 0 else -MAX_SPEED

    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x)-3, int(self.y)-3), 3)  # Блик


# ---------------------- КЛАСС ИГРОКА (ЧЕЛОВЕК) ----------------------
class Player:
    def __init__(self, x, y, color, keys_left, keys_right, keys_up, keys_down, name):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.color = color
        self.radius = PLAYER_RADIUS
        self.speed = PLAYER_SPEED
        self.keys = {'left': keys_left, 'right': keys_right, 'up': keys_up, 'down': keys_down}
        self.name = name
        self.score = 0

    def reset_position(self):
        """Возврат на стартовую позицию"""
        self.x = self.start_x
        self.y = self.start_y

    def update(self, keys_pressed, ball, all_players):
        """Движение игрока, удар по мячу, отталкивание от других игроков"""
        dx = dy = 0
        if keys_pressed[self.keys['left']]:
            dx = -self.speed
        if keys_pressed[self.keys['right']]:
            dx = self.speed
        if keys_pressed[self.keys['up']]:
            dy = -self.speed
        if keys_pressed[self.keys['down']]:
            dy = self.speed

        # Нормализация диагонали (чтобы по диагонали не бежать быстрее)
        if dx != 0 and dy != 0:
            dx /= 1.414
            dy /= 1.414

        new_x = self.x + dx
        new_y = self.y + dy
        if FIELD_MARGIN + self.radius <= new_x <= WIDTH - FIELD_MARGIN - self.radius:
            self.x = new_x
        if FIELD_MARGIN + self.radius <= new_y <= HEIGHT - FIELD_MARGIN - self.radius:
            self.y = new_y

        self.collide_ball(ball)

        # Отталкивание от других игроков
        for other in all_players:
            if other == self:
                continue
            dist = math.hypot(self.x - other.x, self.y - other.y)
            if dist < self.radius + other.radius:
                angle = math.atan2(self.y - other.y, self.x - other.x)
                overlap = (self.radius + other.radius) - dist
                self.x += math.cos(angle) * overlap
                self.y += math.sin(angle) * overlap

    def collide_ball(self, ball):
        """Удар по мячу (задаёт скорость и направление)"""
        dist = math.hypot(self.x - ball.x, self.y - ball.y)
        if dist < self.radius + ball.radius:
            angle = math.atan2(ball.y - self.y, ball.x - self.x)
            force = BALL_HIT_FORCE
            ball.vx = math.cos(angle) * force
            ball.vy = math.sin(angle) * force
            ball.vx += random.uniform(-2, 2)  # Случайный разброс
            ball.vy += random.uniform(-2, 2)
            spd = math.hypot(ball.vx, ball.vy)
            if spd > MAX_SPEED:
                ball.vx = ball.vx / spd * MAX_SPEED
                ball.vy = ball.vy / spd * MAX_SPEED
            overlap = (self.radius + ball.radius) - dist
            ball.x += math.cos(angle) * overlap
            ball.y += math.sin(angle) * overlap

    def draw(self, screen):
        """Отрисовка игрока (круг, глаза, румянец, улыбка)"""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 2)
        # Глаза
        pygame.draw.circle(screen, WHITE, (int(self.x)-8, int(self.y)-6), 6)
        pygame.draw.circle(screen, WHITE, (int(self.x)+8, int(self.y)-6), 6)
        pygame.draw.circle(screen, BLACK, (int(self.x)-7, int(self.y)-7), 3)
        pygame.draw.circle(screen, BLACK, (int(self.x)+9, int(self.y)-7), 3)
        pygame.draw.circle(screen, WHITE, (int(self.x)-9, int(self.y)-9), 2)
        pygame.draw.circle(screen, WHITE, (int(self.x)+7, int(self.y)-9), 2)
        # Румянец
        pygame.draw.circle(screen, PINK, (int(self.x)-12, int(self.y)-2), 4)
        pygame.draw.circle(screen, PINK, (int(self.x)+12, int(self.y)-2), 4)
        # Улыбка
        pygame.draw.arc(screen, BLACK, (int(self.x)-12, int(self.y)-2, 24, 14), 0, math.pi, 3)


# ---------------------- КЛАСС AI (НАСЛЕДНИК ИГРОКА) ----------------------
class AI(Player):
    def __init__(self, x, y, color, name, difficulty='medium'):
        super().__init__(x, y, color, None, None, None, None, name)
        self.difficulty = difficulty
        # Настройки скорости, силы и задержки реакции в зависимости от сложности
        if difficulty == 'Лёгкий':
            self.speed = 2
            self.strength = 0.3
            self.reaction_delay = 10
        elif difficulty == 'Средний':
            self.speed = 3.5
            self.strength = 0.6
            self.reaction_delay = 3
        else:  # Сложный
            self.speed = 5
            self.strength = 0.9
            self.reaction_delay = 0
        self.counter = 0

    def update(self, keys_pressed, ball, all_players):
        """Движение AI к мячу, удар с задержкой, отталкивание"""
        self.counter += 1
        dx = ball.x - self.x
        dy = ball.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx /= dist
            dy /= dist
        self.x += dx * self.speed
        self.y += dy * self.speed

        # Границы поля
        self.x = max(FIELD_MARGIN + self.radius, min(WIDTH - FIELD_MARGIN - self.radius, self.x))
        self.y = max(FIELD_MARGIN + self.radius, min(HEIGHT - FIELD_MARGIN - self.radius, self.y))

        if self.counter >= self.reaction_delay:
            self.counter = 0
            self.collide_ball_ai(ball)

        # Отталкивание от игроков
        for other in all_players:
            if other == self:
                continue
            dist = math.hypot(self.x - other.x, self.y - other.y)
            if dist < self.radius + other.radius:
                angle = math.atan2(self.y - other.y, self.x - other.x)
                overlap = (self.radius + other.radius) - dist
                self.x += math.cos(angle) * overlap
                self.y += math.sin(angle) * overlap

    def collide_ball_ai(self, ball):
        """Удар AI с ошибкой в зависимости от сложности"""
        dist = math.hypot(self.x - ball.x, self.y - ball.y)
        if dist < self.radius + ball.radius:
            # Всегда бьёт в сторону левых ворот (чужих)
            target_x = FIELD_MARGIN
            target_y = HEIGHT // 2
            angle = math.atan2(target_y - ball.y, target_x - ball.x)
            if self.difficulty == 'Лёгкий':
                angle += random.uniform(-0.5, 0.5)
            elif self.difficulty == 'Средний':
                angle += random.uniform(-0.2, 0.2)
            force = BALL_HIT_FORCE * self.strength
            ball.vx = math.cos(angle) * force
            ball.vy = math.sin(angle) * force
            ball.vx += random.uniform(-0.5, 0.5)
            ball.vy += random.uniform(-0.5, 0.5)
            spd = math.hypot(ball.vx, ball.vy)
            if spd > MAX_SPEED:
                ball.vx = ball.vx / spd * MAX_SPEED
                ball.vy = ball.vy / spd * MAX_SPEED
            overlap = (self.radius + ball.radius) - dist
            ball.x += math.cos(angle) * overlap
            ball.y += math.sin(angle) * overlap


# ---------------------- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ----------------------

def draw_field(screen):
    """Отрисовка поля: газон, полоски, линии, ворота с сеткой"""
    screen.fill(GRASS_GREEN)
    # Вертикальные полоски на газоне
    stripe_width = 60
    for x in range(0, WIDTH, stripe_width * 2):
        pygame.draw.rect(screen, GRASS_LIGHT, (x, 0, stripe_width, HEIGHT))
    
    # Линии поля
    pygame.draw.line(screen, WHITE, (WIDTH//2, FIELD_MARGIN), (WIDTH//2, HEIGHT - FIELD_MARGIN), 5)
    pygame.draw.circle(screen, WHITE, (WIDTH//2, HEIGHT//2), 60, 5)
    pygame.draw.rect(screen, WHITE, (FIELD_MARGIN, FIELD_MARGIN, WIDTH-2*FIELD_MARGIN, HEIGHT-2*FIELD_MARGIN), 5)
    
    # Ворота
    left_goal = pygame.Rect(FIELD_MARGIN-10, HEIGHT//2 - GOAL_WIDTH//2, 20, GOAL_WIDTH)
    right_goal = pygame.Rect(WIDTH - FIELD_MARGIN - 10, HEIGHT//2 - GOAL_WIDTH//2, 20, GOAL_WIDTH)
    pygame.draw.rect(screen, WHITE, left_goal, 4)
    pygame.draw.rect(screen, WHITE, right_goal, 4)
    
    # Сетка ворот
    for i in range(6):
        y = HEIGHT//2 - GOAL_WIDTH//2 + i * (GOAL_WIDTH // 5)
        pygame.draw.line(screen, WHITE, (FIELD_MARGIN-5, y), (FIELD_MARGIN-15, y), 2)
        pygame.draw.line(screen, WHITE, (WIDTH - FIELD_MARGIN + 5, y), (WIDTH - FIELD_MARGIN + 15, y), 2)


def check_goal(ball):
    """Проверка гола: 1 — левые ворота (забил правый), 2 — правые (забил левый)"""
    if (ball.x - ball.radius <= FIELD_MARGIN + 10 and
        HEIGHT//2 - GOAL_WIDTH//2 - 10 < ball.y < HEIGHT//2 + GOAL_WIDTH//2 + 10):
        return 2
    if (ball.x + ball.radius >= WIDTH - FIELD_MARGIN - 10 and
        HEIGHT//2 - GOAL_WIDTH//2 - 10 < ball.y < HEIGHT//2 + GOAL_WIDTH//2 + 10):
        return 1
    return 0


def draw_score(screen, left, right):
    """Отображение счёта с тенью"""
    font = pygame.font.Font(None, 80)
    text = font.render(f"{left} : {right}", True, WHITE)
    shadow = font.render(f"{left} : {right}", True, BLACK)
    screen.blit(shadow, (WIDTH//2 - text.get_width()//2 + 4, 24))
    screen.blit(text, (WIDTH//2 - text.get_width()//2, 20))


def draw_timer(screen, minutes, seconds):
    """Отображение таймера (оранжевый с тенью)"""
    font = pygame.font.Font(None, 50)
    timer_text = font.render(f"{minutes:02d}:{seconds:02d}", True, ORANGE)
    shadow = font.render(f"{minutes:02d}:{seconds:02d}", True, BLACK)
    screen.blit(shadow, (WIDTH//2 - 50 + 3, 83))
    screen.blit(timer_text, (WIDTH//2 - 50, 80))


def draw_speaker_icon(screen, rect, on):
    """Иконка динамика для управления музыкой (вкл/выкл по клику)"""
    pygame.draw.rect(screen, WHITE, rect, 2)
    if on:
        pygame.draw.line(screen, WHITE, (rect.x + 5, rect.y + 10), (rect.x + 5, rect.y + 20), 3)
        pygame.draw.line(screen, WHITE, (rect.x + 10, rect.y + 5), (rect.x + 10, rect.y + 25), 2)
        pygame.draw.line(screen, WHITE, (rect.x + 15, rect.y + 8), (rect.x + 15, rect.y + 22), 1)
        pygame.draw.arc(screen, WHITE, (rect.x + 18, rect.y + 8, 12, 14), -0.5, 0.5, 2)
        pygame.draw.arc(screen, WHITE, (rect.x + 22, rect.y + 5, 16, 20), -0.5, 0.5, 2)


# ---------------------- МЕНЮ, ИНСТРУКЦИЯ, СТАТИСТИКА ----------------------

def show_instructions(mode, difficulty):
    """Экран инструкции перед началом матча"""
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Инструкция")
    font_title = pygame.font.Font(None, 56)
    font_text = pygame.font.Font(None, 32)
    speaker_icon = pygame.Rect(WIDTH - 60, HEIGHT - 60, 40, 40)
    
    # Текст зависит от режима
    if mode == "1 vs 1":
        instructions = [
            "ИНСТРУКЦИЯ", "",
            f"Режим: {mode}", "",
            "Управление синим (левый): W, A, S, D",
            "Управление красным (правый): стрелки", "",
            "Общие клавиши:",
            "R - сбросить позиции",
            "M - главное меню",
            "ESC - выход", "",
            "Правила: матч до 5 голов или 3 минут", "",
            "Нажмите любую клавишу"
        ]
    else:
        instructions = [
            "ИНСТРУКЦИЯ", "",
            f"Режим: {mode}",
            f"Сложность: {difficulty}", "",
            "Управление синим (Вы): W, A, S, D",
            "Красный (AI) управляется компьютером", "",
            "Общие клавиши:",
            "R - сбросить позиции",
            "M - главное меню",
            "ESC - выход", "",
            "Правила: матч до 5 голов или 3 минут", "",
            "Нажмите любую клавишу"
        ]
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if speaker_icon.collidepoint(event.pos) and music_on is not False:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
            if event.type == pygame.KEYDOWN:
                waiting = False
        
        screen.fill(DARK_BLUE)
        # Рамка
        frame_rect = pygame.Rect(50, 50, WIDTH - 100, HEIGHT - 100)
        pygame.draw.rect(screen, LIGHT_BLUE, frame_rect)
        pygame.draw.rect(screen, WHITE, frame_rect, 3)
        
        y = 100
        for line in instructions:
            if line == "":
                y += 15
                continue
            if line == "ИНСТРУКЦИЯ":
                surf = font_title.render(line, True, ORANGE)
            elif "Режим" in line or "Сложность" in line:
                surf = font_text.render(line, True, ORANGE)
            else:
                surf = font_text.render(line, True, WHITE)
            screen.blit(surf, (WIDTH//2 - surf.get_width()//2, y))
            y += 40
        
        draw_speaker_icon(screen, speaker_icon, music_on and pygame.mixer.music.get_busy())
        pygame.display.flip()
        pygame.time.Clock().tick(30)


def choose_mode_and_difficulty():
    """Главное меню выбора режима и сложности"""
    global music_on
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Socxel Football - Выбор режима")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 48)
    font_title = pygame.font.Font(None, 72)
    
    speaker_icon = pygame.Rect(WIDTH - 60, HEIGHT - 60, 40, 40)
    options = ["1 vs 1 (два игрока)", "1 vs AI (выбор сложности)", "Выход"]
    difficulties = ["Лёгкий", "Средний", "Сложный"]
    selected = 0
    mode = None
    difficulty = "Средний"
    
    # Запуск фоновой музыки
    try:
        pygame.mixer.music.load("bg_music.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        music_on = True
    except:
        music_on = False
    
    while mode is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if speaker_icon.collidepoint(event.pos) and music_on is not False:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected == 0:
                        mode = "1 vs 1"
                    elif selected == 1:
                        d_sel = 1
                        while True:
                            screen.fill(DARK_BLUE)
                            for i, d in enumerate(difficulties):
                                color = ORANGE if i == d_sel else WHITE
                                txt = font.render(d, True, color)
                                screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 300 + i*60))
                            pygame.display.flip()
                            for e in pygame.event.get():
                                if e.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                                if e.type == pygame.KEYDOWN:
                                    if e.key == pygame.K_UP:
                                        d_sel = (d_sel - 1) % 3
                                    elif e.key == pygame.K_DOWN:
                                        d_sel = (d_sel + 1) % 3
                                    elif e.key == pygame.K_RETURN:
                                        difficulty = difficulties[d_sel]
                                        mode = "1 vs AI"
                                        return mode, difficulty
                            clock.tick(30)
                    else:
                        pygame.quit()
                        sys.exit()
        
        screen.fill(DARK_BLUE)
        # Рамка для названия
        title_rect = pygame.Rect(WIDTH//2 - 300, 60, 600, 90)
        pygame.draw.rect(screen, LIGHT_BLUE, title_rect)
        pygame.draw.rect(screen, WHITE, title_rect, 3)
        title = font_title.render("SOCXEL FOOTBALL", True, ORANGE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 85))
        
        # Пункты меню
        for i, opt in enumerate(options):
            color = ORANGE if i == selected else WHITE
            txt = font.render(opt, True, color)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 280 + i*70))
        
        draw_speaker_icon(screen, speaker_icon, music_on and pygame.mixer.music.get_busy())
        pygame.display.flip()
        clock.tick(30)
    
    return mode, difficulty


def show_statistics(stats):
    """Экран статистики после матча"""
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Статистика")
    font_title = pygame.font.Font(None, 60)
    font_text = pygame.font.Font(None, 40)
    font_small = pygame.font.Font(None, 30)
    speaker_icon = pygame.Rect(WIDTH - 60, HEIGHT - 60, 40, 40)
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if speaker_icon.collidepoint(event.pos) and music_on is not False:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
            if event.type == pygame.KEYDOWN:
                waiting = False
        
        screen.fill(DARK_BLUE)
        frame_rect = pygame.Rect(50, 50, WIDTH - 100, HEIGHT - 100)
        pygame.draw.rect(screen, LIGHT_BLUE, frame_rect)
        pygame.draw.rect(screen, WHITE, frame_rect, 3)
        
        title = font_title.render("СТАТИСТИКА", True, ORANGE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 90))
        
        lines = [
            f"Сыграно матчей: {stats['games_played']}",
            f"Побед левого игрока: {stats['left_wins']}",
            f"Побед правого игрока: {stats['right_wins']}",
            f"Ничьих: {stats['ties']}"
        ]
        y = 220
        for line in lines:
            surf = font_text.render(line, True, WHITE)
            screen.blit(surf, (WIDTH//2 - surf.get_width()//2, y))
            y += 70
        
        cont = font_small.render("Нажми любую клавишу", True, ORANGE)
        screen.blit(cont, (WIDTH//2 - cont.get_width()//2, HEIGHT - 130))
        
        draw_speaker_icon(screen, speaker_icon, music_on and pygame.mixer.music.get_busy())
        pygame.display.flip()
        pygame.time.Clock().tick(30)


# ---------------------- ГЛАВНАЯ ФУНКЦИЯ ----------------------
def main():
    global session_stats, music_on
    
    mode, difficulty = choose_mode_and_difficulty()
    show_instructions(mode, difficulty)
    
    speaker_icon = pygame.Rect(WIDTH - 60, HEIGHT - 60, 40, 40)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Socxel Arcade Football")
    clock = pygame.time.Clock()
    
    ball = Ball(WIDTH//2, HEIGHT//2)
    
    # Создание игроков в зависимости от режима
    if mode == "1 vs 1":
        player1 = Player(LEFT_START_X, CENTER_Y, BLUE,
                         pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, "Игрок 1")
        player2 = Player(RIGHT_START_X, CENTER_Y, RED,
                         pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, "Игрок 2")
        players = [player1, player2]
    else:
        human = Player(LEFT_START_X, CENTER_Y, BLUE,
                       pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, "Вы")
        ai = AI(RIGHT_START_X, CENTER_Y, RED, "AI", difficulty)
        players = [human, ai]
    
    score_left = 0
    score_right = 0
    start_ticks = pygame.time.get_ticks()
    match_duration = 180000  # 3 минуты в миллисекундах
    goal_limit = 5
    match_over = False
    winner_text = ""
    
    running = True
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if speaker_icon.collidepoint(event.pos) and music_on is not False:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r and not match_over:
                    ball.reset()
                    for p in players:
                        p.reset_position()
                if event.key == pygame.K_m and not match_over:
                    return
        
        if not match_over:
            elapsed = pygame.time.get_ticks() - start_ticks
            time_left = max(0, match_duration - elapsed)
            minutes = time_left // 60000
            seconds = (time_left // 1000) % 60
            
            # Проверка окончания матча
            if score_left >= goal_limit or score_right >= goal_limit or time_left <= 0:
                match_over = True
                session_stats["games_played"] += 1
                if score_left > score_right:
                    winner_text = "ПОБЕДИЛ ИГРОК 1 / ВЫ!"
                    session_stats["left_wins"] += 1
                elif score_right > score_left:
                    winner_text = "ПОБЕДИЛ ИГРОК 2 / AI!"
                    session_stats["right_wins"] += 1
                else:
                    winner_text = "НИЧЬЯ!"
                    session_stats["ties"] += 1
        
        # Экран окончания матча
        if match_over:
            draw_field(screen)
            ball.draw(screen)
            for p in players:
                p.draw(screen)
            draw_score(screen, score_left, score_right)
            
            font_win = pygame.font.Font(None, 60)
            win_surf = font_win.render(winner_text, True, ORANGE)
            win_shadow = font_win.render(winner_text, True, BLACK)
            screen.blit(win_shadow, (WIDTH//2 - win_surf.get_width()//2 + 3, HEIGHT//2 - 50 + 3))
            screen.blit(win_surf, (WIDTH//2 - win_surf.get_width()//2, HEIGHT//2 - 50))
            
            font_small = pygame.font.Font(None, 32)
            info_surf = font_small.render("Нажми любую клавишу для статистики...", True, WHITE)
            screen.blit(info_surf, (WIDTH//2 - info_surf.get_width()//2, HEIGHT//2 + 50))
            
            draw_speaker_icon(screen, speaker_icon, music_on and pygame.mixer.music.get_busy())
            pygame.display.flip()
            clock.tick(60)
            
            # Ожидание нажатия клавиши перед статистикой
            wait = True
            while wait:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        wait = False
                        show_statistics(session_stats)
                        return
            continue
        
        # Основной игровой цикл
        keys = pygame.key.get_pressed()
        for p in players:
            p.update(keys, ball, players)
        ball.update()
        
        # Проверка гола
        goal = check_goal(ball)
        if goal == 1:
            score_left += 1
            ball.reset()
            for p in players:
                p.reset_position()
        elif goal == 2:
            score_right += 1
            ball.reset()
            for p in players:
                p.reset_position()
        
        # Отрисовка всего
        draw_field(screen)
        ball.draw(screen)
        for p in players:
            p.draw(screen)
        draw_score(screen, score_left, score_right)
        draw_timer(screen, minutes, seconds)
        
        font_info = pygame.font.Font(None, 28)
        if mode == "1 vs 1":
            info = "Режим: 1 vs 1"
        else:
            info = f"Режим: Вы vs AI ({difficulty})"
        info += f"   Голов до: {goal_limit}"
        screen.blit(font_info.render(info, True, WHITE), (20, 20))
        
        draw_speaker_icon(screen, speaker_icon, music_on and pygame.mixer.music.get_busy())
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()


# ---------------------- ЗАПУСК ----------------------
if __name__ == "__main__":
    while True:
        main()
