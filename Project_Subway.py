import os
import sys
import pygame
import random
import time

pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GREY = (211, 211, 211)

font = pygame.font.SysFont(None, 36)
title_font = pygame.font.SysFont(None, 72)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.font = font
        self.text_surf = self.font.render(self.text, True, BLACK)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_surf, self.text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) and self.action:
                self.action()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, sheet, columns, rows, speed):
        super().__init__()
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x = x
        self.y = y
        self.speed = speed

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.rect.width))
        self.rect.x = self.x
        self.rect.y = self.y
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]



class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, image, speed):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x = x
        self.y = y
        self.speed = speed

    def update(self):
        self.y += self.speed
        self.rect.y = self.y



class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, image, speed):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x = x
        self.y = y
        self.speed = speed

    def update(self):
        self.y += self.speed
        self.rect.y = self.y

def load_image(name, colorkey=None):
    fullname = os.path.join('resourse', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image

def check_collision(sprite1, sprite2):
    return pygame.sprite.collide_rect(sprite1, sprite2)

def start_game():
    global game_state, all_sprites, obstacles, coins, player, score, start_time, finish_time, level, SPAWN_RANGE
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    player = Player(SCREEN_WIDTH // 2 - 10, SCREEN_HEIGHT - 40, player_sheet, 2, 1, 3.4)
    all_sprites.add(player)
    score = 0
    start_time = time.time()
    finish_time = random.randint(30, 90)
    level = 1
    SPAWN_RANGE = 1500
    game_state = "running"

def next_level():
  global game_state, all_sprites, obstacles, coins, player, score, start_time, finish_time, level, SPAWN_RANGE
  all_sprites = pygame.sprite.Group()
  obstacles = pygame.sprite.Group()
  coins = pygame.sprite.Group()
  player = Player(SCREEN_WIDTH // 2 - 10, SCREEN_HEIGHT - 40, player_sheet, 2, 1, 3.4)
  all_sprites.add(player)
  score = 0
  start_time = time.time()
  finish_time = random.randint(30, 90)
  level += 1
  SPAWN_RANGE -=100
  game_state = "running"

def save_score(score, level):
    try:
        with open("highscores.txt", "a") as f:
            f.write(f"Результат: {score}, Уровень: {level}\n")
    except Exception as e:
        print(f"Ошика сохранения результата: {e}")


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
obstacle_images = [
    load_image("machine.png", -1),
    load_image("traktor.png", -1),
    load_image("vagon.png")
]
coin_image = load_image("moneta.png", -1)
obstacle_frequency = 50
coin_frequency = 75
coin_value = 50
all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
coins = pygame.sprite.Group()
pygame.display.set_caption("Subway Surfer")
player_sheet = pygame.transform.scale(load_image("pixilart.png", -1), (60, 30))
player = Player(SCREEN_WIDTH // 2 - 10, SCREEN_HEIGHT - 40, player_sheet, 2, 1, 3.4)
all_sprites.add(player)
clock = pygame.time.Clock()
game_state = "menu"
start_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 25, 200, 50,
                       "Start Game", GREEN, YELLOW, start_game)
title_text = title_font.render("SubWay", True, BLACK)
title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
running = True
SPAWN_RANGE = 1500
level = 1

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_state == "menu":
            start_button.handle_event(event)

    if game_state == "menu":
        screen.fill(WHITE)
        screen.blit(title_text, title_rect)
        start_button.draw(screen)
        pygame.display.flip()

    elif game_state == "running":
        screen.fill(GREY)
        player.update()
        if random.randrange(0, SPAWN_RANGE ) < obstacle_frequency:
            obstacle_image = random.choice(obstacle_images)
            obstacle_x = random.randrange(0, SCREEN_WIDTH - obstacle_image.get_width())
            obstacle_y = -obstacle_image.get_height()
            obstacle = Obstacle(obstacle_x, obstacle_y, obstacle_image, 2.2)
            can_spawn = True
            for other_obstacle in obstacles:
                if pygame.sprite.collide_rect(obstacle, other_obstacle):
                    can_spawn = False
                    break
            if can_spawn:
                obstacles.add(obstacle)
                all_sprites.add(obstacle)
        if random.randrange(0, SPAWN_RANGE) < coin_frequency:
            coin_x = random.randrange(0, SCREEN_WIDTH - 10)
            coin_y = -10
            coin = Coin(coin_x, coin_y, coin_image, 2.2)
            can_spawn = True
            for obstacle in obstacles:
                if check_collision(coin, obstacle):
                    can_spawn = False
                    break
            if can_spawn:
                coins.add(coin)
                all_sprites.add(coin)
        for sprite in all_sprites:
            sprite.update()
        collision = False
        for obstacle in obstacles:
            if check_collision(player, obstacle):
                collision = True
                break

        for coin in coins:
            if check_collision(player, coin):
                score += coin_value
                coin.kill()
                coins.remove(coin)
                all_sprites.remove(coin)


        current_time = time.time()
        time_up = (current_time - start_time) > finish_time

        if collision:
            game_state = "game_over"
        elif time_up:
            game_state = "win"

        all_sprites.draw(screen)

        score_text = font.render("Результат: " + str(score), True, BLACK)
        screen.blit(score_text, (10, 10))

        time_text = font.render("До окончания времени: " + str(round(finish_time - (current_time - start_time))), True, BLACK)
        screen.blit(time_text, (10, 40))

        level_text = font.render("Уровень: " + str(level), True, BLACK)
        screen.blit(level_text, (10, 70))

        pygame.display.flip()
        clock.tick(60)

    elif game_state == "game_over":
        screen.fill(WHITE)
        game_over_text = font.render("Поражение!", True, BLACK)
        score_text = font.render("Финальный Результат: " + str(score), True, BLACK)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(game_over_text, game_over_rect)
        screen.blit(score_text, score_rect)
        pygame.display.flip()
        save_score(score, level)
        time.sleep(3)
        game_state = "menu"

    elif game_state == "win":
      screen.fill(WHITE)
      win_text = font.render("Победа!", True, BLACK)
      win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
      screen.blit(win_text, win_rect)
      pygame.display.flip()
      time.sleep(3)
      save_score(score, level)
      next_level()

pygame.quit()




