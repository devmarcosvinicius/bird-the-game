import pygame
from pygame import mixer
import random

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

largura_tela = 600
altura_tela = 800
tela = pygame.display.set_mode((largura_tela, altura_tela))
pygame.display.set_caption('Bird The Game')

font30 = pygame.font.SysFont('Constantia', 30)
font40 = pygame.font.SysFont('Constantia', 40)

morte_fx = pygame.mixer.Sound("img/passarinho_morrendo.mp3")
morte_fx.set_volume(0.08)

morte2_fx = pygame.mixer.Sound("img/passarinho_morrendo.mp3")
morte2_fx.set_volume(0.08)

flexada_fx = pygame.mixer.Sound("img/passarinho_cantando.mp3")
flexada_fx.set_volume(0.05)

rows = 5
cols = 5
alien_cooldown = 1000
ultimo_tiro_inimigo = pygame.time.get_ticks()
countdown = 3
last_count = pygame.time.get_ticks()
fim = 0

red = (255, 0, 0)
green = (0, 255, 0)
white = (255, 255, 255)

bg = pygame.image.load("img/bg.png")

passaro_grupo = pygame.sprite.Group()
flexa_grupo = pygame.sprite.Group()
inimigo_grupo = pygame.sprite.Group()
ovos_grupo = pygame.sprite.Group()
morte_grupo = pygame.sprite.Group()

bg_start = pygame.image.load("img/bg_start.png")  
bg_win = pygame.image.load("img/bg_win.png")  
bg_gameover = pygame.image.load("img/bg_gameover.png")  

run = True
game_started = False  
fim = 0  

def desenhar_bg():
	tela.blit(bg, (0, 0))

def desenhar_texto(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	tela.blit(img, (x, y))

class Passaro(pygame.sprite.Sprite):
	def __init__(self, x, y, health):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/bird.png")
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.health_start = health
		self.health_remaining = health
		self.last_shot = pygame.time.get_ticks()

	def update(self):
		speed = 8
		cooldown = 500
		game_over = 0

		key = pygame.key.get_pressed()
		if key[pygame.K_LEFT] and self.rect.left > 0:
			self.rect.x -= speed
		if key[pygame.K_RIGHT] and self.rect.right < largura_tela:
			self.rect.x += speed

		time_now = pygame.time.get_ticks()
		if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
			flexada_fx.play()
			bullet = Ovos(self.rect.centerx, self.rect.top)
			flexa_grupo.add(bullet)
			self.last_shot = time_now

		self.mask = pygame.mask.from_surface(self.image)

		pygame.draw.rect(tela, red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
		if self.health_remaining > 0:
			pygame.draw.rect(tela, green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 15))
		elif self.health_remaining <= 0:
			explosion = Morte(self.rect.centerx, self.rect.centery, 3)
			morte_grupo.add(explosion)
			self.kill()
			game_over = -1
		return game_over


passaro = Passaro(int(largura_tela / 2), altura_tela - 100, 3)
passaro_grupo.add(passaro)

class Ovos(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/arrow.png")
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]

	def update(self):
		self.rect.y -= 5
		if self.rect.bottom < 0:
			self.kill()
		if pygame.sprite.spritecollide(self, inimigo_grupo, True):
			self.kill()
			morte_fx.play()
			explosion = Morte(self.rect.centerx, self.rect.centery, 2)
			morte_grupo.add(explosion)
   
   
class Inimigos(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/enemy" + str(random.randint(1, 4)) + ".png")
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.move_counter = 0
		self.move_direction = 1

	def update(self):
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 75:
			self.move_direction *= -1
			self.move_counter *= self.move_direction

class Ovos_Inimigos(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/enemy_egg.png")
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]

	def update(self):
		self.rect.y += 2
		if self.rect.top > altura_tela:
			self.kill()
		if pygame.sprite.spritecollide(self, passaro_grupo, False, pygame.sprite.collide_mask):
			self.kill()
			morte2_fx.play()
			passaro.health_remaining -= 1
			explosion = Morte(self.rect.centerx, self.rect.centery, 1)
			morte_grupo.add(explosion)
   
   
class Morte(pygame.sprite.Sprite):
	def __init__(self, x, y, size):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(1, 2):
			img = pygame.image.load(f"img/feathers.png")
			if size == 1:
				img = pygame.transform.scale(img, (20, 20))
			if size == 2:
				img = pygame.transform.scale(img, (40, 40))
			if size == 3:
				img = pygame.transform.scale(img, (160, 160))
			self.images.append(img)
		self.index = 0
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.counter = 0

	def update(self):
		explosion_speed = 3
		self.counter += 1
		if self.counter >= explosion_speed and self.index < len(self.images) - 1:
			self.counter = 0
			self.index += 1
			self.image = self.images[self.index]
		if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
			self.kill()
   

def create_inimigo():
	for row in range(rows):
		for item in range(cols):
			inimigo = Inimigos(100 + item * 100, 100 + row * 70)
			inimigo_grupo.add(inimigo)

create_inimigo()

def reset_game():
    global passaro_grupo, flexa_grupo, inimigo_grupo, ovos_grupo, morte_grupo, passaro, fim, countdown
    passaro_grupo = pygame.sprite.Group()
    flexa_grupo = pygame.sprite.Group()
    inimigo_grupo = pygame.sprite.Group()
    ovos_grupo = pygame.sprite.Group()
    morte_grupo = pygame.sprite.Group()
    create_inimigo()
    passaro = Passaro(int(largura_tela / 2), altura_tela - 100, 3)
    passaro_grupo.add(passaro)
    fim = 0
    countdown = 3

while run:
    if not game_started:
        
        tela.blit(bg_start, (0, 0))  
        desenhar_texto("Bird The Game", font40, white, int(largura_tela / 2 - 120), int(altura_tela / 2 - 50))
        desenhar_texto("Pressione espaço para começar", font30, white, int(largura_tela / 2 - 180), int(altura_tela / 2 + 10))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_started = True

    elif fim == -1:  
        tela.blit(bg_gameover, (0, 0))  
        desenhar_texto("Você morreu! :(", font40, white, int(largura_tela / 2 - 120), int(altura_tela / 2 - 50))
        desenhar_texto("Pressione espaço para recomeçar", font30, white, int(largura_tela / 2 - 180), int(altura_tela / 2 + 10))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                reset_game()
                game_started = True

    elif fim == 1:  
        tela.blit(bg_win, (0, 0))  
        desenhar_texto("Você venceu!", font40, white, int(largura_tela / 2 - 120), int(altura_tela / 2 - 50))
        desenhar_texto("Pressione espaço para começar", font30, white, int(largura_tela / 2 - 180), int(altura_tela / 2 + 10))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                reset_game()
                game_started = True

    else:
        
        clock.tick(fps)
        desenhar_bg()

        if countdown == 0:
            time_now = pygame.time.get_ticks()
            if time_now - ultimo_tiro_inimigo > alien_cooldown and len(ovos_grupo) < 5 and len(inimigo_grupo) > 0:
                inimigo_atacando = random.choice(inimigo_grupo.sprites())
                ovos = Ovos_Inimigos(inimigo_atacando.rect.centerx, inimigo_atacando.rect.bottom)
                ovos_grupo.add(ovos)
                ultimo_tiro_inimigo = time_now
            if len(inimigo_grupo) == 0:
                fim = 1
            if fim == 0:
                fim = passaro.update()
                flexa_grupo.update()
                inimigo_grupo.update()
                ovos_grupo.update()
            else:
                if fim == 1:
                    desenhar_texto('YOU WIN!', font40, white, int(largura_tela / 2 - 100), int(altura_tela / 2 + 50))

        if countdown > 0:
            desenhar_texto('GET READY!', font40, white, int(largura_tela / 2 - 110), int(altura_tela / 2 + 50))
            desenhar_texto(str(countdown), font40, white, int(largura_tela / 2 - 10), int(altura_tela / 2 + 100))
            count_timer = pygame.time.get_ticks()
            if count_timer - last_count > 1000:
                countdown -= 1
                last_count = count_timer

        morte_grupo.update()
        passaro_grupo.draw(tela)
        flexa_grupo.draw(tela)
        inimigo_grupo.draw(tela)
        ovos_grupo.draw(tela)
        morte_grupo.draw(tela)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.display.update()

pygame.quit()
