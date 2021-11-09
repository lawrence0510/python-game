import pygame
import random
import os

#使得鍵盤操作可以被pygame函式庫讀取
from pygame.constants import KEYDOWN

#設定螢幕更新率
FPS=60

#顏色設定
white=(255,250,250)
black=(0,0,0)
green=(0,255,0)
red=(255,0,0)
yellow=(255,255,0)

#長寬設定
width=500
height=600

#重製pygame與設定基本數值
pygame.init()
pygame.mixer.init()
screen=pygame.display.set_mode((width,height))
pygame.display.set_caption("太空生存戰") #視窗名稱
clock=pygame.time.Clock() #更新時脈

#插入圖片
background_img=pygame.image.load(os.path.join("img", "background.png")).convert()
bullet_img=pygame.image.load(os.path.join("img", "bullet.png")).convert()
player_img=pygame.image.load(os.path.join("img", "player.png")).convert()
player_mini_image=pygame.transform.scale(player_img, (25,19))
player_mini_image.set_colorkey(black)
pygame.display.set_icon(player_mini_image)
rockimages=[]
for i in range(7):
    rockimages.append(pygame.image.load(os.path.join("img", f"rock{i}.png")).convert())
explode_animation={}
explode_animation['large']=[]
explode_animation['small']=[]
explode_animation['player']=[]
for i in range(9):
    explode_img=pygame.image.load(os.path.join("img", f"expl{i}.png")).convert()
    explode_img.set_colorkey(black)
    explode_animation['large'].append(pygame.transform.scale(explode_img, (75,75)))
    explode_animation['small'].append(pygame.transform.scale(explode_img, (30,30)))
    player_explode_img=pygame.image.load(os.path.join("img", f"player_expl{i}.png")).convert()
    player_explode_img.set_colorkey(black)
    explode_animation['player'].append(player_explode_img)
#插入音樂
shootsound=pygame.mixer.Sound(os.path.join("sound", "shoot.wav"))
diesound=pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))
explodesound=[
    pygame.mixer.Sound(os.path.join("sound", "expl0.wav")),
    pygame.mixer.Sound(os.path.join("sound", "expl1.wav"))
]

#插入背景音樂
pygame.mixer.music.load(os.path.join("Sound","background.ogg"))
pygame.mixer.music.set_volume(0.15)

#分數字體樣式
font_name=os.path.join("font.ttf")
def draw_text(surf, text, size, x, y):
    font=pygame.font.Font(font_name, size)
    text_surface=font.render(text, True, white)
    text_rect=text_surface.get_rect()
    text_rect.centerx=x
    text_rect.top=y
    surf.blit(text_surface, text_rect)
#增加一個新石頭畫面中的函式
def new_rock():
    r=Rock()
    all_sprite.add(r)
    rocks.add(r)

#將剩餘血量顯示出來
def draw_health(surf, hp, x, y):
    if hp<0:
        hp=0
    bar_length=100
    bar_height=10
    fill=hp/100*bar_length
    outline_rect=pygame.Rect(x, y, bar_length, bar_height)
    fill_rect=pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surf, green, fill_rect)
    pygame.draw.rect(surf, white, outline_rect, 2)

#將剩餘命數顯示出來
def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect=img.get_rect()
        img_rect.x=x+32*i
        img_rect.y=y
        surf.blit(img, img_rect)

#初始畫面的顯示
def draw_initial():
    screen.blit(background_img, (0,0))
    draw_text(screen, '太空生存戰', 64, width/2, height/4)
    draw_text(screen, '← →移動飛船 空白鍵發射子彈', 22, width/2, height/2)
    draw_text(screen, '按任意鍵開始遊戲!', 18, width/2, height*3/4)
    pygame.display.update()
    waiting=True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYDOWN:
                waiting = False
                return False

#重置遊戲
def reset():
    all_sprite=pygame.sprite.Group()
    rocks= pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    player=Player()
    all_sprite.add(player)
    for i in range(8):
        new_rock()
    score=0

#建立一個可以操作player的sprite
class Player(pygame.sprite.Sprite):
    #初始化這個class
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image=pygame.transform.scale(player_img, (50,38)) 
        self.image.set_colorkey(black)
        self.rect=self.image.get_rect()
        self.radius=20
        #pygame.draw.circle(self.image, red, self.rect.center, self.radius)
        self.rect.centerx=width/2
        self.rect.bottom=height-10
        self.speedx=8
        self.health=100
        self.lives=3
        self.hidden=False
        self.hide_time=0
    def update(self):
        key_pressed= pygame.key.get_pressed()
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx
        if self.rect.right > width:
            self.rect.right=width
        if self.rect.left < 0:
            self.rect.left=0
        if self.hidden and pygame.time.get_ticks()-self.hide_time>1000:
            self.hidden=False
            self.rect.centerx=width/2
            self.rect.bottom=height-10
    def shoot(self):
        if not(self.hidden):
            bullet=Bullet(self.rect.centerx, self.rect.top)
            all_sprite.add(bullet)
            bullets.add(bullet)
            shootsound.play()
    def hide(self):
        self.hidden=True
        self.hide_time=pygame.time.get_ticks()
        self.rect.center=(width/2, height+500)
class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.imageoriginal=random.choice(rockimages)
        self.image=self.imageoriginal.copy()
        self.imageoriginal.set_colorkey(black)
        self.rect=self.image.get_rect()
        self.radius=int(self.rect.width*0.85/2)
        #pygame.draw.circle(self.image, red, self.rect.center, self.radius)
        self.rect.x=random.randrange(0,width-self.rect.width)
        self.rect.y=random.randrange(-180,-100)
        self.speedy=random.randrange(5,10)
        self.speedx=random.randrange(-3,3)
        self.totaldegree=0
        self.rotatedegree=random.randrange(-3,3)
    def rotate(self):
        self.totaldegree+=self.rotatedegree
        self.totaldegree=self.totaldegree%360
        self.image=pygame.transform.rotate(self.imageoriginal, self.totaldegree)
        center=self.rect.center
        self.rect=self.image.get_rect()
        self.rect.center=center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top >height or self.rect.left > width or self.rect.right <0:
            self.rect.x=random.randrange(0,width-self.rect.width)
            self.rect.y=random.randrange(-100,-40)
            self.speedy=random.randrange(2,10)
            self.speedx=random.randrange(-3,3)
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image=bullet_img
        self.image.set_colorkey(black)
        self.rect=self.image.get_rect()
        self.rect.centerx=x
        self.rect.bottom=y
        self.speedy= -10
    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom <0:
            self.kill()
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explode_animation[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explode_animation[self.size]):
                self.kill()
            else:
                self.image = explode_animation[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center

all_sprite=pygame.sprite.Group()
rocks= pygame.sprite.Group()
bullets = pygame.sprite.Group()

player=Player()
all_sprite.add(player)
for i in range(8):
    new_rock()
score=0
pygame.mixer.music.play(-1)

show_initial=True
running=True

#結尾畫面的顯示
def draw_epilogue():
    screen.blit(background_img, (0,0))
    draw_text(screen, 'You Died!', 64, width/2, height/4)
    draw_text(screen, '您的最終得分為: '+str(score)+'分', 36, width/2, height/2)
    draw_text(screen, '按任意鍵重新開始遊戲!', 18, width/2, height*3/4)
    pygame.display.update()
    waiting=True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYDOWN:
                waiting=False
                show_initial=True
                running=True  
    all_sprite.update()

def wait_for_key(self):
    waiting = True
    while waiting:
        self.clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
                self.running = False
            if event.type == pygame.KEYUP:
                running=True

while running:
    clock.tick(FPS) #一秒鐘之內最多只能被執行FPS次_解決電腦速度不一之問題
    if show_initial:
        draw_initial()
        show_initial=False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False
        elif event.type == KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()
    all_sprite.update()
    
    #判斷有沒有相撞
    hits=pygame.sprite.groupcollide(rocks, bullets, True, True)
    for hit in hits:
        random.choice(explodesound).play()
        new_rock()
        score+=hit.radius
        explode=Explosion(hit.rect.center, 'large')
        all_sprite.add(explode)
    hits=pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_circle)
    for hit in hits:
        new_rock()
        player.health-=hit.radius
        if player.health <=0:
            die=Explosion(player.rect.center, 'player')
            all_sprite.add(die)
            diesound.play()
            player.lives-=1
            player.health=100
            player.hide()
        explode=Explosion(hit.rect.center, 'small')
        all_sprite.add(explode)
    if player.lives==0 and not(die.alive()):
        screen.blit(background_img, (0,0))
        draw_text(screen, 'You Died!', 64, width/2, height/4)
        draw_text(screen, '您的最終得分為: '+str(score)+'分', 36, width/2, height/2)
        draw_text(screen, '按任意鍵重新開始遊戲!', 18, width/2, height*3/4)
        pygame.display.update()
        self.wait_for_key()
    screen.fill(black)
    screen.blit(background_img, (0,0))
    all_sprite.draw(screen)
    draw_text(screen, str(score), 18, width/2, 10)
    draw_health(screen, player.health, 5, 15)
    draw_lives(screen, player.lives, player_mini_image, width-100, 15)
    pygame.display.update()
pygame.quit() #退出遊戲
