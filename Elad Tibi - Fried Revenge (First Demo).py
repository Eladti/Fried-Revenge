# Copyright (c) [2024] [Elad Tibi, BSC. ECE BGU]

import pygame
import random
import math
import time

pygame.init()


# -------------------------------- Hero Class -------------------------------------------

class Hero(pygame.sprite.Sprite):
    def __init__(self, x, y, potato_regular, potato_flip, bg1_rect, bg2_rect, screen_width):
        pygame.sprite.Sprite.__init__(self)
        self.potato_regular = potato_regular
        self.potato_flip = potato_flip
        self.current_image = potato_regular[0]
        self.current_rect = self.current_image.get_rect(topleft=(x, y))
        self.bg1_rect = bg1_rect
        self.bg2_rect = bg2_rect
        self.current_rect.center = (x, y)

        self.walk_state = 0
        self.screen_width = screen_width
        self.screen_height = 600
        self.animation_speed = 10
        self.animation_counter = 0

        self.fries_count = 0

        self.health = 100
        self.mana = 100

        self.last_attack_time = 0
        self.attack_recoil = 0.1
        self.potato_punch = potato_punch
        self.is_attacking = False

    def update(self, key):
        # Update animation counter and switch frame if needed
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.walk_state = (self.walk_state + 1) % len(self.potato_regular)
            self.animation_counter = 0

        if time.time() - self.last_attack_time > self.attack_recoil:
            self.is_attacking = False

        if key[pygame.K_d]:
            self.walk_right()  # Walking right
        elif key[pygame.K_a]:
            self.walk_left()  # Walking left
        elif key[pygame.K_w]:
            self.walk_up()  # Walking up
        elif key[pygame.K_s]:
            self.walk_down()  # Walking down

    def walk_right(self):
        # If the hero is not at the right edge, move the background
        if self.current_rect.right < self.screen_width - 1:
            self.bg1_rect.x -= 1
            self.bg2_rect.x -= 1
            self.current_rect.move_ip(2, 0)  # Move right
            self.current_image = self.potato_regular[self.walk_state]

    def walk_left(self):
        # If the hero is not at the left edge, move the background
        if self.current_rect.left > 0:
            self.bg1_rect.x += 1
            self.bg2_rect.x += 1
            self.current_rect.move_ip(-2, 0)  # Move left
            self.current_image = self.potato_flip[self.walk_state]

    def walk_up(self):
        self.current_rect.move_ip(0, -2)  # Move up
        self.current_image = self.potato_regular[self.walk_state]
        self.adjust_boundary()

    def walk_down(self):
        self.current_rect.move_ip(0, 2)  # Move down
        self.current_image = self.potato_regular[self.walk_state]
        self.adjust_boundary()

    def adjust_boundary(self):
        # Right boundary
        if self.current_rect.right > self.screen_width:
            self.current_rect.right = self.screen_width
        # Left boundary
        elif self.current_rect.left < 0:
            self.current_rect.left = 0
        # Upper boundary
        elif self.current_rect.top < 72:
            self.current_rect.top = 73
        # Lower boundary
        if self.current_rect.bottom > 535:
            self.current_rect.bottom = 534

    def attack(self, chefs):
        attack_radius = 40  # Radius within which chefs will be attacked
        current_time = time.time()  # Get the current time

        # Check if the recoil time has passed since the last attack
        if current_time - self.last_attack_time < self.attack_recoil:
            return  # If not enough time has passed, do nothing

        self.last_attack_time = current_time
        self.is_attacking = True

        for chef in chefs:
            # Calculate the distance between the hero and the chef
            dx = self.current_rect.centerx - chef.rect.centerx
            dy = self.current_rect.centery - chef.rect.centery
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance <= attack_radius:
                # If the chef is within the attack radius, reduce their health
                chef.health -= 10  # You can adjust the damage as needed

    def collect_fries(self):
        # Check if near any fries and "t" is pressed
        global fries_list  # Global fries object list
        for fries in fries_list:
            if self.current_rect.colliderect(fries.rect):
                if pygame.key.get_pressed()[pygame.K_t]:
                    self.fries_count += 1  # Increment the fries count
                    fries_list.remove(fries)  # Remove collected fries
                    return

    def draw(self, screen):
        if self.is_attacking:
            # If attacking, use the punch image
            screen.blit(self.potato_punch, self.current_rect.topleft)
        else:
            # Otherwise, use the current image (walking or idle)
            screen.blit(self.current_image, self.current_rect.topleft)

    def rect(self):
        return self.current_rect


# -------------------------------- Chefs Class -------------------------------------------

class Littlechef1(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.OGimage = pygame.image.load("Littlechef1.png")
        self.image = pygame.transform.scale(self.OGimage, (int(self.OGimage.get_width() / 6), int(self.OGimage.get_height() / 4)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 1

        self.health = 100
        self.mana = 100
        self.dead = False

        self.last_attack_time = time.time()
        self.attack_cooldown = 1

    def update(self, player_rect):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance != 0:
            self.rect.x += self.speed * dx / distance
            self.rect.y += self.speed * dy / distance

        if self.health <= 0 and not self.dead:
            self.dead = True
            fries = Fries(self.rect.centerx, self.rect.centery)
            fries_list.append(fries)

    def attack(self, hero):
        current_time = time.time()

        if current_time - self.last_attack_time < self.attack_cooldown:
            return

        dx = self.rect.centerx - hero.current_rect.centerx
        dy = self.rect.centery - hero.current_rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance <= 10:
            hero.health -= 5
            self.last_attack_time = current_time


class Littlechef2(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.OGimage = pygame.image.load("LittleChef3.png")
        self.image = pygame.transform.scale(self.OGimage, (int(self.OGimage.get_width() / 6), int(self.OGimage.get_height() / 4)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 1

        self.health = 100
        self.mana = 100
        self.dead = False

        self.last_attack_time = time.time()
        self.attack_cooldown = 0.8

    def update(self, player_rect):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance != 0:
            self.rect.x += self.speed * dx / distance
            self.rect.y += self.speed * dy / distance

        if self.health <= 0 and not self.dead:
            self.dead = True
            fries = Fries(self.rect.centerx, self.rect.centery)
            fries_list.append(fries)

    def attack(self, hero):
        current_time = time.time()

        if current_time - self.last_attack_time < self.attack_cooldown:
            return

        dx = self.rect.centerx - hero.current_rect.centerx
        dy = self.rect.centery - hero.current_rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance <= 10:
            hero.health -= 10
            self.last_attack_time = current_time


# -------------------------------- Fries Class -------------------------------------------
fries_list = []


class Fries(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.upper_fries = pygame.image.load("Upper_Fries.png")
        self.lower_fries = pygame.image.load("Lower_fries.png")
        self.current_image = self.upper_fries
        self.image = self.current_image
        self.rect = self.image.get_rect(center=(x, y))
        self.animation_counter = time.time()

    def update(self):
        current_time = time.time()
        if current_time - self.animation_counter >= 0.5:
            self.current_image = self.lower_fries if self.current_image == self.upper_fries else self.upper_fries
            self.animation_counter = current_time
            self.image = self.current_image


# ------------------------ New Game State and Level Transition ------------------------

def check_level_complete():
    global littlechefs1, fries_needed
    return len(littlechefs1) == 0 and hero.fries_count >= fries_needed


def transition_to_next_level():
    global current_level, screen_width, screen_height, bg1_rect, bg2_rect, littlechefs1
    current_level += 1

    hero.fries_count = 0
    hero.health = 100
    hero.current_rect.topleft = (20, 200)

    bg1_rect.topleft = (0, 0)
    bg2_rect.topleft = (bg1_rect.width, 0)

    littlechefs1 = []

    if current_level == 2:
        for _ in range(3):
            x = random.randint(abs((screen_width // 4) - screen_width), screen_width)
            y = random.randint(72, 475)
            chef = Littlechef2(x, y)
            littlechefs1.append(chef)

    if current_level == 3:
        return


# -------------------------------- Health and Mana bar -------------------------------------------

def draw_health_and_mana(screen, hero, chefs):
    grey_bar_height = 50
    grey_bar_y = screen.get_height() - grey_bar_height
    pygame.draw.rect(screen, (192, 192, 192), (0, grey_bar_y, screen.get_width(), grey_bar_height))

    icon_size = (30, 30)
    hero_icon = pygame.transform.scale(hero.current_image, icon_size)
    pygame.draw.rect(screen, (255, 0, 0), (50, grey_bar_y + 10, hero.health, 10))
    pygame.draw.rect(screen, (0, 0, 255), (50, grey_bar_y + 25, hero.mana, 10))
    screen.blit(hero_icon, (10, grey_bar_y + 10))

    bar_width = 100
    bar_height = 10
    bar_spacing = 15
    icon_offset = 40

    chef_x_positions = [150, 300, 450]

    for index, chef in enumerate(chefs):
        column_x = chef_x_positions[index]
        chef_icon = pygame.transform.scale(chef.image, icon_size)

        pygame.draw.rect(screen, (255, 0, 0), (column_x + icon_offset, grey_bar_y + 10, chef.health, bar_height))
        pygame.draw.rect(screen, (0, 0, 255), (column_x + icon_offset, grey_bar_y + 25, chef.mana, bar_height))

        screen.blit(chef_icon, (column_x, grey_bar_y + 10))


def reset_game():
    hero.health = 100
    hero.current_rect.topleft = (screen_width // 2, screen_height // 2)
    global current_level
    current_level = 1

    bg1_rect.topleft = (0, 0)
    bg2_rect.topleft = (bg1_rect.width, 0)

    global game_over, game_started
    game_over = False
    game_started = False

    for _ in range(3):
        x = random.randint(abs((screen_width // 4) - screen_width), screen_width)
        y = random.randint(140, 475)
        chef = Littlechef1(x, y)
        littlechefs1.append(chef)


# -------------------------------- Screen and Background Setup -------------------------------------------

game_world_width = 1600
screen_width = 800
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
background_image = pygame.image.load("Kitchen Background with Logo.png").convert()
welcome_background = pygame.image.load("Welcom_Background with logo.png").convert()
restart_background = pygame.image.load("Finish Background.png").convert()
potato_punch = pygame.image.load("Potato_punch.png").convert_alpha()

bg1_rect = background_image.get_rect(topleft=(0, 0))
bg2_rect = background_image.get_rect(topleft=(bg1_rect.width, 0))

bg3_rect = welcome_background.get_rect(topleft=(0, 0))
bg4_rect = welcome_background.get_rect(topleft=(bg1_rect.width, 0))

bg5_rect = restart_background.get_rect(topleft=(0, 0))
bg6_rect = restart_background.get_rect(topleft=(bg1_rect.width, 0))

door = pygame.image.load('Door.png').convert_alpha()
background_color = (255, 255, 255)
door.set_colorkey(background_color)
door_rect = door.get_rect(topleft=(400, 300))


# -------------------------------- Potatoes / Hero Images -------------------------------------------

potato1 = pygame.image.load("Potato man - regular.png").convert_alpha()
potato2 = pygame.image.load("Potato man regular 2.png").convert_alpha()

potato_flip1 = pygame.transform.flip(potato1, True, False)
potato_flip2 = pygame.transform.flip(potato2, True, False)

potato_regular = [potato1, potato2]
potato_flip_list = [potato_flip1, potato_flip2]

# -------------------------------- Obstacles -------------------------------------------

littlechefs1 = []
for _ in range(3):
    x = random.randint(abs((screen_width // 4) - screen_width), screen_width)
    y = random.randint(140, 475)
    chef = Littlechef1(x, y)
    littlechefs1.append(chef)

# -------------------------------- Colors and Variables -------------------------------------------

BG = (50, 50, 50)
clock = pygame.time.Clock()
pygame.mouse.set_visible(True)

current_level = 1
fries_needed = 3

hero = Hero(20, 200, potato_regular, potato_flip_list, bg1_rect, bg2_rect, screen_width)

button_width = 200
button_height = 50
button_color = (180, 120, 100)
button_text_color = (255, 255, 255)
RED_text = (190, 60, 30)
button_rect = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 95, button_width, button_height)
button_font = pygame.font.Font(None, 36)
button_text = button_font.render("Start Game", True, RED_text)
restart_button_text = button_font.render("Restart", True, RED_text)

lower_center = (screen_width // 2 - 70, screen_height // 2 + 110)
screen_center = (screen_width // 2 - 70, screen_height // 2 - 10)
welcome_center = (screen_width // 2 - 150, screen_height // 2 - 80)

reset_button_width = 150
reset_button_height = 50
reset_button_color = (211, 211, 211)
reset_button_text_color = (0, 0, 0)
reset_button_rect = pygame.Rect((screen_width - reset_button_width) // 2, (screen_height - reset_button_height) // 2, reset_button_width, reset_button_height)

restart_button_rect = pygame.Rect(550, 450, reset_button_width, reset_button_height)
restart_button_center = (580, 460)
reset_text = button_font.render("Restart Game", True, (0, 0, 0))

title_reset_text = button_font.render("You died avenging the fries", True, button_text_color)
reset_button_text = button_font.render("Again?", True, reset_button_text_color)
reset_button_center = (screen_width // 2 - 40, screen_height // 2 - 10)

# Game state variable
game_started = False
game_over = False
game_finished = False


# -------------------------------- Game Loop -------------------------------------------

run = True
while run:
    clock.tick(120)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos) and not game_started:
                game_started = True
            elif game_over and reset_button_rect.collidepoint(event.pos):
                reset_game()
            elif game_started and button_rect.collidepoint(event.pos):
                game_started = True
            elif game_finished and restart_button_rect.collidepoint(event.pos):
                game_finished = False
                reset_game()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                hero.attack(littlechefs1)

    if not game_started:
        screen.fill((0, 0, 0))
        screen.blit(welcome_background, bg3_rect.topleft)
        screen.blit(welcome_background, bg4_rect.topleft)
        pygame.draw.rect(screen, button_color, button_rect)
        screen.blit(button_text, lower_center)
    elif game_over:
        screen.fill((0, 0, 0))
        screen.blit(background_image, bg1_rect.topleft)
        screen.blit(background_image, bg2_rect.topleft)
        pygame.draw.rect(screen, reset_button_color, reset_button_rect)
        screen.blit(title_reset_text, welcome_center)
        screen.blit(reset_button_text, reset_button_center)
    elif game_finished:
        screen.fill((0, 0, 0))
        screen.blit(restart_background, bg5_rect.topleft)
        screen.blit(restart_background, bg6_rect.topleft)
        pygame.draw.rect(screen, (211, 211, 211), restart_button_rect)
        screen.blit(restart_button_text, restart_button_center)
    else:
        if hero.health <= 0:
            game_over = True
            screen.fill((0, 0, 0))
            pygame.draw.rect(screen, (211, 211, 211), reset_button_rect)
            reset_text = button_font.render("Reset Game", True, (0, 0, 0))
            screen.blit(reset_text, reset_button_rect.center)

        elif game_started and not game_over and not game_finished:
            if bg1_rect.right <= 0:
                bg1_rect.left = bg2_rect.right
            if bg2_rect.right <= 0:
                bg2_rect.left = bg1_rect.right
            if bg1_rect.left >= screen_width:
                bg1_rect.right = bg2_rect.left
            if bg2_rect.left >= screen_width:
                bg2_rect.right = bg1_rect.left

            screen.fill((0, 0, 0))
            screen.blit(background_image, bg1_rect.topleft)
            screen.blit(background_image, bg2_rect.topleft)

            if check_level_complete() and key[pygame.K_k] and door_rect.colliderect(hero.current_rect):
                transition_to_next_level()

            if current_level == 3:
                game_finished = True

            if check_level_complete():
                screen.blit(door, door_rect)

            key = pygame.key.get_pressed()
            hero.update(key)
            hero.draw(screen)

            for chef in littlechefs1:
                chef.update(hero.rect())
                screen.blit(chef.image, chef.rect)

            for chef in littlechefs1:
                chef.attack(hero)
                if chef.health <= 0:
                    littlechefs1.remove(chef)

            for fries in fries_list:
                fries.update()  # Call update to toggle animation
                screen.blit(fries.image, fries.rect)

            hero.collect_fries()

            draw_health_and_mana(screen, hero, littlechefs1)

            font = pygame.font.Font(None, 28)
            fries_text = f"Fries Retrieved: {hero.fries_count}"
            text_surface = font.render(fries_text, True, RED_text)
            screen.blit(text_surface, (625, screen.get_height() - 35))

    pygame.display.flip()

pygame.quit()