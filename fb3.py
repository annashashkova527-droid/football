# v1.0 - Socxel Football Game
import pygame
import sys
import math
import random

# Инициализация
pygame.init()

# Размеры экрана
WIDTH, HEIGHT = 1200, 700
FIELD_MARGIN = 50
GOAL_WIDTH = 150
PLAYER_RADIUS = 20
BALL_RADIUS = 10

# Цвета
DARK_GREEN = (0, 100, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (50, 50, 255)
RED = (255, 50, 50)
BLACK = (0, 0, 0)

# Физика
PLAYER_SPEED = 7
BALL_HIT_FORCE = 12
MAX_SPEED = 12
FRICTION = 0.98

# ----------------------------------------------------------------------
# Класс мяча
# ----------------------------------------------------------------------
class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = BALL_RADIUS

    def update(self):
        self.x += self.vx
        self.y += self.vy
        # трение
        self.vx *= FRICTION
        self.vy *= FRICTION
        if abs(self.vx) < 0.1:
            self.vx = 0
        if abs(self.vy) < 0.1:
            self.vy = 0

        # столкновение со стенами
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

        # ограничение максимальной скорости
        if abs(self.vx) > MAX_SPEED:
            self.vx = MAX_SPEED if self.vx > 0 else -MAX_SPEED
        if abs(self.vy) > MAX_SPEED:
            self.vy = MAX_SPEED if self.vy > 0 else -MAX_SPEED

    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x)-3, int(self.y)-3), 3)

# ----------------------------------------------------------------------
# Класс игрока (человек)
# ----------------------------------------------------------------------
class Player:
    def __init__(self, x, y, color, keys_left, keys_right, keys_up, keys_down, name):
        self.x = x
        self.y = y
        self.color = color
        self.radius = PLAYER_RADIUS
        self.speed = PLAYER_SPEED
        self.keys = {
            'left': keys_left,
            'right': keys_right,
            'up': keys_up,
            'down': keys_down
        }
        self.name = name
        self.score = 0

    def update(self, keys_pressed, ball, all_players):
        dx = dy = 0
        if keys_pressed[self.keys['left']]:
            dx = -self.speed
        if keys_pressed[self.keys['right']]:
            dx = self.speed
        if keys_pressed[self.keys['up']]:
            dy = -self.speed
        if keys_pressed[self.keys['down']]:
            dy = self.speed

        # нормализация диагонали
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

        # отталкивание от других игроков
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
        dist = math.hypot(self.x - ball.x, self.y - ball.y)
        if dist < self.radius + ball.radius:
            angle = math.atan2(ball.y - self.y, ball.x - self.x)
            force = BALL_HIT_FORCE
            ball.vx = math.cos(angle) * force
            ball.vy = math.sin(angle) * force
            ball.vx += random.uniform(-2, 2)
            ball.vy += random.uniform(-2, 2)
            spd = math.hypot(ball.vx, ball.vy)
            if spd > MAX_SPEED:
                ball.vx = ball.vx / spd * MAX_SPEED
                ball.vy = ball.vy / spd * MAX_SPEED
            overlap = (self.radius + ball.radius) - dist
            ball.x += math.cos(angle) * overlap
            ball.y += math.sin(angle) * overlap

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x)-7, int(self.y)-7), 4)
        pygame.draw.circle(screen, WHITE, (int(self.x)+7, int(self.y)-7), 4)
        pygame.draw.circle(screen, BLACK, (int(self.x)-7, int(self.y)-7), 2)
        pygame.draw.circle(screen, BLACK, (int(self.x)+7, int(self.y)-7), 2)

# ----------------------------------------------------------------------
# Класс AI
# ----------------------------------------------------------------------
class AI(Player):
    def __init__(self, x, y, color, name, difficulty='medium'):
        super().__init__(x, y, color, None, None, None, None, name)
        self.difficulty = difficulty
        if difficulty == 'easy':
            self.speed = 2
            self.strength = 0.3
            self.reaction_delay = 10
        elif difficulty == 'medium':
            self.speed = 3.5
            self.strength = 0.6
            self.reaction_delay = 3
        else:  # hard
            self.speed = 5
            self.strength = 0.9
            self.reaction_delay = 0
        self.counter = 0

    def update(self, keys_pressed, ball, all_players):
        self.counter += 1
        # движение к мячу
        dx = ball.x - self.x
        dy = ball.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx /= dist
            dy /= dist
        self.x += dx * self.speed
        self.y += dy * self.speed
        # границы
        self.x = max(FIELD_MARGIN + self.radius, min(WIDTH - FIELD_MARGIN - self.radius, self.x))
        self.y = max(FIELD_MARGIN + self.radius, min(HEIGHT - FIELD_MARGIN - self.radius, self.y))
        # удар с задержкой
        if self.counter >= self.reaction_delay:
            self.counter = 0
            self.collide_ball_ai(ball)
        # отталкивание
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
        dist = math.hypot(self.x - ball.x, self.y - ball.y)
        if dist < self.radius + ball.radius:
            target_x = FIELD_MARGIN
            target_y = HEIGHT // 2
            angle = math.atan2(target_y - ball.y, target_x - ball.x)
            if self.difficulty == 'easy':
                angle += random.uniform(-0.5, 0.5)
            elif self.difficulty == 'medium':
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

# ----------------------------------------------------------------------
# Вспомогательные функции: поле, гол, счёт, меню
# ----------------------------------------------------------------------
def draw_field(screen):
    screen.fill(DARK_GREEN)
    pygame.draw.line(screen, WHITE, (WIDTH//2, FIELD_MARGIN), (WIDTH//2, HEIGHT - FIELD_MARGIN), 3)
    pygame.draw.circle(screen, WHITE, (WIDTH//2, HEIGHT//2), 50, 3)
    pygame.draw.rect(screen, WHITE, (FIELD_MARGIN, FIELD_MARGIN, WIDTH-2*FIELD_MARGIN, HEIGHT-2*FIELD_MARGIN), 3)
    left_goal = pygame.Rect(FIELD_MARGIN-10, HEIGHT//2 - GOAL_WIDTH//2, 20, GOAL_WIDTH)
    right_goal = pygame.Rect(WIDTH - FIELD_MARGIN - 10, HEIGHT//2 - GOAL_WIDTH//2, 20, GOAL_WIDTH)
    pygame.draw.rect(screen, WHITE, left_goal, 3)
    pygame.draw.rect(screen, WHITE, right_goal, 3)

def check_goal(ball):
    # левые ворота (гол забивает правый игрок)
    if (ball.x - ball.radius <= FIELD_MARGIN + 10 and
        HEIGHT//2 - GOAL_WIDTH//2 - 10 < ball.y < HEIGHT//2 + GOAL_WIDTH//2 + 10):
        return 2
    # правые ворота (гол забивает левый игрок)
    if (ball.x + ball.radius >= WIDTH - FIELD_MARGIN - 10 and
        HEIGHT//2 - GOAL_WIDTH//2 - 10 < ball.y < HEIGHT//2 + GOAL_WIDTH//2 + 10):
        return 1
    return 0

def draw_score(screen, left, right):
    font = pygame.font.Font(None, 72)
    text = font.render(f"{left} : {right}", True, WHITE)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, 20))

def choose_mode_and_difficulty():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Socxel Football - Выбор режима")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 48)

    options = ["1 vs 1 (два игрока)", "1 vs AI (выбор сложности)", "Выход"]
    difficulties = ["Лёгкий", "Средний", "Сложный"]
    selected = 0
    mode = None
    difficulty = "medium"

    while mode is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected == 0:
                        mode = "1v1"
                    elif selected == 1:
                        d_sel = 1
                        while True:
                            screen.fill(BLACK)
                            for i, d in enumerate(difficulties):
                                color = YELLOW if i == d_sel else WHITE
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
                                        difficulty = ["easy", "medium", "hard"][d_sel]
                                        mode = "1vAI"
                                        return mode, difficulty
                            clock.tick(30)
                    else:
                        pygame.quit()
                        sys.exit()
        screen.fill(BLACK)
        for i, opt in enumerate(options):
            color = YELLOW if i == selected else WHITE
            txt = font.render(opt, True, color)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 250 + i*80))
        pygame.display.flip()
        clock.tick(30)

    return mode, difficulty

# ----------------------------------------------------------------------
# Основная игра
# ----------------------------------------------------------------------
def main():
    mode, difficulty = choose_mode_and_difficulty()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Socxel Arcade Football")
    clock = pygame.time.Clock()

    ball = Ball(WIDTH//2, HEIGHT//2)

    if mode == "1v1":
        player1 = Player(150, HEIGHT//2, BLUE,
                         pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, "Игрок 1")
        player2 = Player(WIDTH-150, HEIGHT//2, RED,
                         pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, "Игрок 2")
        players = [player1, player2]
    else:
        human = Player(150, HEIGHT//2, BLUE,
                       pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s, "Вы")
        ai = AI(WIDTH-150, HEIGHT//2, RED, "AI", difficulty)
        players = [human, ai]

    score_left = 0
    score_right = 0
    start_ticks = pygame.time.get_ticks()
    match_duration = 180000  # 3 минуты
    goal_limit = 5
    match_over = False
    winner_text = ""

    running = True
    while running:
        if not match_over:
            elapsed = pygame.time.get_ticks() - start_ticks
            time_left = max(0, match_duration - elapsed)
            minutes = time_left // 60000
            seconds = (time_left // 1000) % 60

            # проверка окончания матча
            if score_left >= goal_limit or score_right >= goal_limit or time_left <= 0:
                match_over = True
                if score_left > score_right:
                    winner_text = "Победил Игрок 1!"
                elif score_right > score_left:
                    winner_text = "Победил Игрок 2!"
                else:
                    winner_text = "Ничья!"
        else:
            # экран окончания игры
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    return  # по любой клавише выходим в меню
            # рисуем поле и победителя
            draw_field(screen)
            ball.draw(screen)
            for p in players:
                p.draw(screen)
            draw_score(screen, score_left, score_right)
            font = pygame.font.Font(None, 72)
            win_surf = font.render(winner_text, True, YELLOW)
            screen.blit(win_surf, (WIDTH//2 - win_surf.get_width()//2, HEIGHT//2 - 50))
            font_small = pygame.font.Font(None, 36)
            info_surf = font_small.render("Нажми любую клавишу для продолжения...", True, WHITE)
            screen.blit(info_surf, (WIDTH//2 - info_surf.get_width()//2, HEIGHT//2 + 50))
            pygame.display.flip()
            clock.tick(60)
            continue

        # основной игровой цикл (пока матч не окончен)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    ball.x, ball.y = WIDTH//2, HEIGHT//2
                    ball.vx, ball.vy = 0, 0
                if event.key == pygame.K_m:
                    return

        keys = pygame.key.get_pressed()
        for p in players:
            p.update(keys, ball, players)

        ball.update()

        goal = check_goal(ball)
        if goal == 1:
            score_left += 1
            ball.x, ball.y = WIDTH//2, HEIGHT//2
            ball.vx, ball.vy = 0, 0
        elif goal == 2:
            score_right += 1
            ball.x, ball.y = WIDTH//2, HEIGHT//2
            ball.vx, ball.vy = 0, 0

        draw_field(screen)
        ball.draw(screen)
        for p in players:
            p.draw(screen)
        draw_score(screen, score_left, score_right)

        # отображение таймера
        font_timer = pygame.font.Font(None, 40)
        timer_surf = font_timer.render(f"{minutes:02d}:{seconds:02d}", True, WHITE)
        screen.blit(timer_surf, (WIDTH//2 - 50, 80))

        # информация о режиме и лимите голов
        font_info = pygame.font.Font(None, 30)
        if mode == "1v1":
            info = "Режим: 1 vs 1"
        else:
            diff_name = {"easy":"Лёгкий", "medium":"Средний", "hard":"Сложный"}[difficulty]
            info = f"Режим: Вы vs AI ({diff_name})"
        info += f"   Голов до: {goal_limit}"
        screen.blit(font_info.render(info, True, WHITE), (20, 20))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

# ----------------------------------------------------------------------
# Запуск
# ----------------------------------------------------------------------
if __name__ == "__main__":
    while True:
        main()
