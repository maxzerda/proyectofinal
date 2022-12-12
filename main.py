import pygame
import os
import time
import random
from pygame import mixer
pygame.font.init()
pygame.mixer.init()



#Musica

pygame.mixer.music.load('assets/rebel_theme.wav')
pygame.mixer.music.play()
pygame.mixer.music.set_volume(0.3)
# Dimensiones de la Ventana
WIDTH, HEIGHT = 750, 750

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Proyecto Final")

# Carga de las imagenes


xwing_player = pygame.image.load(os.path.join("assets", "player_xwing.png"))
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "tie_red.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "tie_green.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "tie_blue.png"))

# Proyectiles

RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Fondo escalado para que cubra toda la ventana
background = pygame.transform.scale(pygame.image.load(os.path.join("assets", "galaxia_fondo.png")), (WIDTH, HEIGHT))
perdiste = pygame.transform.scale(pygame.image.load(os.path.join("assets", "perdiste_fondo.png")), (WIDTH, HEIGHT))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
        

    
    def draw(self,window):
        window.blit(self.img, (self.x, self.y))
        
        
            
    def move(self, vel):
        self.y += vel
        
        
    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)
    
    def collision(self, obj):
        return collide(self, obj)
        

class Ship:                                                                 #clase padre basica de naves/ships
    COOLDOWN = 30
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.lasers_img = None
        self.lasers = []
        self.cool_down_counter = 0
        
        
        
        
    def draw(self, window):                                                   #dibujo el player 1 + sus lasers
        window.blit(self.ship_img,(self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):                                          #lo llamo en cada loop en cada nave y player para que disparar los laser 
        
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10     
                self.lasers.remove(laser)
                hit_sound = mixer.Sound("assets/ship_hit.wav")
                hit_sound.play()
                   
             
    def cooldown(self):                                                        # para no disparar tan rapido
        if self.cool_down_counter >=  self.COOLDOWN:
            self.cool_down_counter = 0 
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1      
            
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.lasers_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            laser_sound = mixer.Sound("assets/laser_fire.wav")
            laser_sound.play()
            
             
    def get_width(self):                                  # pido las medidas para limitar las naves contra los bordes de la ventana           
        return self.ship_img.get_width()
    def get_height(self):
        return self.ship_img.get_height()
        
        

                
        
class Player(Ship):                                     #clase hija y nave jugador
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)                  #invoco 
        self.ship_img = xwing_player
        self.lasers_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)    #mascara para mejorar el hitbox 
        self.max_health = health
        
        
    
    def move_lasers(self, vel, objs):  #chequea si el laser q disparamos colisiona con un enemigo si lo hace remover el enemigo y el laser
        
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                            return "mate un enemigo sumame 1 score"
    
    def draw(self,window):                           #llamo la funcion para dibujar la barra de salud 
        super().draw(window)
        self.healthbar(window)
                                                          #barra de vida
    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))              

class Enemy(Ship):                                                         #naves enemigas
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }
    
    
    
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    def move(self, vel):
        self.y += vel
            
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
               

def collide(obj1, obj2):                                                     #para saber cuando colisiona un laser con la nave usando la mascara
    
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None
    
def score(player_vel, score, enemy, laser_vel):
    for player in player():
        player.move(player_vel)
        player.move_lasers(laser_vel, enemy)

        if collide(player, enemy):
            score += 20
            return score
        
        
                                     #main
def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    enemies = []
    wave_lenght = 5
    score = 0
    laser_vel = 4
   
    lost = False
    lost_count = 0
    
    enemy_vel = 1
    player_vel = 4                                     #cantidad de pixeles q se va a mover mi nave
    main_font = pygame.font.SysFont("Franklin Gothic Demi Cond", 50) # typgrafia
    lost_font = pygame.font.SysFont("Franklin Gothic Demi Cond", 90)
    player = Player(300, 650)
    
    
    clock = pygame.time.Clock()
    
    def redraw_widow():                                           #ventana 
        WIN.blit(background, (0,0))
        
        #render de la tipografia 
        lives_label = main_font.render(f"Vidas: {lives}", 1, (255,255,0))  #rgb amarillo
        level_label = main_font.render(f"Nivel: {level}", 1, (255,255,0))  #rgb amarillo
        score_laser = main_font.render(f"Score: {score}", 1, (255,128,0))  #rgb naranja
        
        WIN.blit(lives_label, (10, 10))                                    #posicion de la tipo
        WIN.blit(score_laser, (290, 10)) 
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        
              
            
        for enemy in enemies:
            enemy.draw(WIN)
            
            
        player.draw(WIN)   #nave del jugador
        
        if lost:
            WIN.blit(perdiste,(0,0))
                                                                             #perdiste alert
            lost_label = lost_font.render("Perdiste", 2, (255,50,0))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2,350))
            gameover_sound = mixer.Sound("assets/gameover.wav")
            gameover_sound.play()
            
        pygame.display.update()
    
                                                                      # para que corra a 60 frames aunque estes en una computadora lenta o rapida
    while run:
        clock.tick(FPS)
        redraw_widow()  
        
        if lives < 0 or player.health <= 0:
            lost = True
            lost_count += 1
                                                                     #si perdes detene el juego en 5 segundos
        
    
        if  lost:
            if lost_count > FPS * 3:
                run = False
                return score
            else:
                continue      
        
        
        if len(enemies) == 0:      #creacion de enemigos spawn  
            level += 1
            wave_lenght += 5
            for i in range(wave_lenght):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1000, 0), random.choice(["red","blue","green"])) #llamo al metodo que importe para crear enemigos en lugares random dentro de las posicione que delimite
                enemies.append(enemy)
                
                
        
    
                      
         
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
         
        keys = pygame.key.get_pressed()                      #diccionario de teclas presionadas + movimiento y limites
        if keys[pygame.K_a] and player.x - player_vel > 0:                                      #izquierda
            player.x -= player_vel    
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:              #derecha
            player.x += player_vel
        if keys[pygame.K_w]and player.y - player_vel > 0:                                         #arriba
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() < HEIGHT:              #abajo   
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
    
         
        
                
                
        for enemy in enemies[:]:                                         #creo una lita de enemigos 
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
             
            
            if random.randrange(0, 4*60) == 1 and enemy.y + enemy.get_height() > HEIGHT - 600:      #chance de que un enemigo dispare, empezar a disparar a partir de cierta altura
                enemy.shoot()
                enemy_sound = mixer.Sound("assets/enemy_fire.mp3")
                enemy_sound.play()
                
              
                
            if collide(enemy,player):                                   #si colosionamos con un enemigo perdemos 10 de vida y removemos el enemigo
                player.health -= 10
                enemies.remove(enemy)
                score += 1
                hit_sound = mixer.Sound("assets/ship_hit.wav")
                hit_sound.play()
                
   
                    
                    
            elif enemy.y + enemy.get_height() > HEIGHT:                 #si un enemigo cruza el limite de la pantalla pierdes una vida
                lives -= 1
                enemies.remove(enemy)
        
       
            
                   
        
                                                                        
                     
                
        if player.move_lasers(-laser_vel, enemies):                       #disparos del jugador si pegan +score
            score += 1
            explosion_sound = mixer.Sound("assets/explode.mp3")
            explosion_sound.play()
           


                                                                          #menu principal
def main_menu():
    title_font = pygame.font.SysFont("Franklin Gothic Demi Cond", 40)
    run = True
    
    score = 0
    infile = open('assets/score.txt','r')                                      #leo el txt y adquiero el maximo valor para el score
    score = int(max(infile))
    while run:
        title_label = title_font.render("Presione el mouse para comenzar....", 1, (255,255,0))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 490))
        score_label = title_font.render(f"MAX SCORE: {score}", 1, (255,0,0))
        WIN.blit(score_label, (270, 50))
        
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                high_score = main()
                if high_score > score:
                    score = high_score
                    with open('assets/score.txt', 'a') as text_file:                #al terminar enviar el maximo score a mi txt
                        text_file.write(f"{score}\n")
                print(score)
    pygame.quit()

            
main_menu()