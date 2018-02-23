import os
import pygame
import sys

d=(700,700)

pygame.init()
screen = pygame.display.set_mode(d)
player_group = pygame.sprite.Group()
sprites=pygame.sprite.Group()
running=True


def load_image(name, colorkey = None):
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
    sys.exit();

def startScreen():

    introText = ["Иди к выходу"]

    screen.blit(image, (0, 0));
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

    introText = ["Конец"]

    screen.blit(image, (0, 0));
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


class Player(pygame.sprite.Sprite):
    up = load_image('Up.png')
    down = load_image('Down.png')
    left = load_image('Left.png')
    right = load_image('Right.png')

    def __init__(self,group, x, y):
        super().__init__(group)
        self.image = self.up
        self.rect = self.image.get_rect()
        self.rect.x=x
        self.rect.y=y

    def get_event(self):
        if (pygame.key.get_pressed()[pygame.K_UP] != 0):
            self.image=self.up
            self.rect.y-=30
        if (pygame.key.get_pressed()[pygame.K_DOWN] != 0):
            self.image=self.down
            self.rect.y+=30
        if (pygame.key.get_pressed()[pygame.K_LEFT] != 0):
            self.image=self.left
            self.rect.x-=30
        if (pygame.key.get_pressed()[pygame.K_RIGHT] != 0):
            self.image=self.right
            self.rect.x+=30
class Objects(pygame.sprite.Sprite):
    cancel=load_image('Cancel.png')
    cancel = pygame.transform.scale(cancel, (200, 50))
    def __init__(self,group, x, y):
        super().__init__(group)
        self.image = self.cancel
        self.rect = self.image.get_rect()
        self.rect.x=x
        self.rect.y=y

    def update(self):
        if pygame.sprite.spritecollideany(self, player_group):
            return 1

image=load_image('Intro.jpg')
image=pygame.transform.scale(image, (700, 700));
startScreen()
Player(player_group,150,150)
Objects(sprites,300,500)
image=load_image('Background.jpg')


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for i in player_group:
            i.get_event()
    screen.blit(image, (0, 0));
    sprites.draw(screen)
    for i in sprites:
        if i.update()==1:
            image = load_image('Intro.jpg')
            image = pygame.transform.scale(image, (700, 700));
            endScreen()
            running=False
    player_group.draw(screen)
    pygame.display.flip()