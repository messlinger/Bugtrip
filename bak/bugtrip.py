from math import *
from random import random
import pygame, time, os
from helper import ir
from sprite import MovingSprite
import kinect as kin
import detect

fullscreen = 1
n_sprites = 12
sprite_speed = 200
speedup = 1.05
points = 5


detect.init()
detect.warmup()
detect.take_zero()


os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
W, H = 800, 600  # will be overriden by fullscreen
if fullscreen:
    screen = pygame.display.set_mode( (0,0), pygame.FULLSCREEN )
    W = pygame.display.Info().current_w
    H = pygame.display.Info().current_h
else:
    screen = pygame.display.set_mode( (W,H) )
    
screen.fill((0,0,0))
pygame.display.flip()

font = pygame.font.Font(None, 120)
font_big = pygame.font.Font(None, 250)

class World():
    def __init__(self, (W,H) ):
        self.W, self.H = W, H
world = World( (W,H) )
feet = []




all_sprites = pygame.sprite.Group()
pos = random()*world.W, random()*100  # all from the same nest
for i in range(n_sprites):
    alpha = random()*2*pi
    speed = (random()+1)*sprite_speed/2
    vel = speed*cos(alpha), speed*sin(alpha)
    sp = MovingSprite( pos, vel )
    all_sprites.add(sp)


# Timing
dt = 0.05  # desired frame interval
t_next = None  
t_last_step = None
t_start = None

run = 1
score = 0
game_over = 0

try:
    print 'Main loop'
    while run:
        
        # Pygame events
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or \
                   event.key == pygame.K_ESCAPE:
                    run = 0
            if event.type == pygame.QUIT:
                run = 0
            if event.type == pygame.MOUSEMOTION:
                ##feet = [ Pos(event.pos) ]
                pass
        if not run: break

        # Foot detection
        feet = detect.find_feet()

        # Random direction changes
        for s in all_sprites:
            dphi = 0.1*(random()-0.5)
            s.rotate_vel(dphi)

        # Attraction to base line
        for s in all_sprites:
            delta = pi/2. - atan2(s.vy, s.vx)
            if delta>pi: delta = delta - 2*pi
            s.rotate_vel( delta * dt/20. )
            

        # Repulsion from feet
        for f in feet:
            for s in all_sprites:
                fsx = s.x - f.x  # vector foot -> sprite
                fsy = s.y - f.y
                d = sqrt(fsx**2 + fsy**2)
                if d<120:
                    s.rotate_vel( atan2(fsy,fsx), absolute=1)
                    s.speedup( 1.01 )
                 

        # Motion update        
        t = time.time()
        if t_start==None:
            t_last_step = t-dt
            t_start = t
        all_sprites.update(t-t_last_step, world) # real
        t_last_step = t

        # Test baseline hits
        for s in all_sprites:
            if s.y > H-10:
                print 'HIT!' + ' Score:' + str(score)               
                pos = random()*world.W, random()*100  # Respawn
                vel = 100*cos(random()), 100*sin(random())
                s.set_pos( pos )
                s.set_vel( vel )
                score += 1
                if score>=points: game_over = 1                    
                

        # Screen
        screen.fill((0,0,0))
        all_sprites.draw(screen)

        for f in feet:
            pygame.draw.circle( screen, (255,255,255), ir((f.x,f.y)), 60, 0 )
            pygame.draw.circle( screen, (255,0,0), ir((f.x,f.y)), 60, 2 )

        text_score = font.render("%d" % score, 2, (255, 255, 255))
        screen.blit( text_score, (world.W/2-20, 40) )

        if game_over:
            tt = time.time() - t_start
            mini, sec = int(tt//60), int(tt%60)
            screen.blit( font_big.render("Game over", 3, (255, 255, 255)), (100, 250) )
            screen.blit( font_big.render("Time %d:%.02d" % (mini, sec), 3, (255, 255, 255)), (120,450) )

        pygame.draw.rect( screen, (255,255,255), (0,0,W,H), 10 )
        pygame.display.flip()
        
        if game_over:
            while pygame.event.poll().type != pygame.KEYDOWN: pass
            run = 0
            break


finally:
    pygame.quit()
    detect.quit()
