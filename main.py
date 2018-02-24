from random import randint
from json import loads
import pygame
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
    def __init__(self, d, cnt, levels,level):
        super().__init__(cnt, cnt)
        self.gui = GUI()
        self.level = levels[level]['board']
        self.wall_coords=[]
        self.enemy_coords=[]
        for i in range(cnt):
            for j in range(cnt):
                if self.level[i][j]==1:
                    self.wall_coords.append([i,j])
                if self.level[i][j]==2:
                    self.exit_coords=[i,j]
                if self.level[i][j]==3:
                    self.enemy_coords.append([i,j])

        self.cell_size = int((d[1] - 20) / cnt)
        self.left = int((d[0] - self.cell_size * cnt) / 2)
        self.top = 10

        self.playercoord = (0, 0)
        self.player_group = pygame.sprite.Group()
        self.player = Player(self.player_group, self.cell_size, self.left+self.cell_size, self.top+self.cell_size)

        self.enemy_group=pygame.sprite.Group()
        for i in self.enemy_coords:
            self.enemy=Enemy(self.enemy_group, self.cell_size,  self.left+self.cell_size * i[1],self.top+self.cell_size * i[0])

        self.exit_group=pygame.sprite.Group()
        self.exit = Exit(self.exit_group, self.cell_size, self.left+self.cell_size * self.exit_coords[1],self.top+self.cell_size * self.exit_coords[0])

        self.wall_group=pygame.sprite.Group()
        for i in self.wall_coords:
            self.wall=Walls(self.wall_group, self.cell_size, self.left+self.cell_size * i[1],self.top+self.cell_size * i[0])

        self.isFinished = False #Is level finished
        self.GO=False


    def render(self, screen):
        super().render(screen)
        self.gui.render(screen)
        self.gui.update()
        if self.exit.update(self.player_group)==1:
            self.isFinished = True
        for i in self.enemy_group:
            if i.update(self.player_group) == 1:
                self.GO = True

        self.player_group.draw(screen)
        self.enemy_group.draw(screen)
        self.exit_group.draw(screen)
        self.wall_group.draw(screen)

    def on_click(self, cell_coords):
        if cell_coords:
            self.open_cell(*cell_coords)

    def on_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.player.get_event(self.wall_group)
            for i in self.enemy_group:
                i.get_event(self.wall_group)

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

    def get_event(self,group):
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
        self.enemies=[
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
        [pygame.transform.scale(load_image('slidan.png'), (d - 5, d)),
        pygame.transform.scale(load_image('slidan.png'), (d - 5, d))],
        [pygame.transform.scale(load_image('spider-left.png'), (d - 5, d)),
        pygame.transform.scale(load_image('spider-right.png'), (d - 5, d))]
        ]
        self.image = self.enemies[randint(0,7)][randint(0,1)]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.c=0

    def get_event(self,group):
        self.c=randint(0,4)
        if self.c==0:
            self.rect.y -= self.d
            if pygame.sprite.spritecollideany(self, group):
                self.rect.y += self.d
            self.c+=1
        elif self.c==1:
            self.rect.x += self.d
            if pygame.sprite.spritecollideany(self, group):
                self.rect.x -= self.d
            self.c+=1
        elif self.c==2:
            self.rect.y+=self.d
            if pygame.sprite.spritecollideany(self, group):
                self.rect.y -= self.d
            self.c+=1
        elif self.c==3:
            self.rect.x-=self.d
            if pygame.sprite.spritecollideany(self, group):
                self.rect.x += self.d
            self.c=0
    def update(self,group):
        if pygame.sprite.spritecollideany(self,group):
            return 1

class Exit(pygame.sprite.Sprite):

    def __init__(self, group,d, x, y):

        super().__init__(group)
        self.d = d
        self.image = pygame.transform.scale(load_image('Exit.png'), (d - 5, d))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self,group):
        if pygame.sprite.spritecollideany(self, group):
            return 1
class Walls(pygame.sprite.Sprite):
    def __init__(self, group,d, x, y):

        super().__init__(group)
        self.d = d
        self.image = pygame.transform.scale(load_image('Wall.png'), (d - 5, d))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

image = load_image('Intro.jpg')
image = pygame.transform.scale(image, d)
startScreen()
image = load_image(levels[0]['back'])

board = MainGameBoard(d, 15, levels,level)
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
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
        image = load_image('Intro.jpg')
        image = pygame.transform.scale(image, d)
        endScreen()
        running = False
        terminate()

    image = load_image(levels[level]['back'])
    image = pygame.transform.scale(image, d)
    screen.blit(image, (0, 0))

    board.render(screen)
    pygame.display.flip()
