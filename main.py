from interval import Interval
from random import randint
from json import loads
import pygame
import time
import sys
import os

levels = loads(''.join(open("levels.json").readlines()))['levels']
level = 0
maxlevel = 3

pygame.init()

displayInfo = pygame.display.Info()
d = (displayInfo.current_w - 200, displayInfo.current_h - 200)

screen = pygame.display.set_mode(d)

pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 40)

# pygame.display.toggle_fullscreen()

inventory = {}
objects_paths = ['obj1.png','obj2.png','obj3.png','obj5.png','obj6.png']

healhs = {0:3, 1:0} #Big cludge! used only value


millis = lambda: int(round(time.time() * 1000))

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image


def terminate():
    pygame.quit()
    sys.exit()


def startScreen():
    introText = ["Иди к выходу"]

    screen.blit(image, (0, 0))
    font = pygame.font.Font(None, 30)
    textCoord = 300
    for line in introText:
        stringRendered = font.render(line, 1, pygame.Color('white'))
        introRect = stringRendered.get_rect()
        textCoord += 10
        introRect.top = textCoord
        introRect.x = textCoord
        textCoord += introRect.height
        screen.blit(stringRendered, introRect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()


def endScreen():
    introText = [""]

    screen.blit(image, (0, 0))
    font = pygame.font.Font(None, 300)
    textCoord = 0
    for line in introText:
        stringRendered = font.render(line, 1, pygame.Color('white'))
        introRect = stringRendered.get_rect()
        textCoord += 10
        introRect.top = textCoord
        introRect.x = textCoord
        textCoord += introRect.height
        screen.blit(stringRendered, introRect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
    return


class Label:
    def __init__(self, rect, text, fc=None, fh=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.bgcolor = pygame.Color("black")
        self.font_color = fc if fc else pygame.Color("white")
        self.font = pygame.font.Font(None, fh if fh else self.rect.height)
        self.rendered_text = None
        self.rendered_rect = None

    def render(self, surface):
        surface.fill(self.bgcolor, self.rect)
        self.rendered_text = self.font.render(self.text, 1, self.font_color)
        self.rendered_rect = self.rendered_text.get_rect(x=self.rect.x + 2, centery=self.rect.centery)
        surface.blit(self.rendered_text, self.rendered_rect)


class GUI:
    def __init__(self):
        self.elements = []

    def add_element(self, element):
        self.elements.append(element)

    def render(self, surface):
        for element in self.elements:
            element.render(surface)

    def update(self):
        for element in self.elements:
            update = getattr(element, "update", None)
            if callable(update):
                element.update()

    def get_event(self, event):
        for element in self.elements:
            get_event = getattr(element, "get_event", None)
            if callable(get_event):
                element.get_event(event)


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[-1 for _ in range(width)] for _ in range(height)]
        self.left = 10
        self.top = 10
        self.cell_size = 30

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        pass

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)

    def get_cell(self, mouse_pos):
        x, y = mouse_pos

        if x < self.left or x > (self.cell_size * self.width + self.left):
            return None
        if y < self.top or y > (self.cell_size * self.height + self.top):
            return None

        x = (x - self.left) // self.cell_size
        y = (y - self.top) // self.cell_size
        return y, x

    def on_click(self, cell_coords):
        pass


class MainGameBoard(Board):
    def __init__(self, d, cnt, levels, level):
        super().__init__(cnt, cnt)
        self.cnt = cnt
        self.gui = GUI()
        self.level = levels[level]['board']
        self.wall_coords = []
        self.enemy_coords = []
        for i in range(cnt):
            for j in range(cnt):
                if self.level[i][j] == 1:
                    self.wall_coords.append([i, j])
                if self.level[i][j] == 2:
                    self.exit_coords = [i, j]
                if self.level[i][j] == 3:
                    self.enemy_coords.append([i, j])

        self.cell_size = int((d[1] - 20) / cnt)
        self.left = int((d[0] - self.cell_size * cnt) / 2)
        self.top = 10

        self.playercoord = (0, 0)
        self.player_group = pygame.sprite.Group()
        self.player = Player(self.player_group, self.cell_size, self.left + self.cell_size, self.top + self.cell_size)

        self.exit_group = pygame.sprite.Group()
        self.exit = Exit(self.exit_group, self.cell_size, self.left + self.cell_size * self.exit_coords[1],
                         self.top + self.cell_size * self.exit_coords[0])

        self.wall_group = pygame.sprite.Group()
        for i in self.wall_coords:
            self.wall = Walls(self.wall_group, self.cell_size, self.left + self.cell_size * i[1],
                              self.top + self.cell_size * i[0])

        self.enemys = []
        self.intervals = []
        self.enemy_group = pygame.sprite.Group()
        f = 0
        for i in self.enemy_coords:
            self.enemys += [Enemy(self.enemy_group, self.cell_size, self.left + self.cell_size * i[1],
                                  self.top + self.cell_size * i[0])]
            self.intervals += [Interval(0.4, self.enemys[f].get_event, args=[self.wall_group, ])]
            self.intervals[f].start()
            f += 1

        self.objects_group = pygame.sprite.Group()
        self.objects = []
        for i in range(5):
            x, y = self.genrandpos()
            self.level[x][y] = 10
            self.objects += [Object(self.objects_group, self.cell_size, self.left + self.cell_size * x,
                                    self.top + self.cell_size * y, randint(0, len(objects_paths) - 1))]

        self.isFinished = False  # Is level finished
        self.GO = False
        self.lastkill = 0

    def genrandpos(self):
        x, y = 0, 0
        while True:
            x, y = randint(1, self.cnt - 1), randint(1, self.cnt - 1)
            if self.board[x][y] == -1 and self.level[x][y] == 0 and self.level[y][x] == 0:
                return x, y

    def render(self, screen):
        super().render(screen)
        self.gui.render(screen)
        self.gui.update()
        if self.exit.update(self.player_group) == 1:
            self.isFinished = True
        for i in self.enemy_group:
            if i.update(self.player_group) == 1:
                if (millis() - self.lastkill) > 800:
                    if 0 in inventory.keys():
                        inventory.pop(0)
                    else:
                        healhs[0] -= 1
                        if healhs[0] == 0:
                            self.GO = True
                        self.lastkill = millis()
        for e in self.objects:
            if e.update(self.player_group) == 1:
                self.objects.remove(e)
                if e.id in [0, 1, 2]:
                    inventory[e.id] = inventory.pop(e.id, 0) + 1
                else:
                    healhs[1] += 10 if e.id == 3 else 20
                e.remove(self.objects_group)

        self.player_group.draw(screen)
        self.enemy_group.draw(screen)
        self.exit_group.draw(screen)
        self.wall_group.draw(screen)
        self.objects_group.draw(screen)

        try:
            if self.isFinished:
                for i in range(len(self.intervals)):
                    self.intervals[i].stop()
        except Exception:
            pass

    def on_click(self, cell_coords):
        if cell_coords:
            pass

    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.player.get_event(self.wall_group)
            for o in self.objects:
                o.update(self.player_group)


class Player(pygame.sprite.Sprite):
    def __init__(self, group, d, x, y):
        super().__init__(group)
        self.d = d

        self.up = pygame.transform.scale(load_image('Up.png'), (d - 5, d))
        self.down = pygame.transform.scale(load_image('Down.png'), (d - 5, d))
        self.left = pygame.transform.scale(load_image('Left.png'), (d - 5, d))
        self.right = pygame.transform.scale(load_image('Right.png'), (d - 5, d))

        self.image = self.down
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def get_event(self, group):
        if (pygame.key.get_pressed()[pygame.K_UP] != 0):
            self.image = self.up
            self.rect.y -= self.d
            if pygame.sprite.spritecollideany(self, group):
                self.rect.y += self.d
        if (pygame.key.get_pressed()[pygame.K_DOWN] != 0):
            self.image = self.down
            self.rect.y += self.d
            if pygame.sprite.spritecollideany(self, group):
                self.rect.y -= self.d
        if (pygame.key.get_pressed()[pygame.K_LEFT] != 0):
            self.image = self.left
            self.rect.x -= self.d
            if pygame.sprite.spritecollideany(self, group):
                self.rect.x += self.d
        if (pygame.key.get_pressed()[pygame.K_RIGHT] != 0):
            self.image = self.right
            self.rect.x += self.d
            if pygame.sprite.spritecollideany(self, group):
                self.rect.x -= self.d


class Enemy(pygame.sprite.Sprite):
    def __init__(self, group, d, x, y):
        super().__init__(group)
        self.d = d
        self.enemies = [
            [pygame.transform.scale(load_image('buzz-left.png'), (d - 5, d)),
             pygame.transform.scale(load_image('buzz-right.png'), (d - 5, d))],
            [pygame.transform.scale(load_image('eye-left.png'), (d - 5, d)),
             pygame.transform.scale(load_image('eye-right.png'), (d - 5, d))],
            [pygame.transform.scale(load_image('ghoul-left.png'), (d - 5, d)),
             pygame.transform.scale(load_image('ghoul-right.png'), (d - 5, d))],
            [pygame.transform.scale(load_image('gob-left.png'), (d - 5, d)),
             pygame.transform.scale(load_image('gob-right.png'), (d - 5, d))],
            [pygame.transform.scale(load_image('mage-left.png'), (d - 5, d)),
             pygame.transform.scale(load_image('mage-right.png'), (d - 5, d))],
            [pygame.transform.scale(load_image('skeleton-left.png'), (d - 5, d)),
             pygame.transform.scale(load_image('skeleton-right.png'), (d - 5, d))],
            [pygame.transform.scale(load_image('spider-left.png'), (d - 5, d)),
             pygame.transform.scale(load_image('spider-right.png'), (d - 5, d))]
        ]
        self.image = self.enemies[randint(0, 6)][randint(0, 1)]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.c = 0
        self.d = -self.d if randint(0, 2) == 0 else self.d

    def get_event(self, group):
        if self.c == 0:
            self.rect.y -= self.d
            if pygame.sprite.spritecollideany(self, group):
                self.rect.y += self.d
            self.c += 1
        elif self.c == 1:
            self.rect.x += self.d
            if pygame.sprite.spritecollideany(self, group):
                self.rect.x -= self.d
            self.c += 1
        elif self.c == 2:
            self.rect.y += self.d
            if pygame.sprite.spritecollideany(self, group):
                self.rect.y -= self.d
            self.c += 1
        elif self.c == 3:
            self.rect.x -= self.d
            if pygame.sprite.spritecollideany(self, group):
                self.rect.x += self.d
            self.c = 0

    def update(self, group):
        if pygame.sprite.spritecollideany(self, group):
            return 1


class Exit(pygame.sprite.Sprite):

    def __init__(self, group, d, x, y):
        super().__init__(group)
        self.d = d
        self.image = pygame.transform.scale(load_image('Exit.png'), (d - 5, d))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, group):
        if pygame.sprite.spritecollideany(self, group):
            return 1


class Walls(pygame.sprite.Sprite):
    def __init__(self, group, d, x, y):
        super().__init__(group)
        self.d = d
        self.image = pygame.transform.scale(load_image('Wall.png'), (d - 5, d))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Object(pygame.sprite.Sprite):
    def __init__(self, group, d, x, y, id):
        super().__init__(group)
        self.d = d
        self.image = pygame.transform.scale(load_image(objects_paths[id]), (d - 5, d))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.id = id

    def update(self, group):
        if pygame.sprite.spritecollideany(self, group):
            return 1


class Inventory(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.image = pygame.transform.scale(load_image("inventory.png"), (222, 46))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, group):
        if pygame.sprite.spritecollideany(self, group):
            return 1

class InventoryItem(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.x, self.y = x, y
        self.image = pygame.transform.scale(load_image("tp.png"), (24, 26))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def set_id(self, id):
        self.image = pygame.transform.scale(load_image(objects_paths[id]), (24, 26))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self, group):
        if pygame.sprite.spritecollideany(self, group):
            return 1

health_paths = ["0.png", "1.png", "2.png", "3.png"]
class HealthBar(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.x, self.y = x, y
        self.image = pygame.transform.scale(load_image(health_paths[healhs[0]]), (54*2, 17*2))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def updatestate(self):
        self.image = pygame.transform.scale(load_image(health_paths[healhs[0]]), (54*2, 17*2))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y


class Score(pygame.sprite.Sprite):
    def __init__(self, group, x, y):
        super().__init__(group)
        self.x, self.y = x, y
        self.image = pygame.transform.scale(load_image("obj5.png"), (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

image = load_image('Intro.jpg')
image = pygame.transform.scale(image, d)
startScreen()
image = load_image(levels[0]['back'])

board = MainGameBoard(d, 15, levels, level)
running = True

inventory_group = pygame.sprite.Group()
inventory_sp = Inventory(inventory_group, 10, d[1] - 54)

inventoryitems_group = pygame.sprite.Group()
isprites = []
x = 20
for i in range(5):
    isprites += [InventoryItem(inventoryitems_group, x, d[1] - 48)]
    x += 44

healths_group = pygame.sprite.Group()
healths_sp = HealthBar(healths_group, d[0] - 135, 20)
score_sp = Score(healths_group, 6, 10)

def exit_game():
    for i in board.intervals:
        i.stop()
    running = False
    pygame.display.flip()
    image = load_image('Intro.jpg')
    image = pygame.transform.scale(image, d)
    endScreen()
    terminate()
    exit(0)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            for i in board.intervals:
                i.stop()
            terminate()
            exit(0)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            board.get_click(event.pos)
        board.on_event(event)
    screen.fill((0, 0, 0))

    if board.GO:
        image = load_image('Game_Over.png')
        image = pygame.transform.scale(image, d)
        endScreen()
        running = False
        terminate()
    if board.isFinished :
        board.isFinished = False
        level += 1
        if level!=maxlevel:
            board = MainGameBoard(d, 15, levels, level)
    if level == maxlevel:
        exit_game()

    idd = 0
    for i in sorted(list(inventory.keys())):
        isprites[idd].set_id(i)
        idd += 1

    image = load_image(levels[level]['back'])
    image = pygame.transform.scale(image, d)
    screen.blit(image, (0, 0))
    board.render(screen)

    inventory_group.draw(screen)
    inventoryitems_group.draw(screen)

    healths_group.draw(screen)
    healths_sp.updatestate()

    font = pygame.font.Font(None, 50)
    stringRendered = font.render(str(healhs[1]), 1, pygame.Color('red'))
    introRect = stringRendered.get_rect()
    introRect.top = 20
    introRect.left = 60
    screen.blit(stringRendered, introRect)

    pygame.display.flip()
