import pygame, sys
from player import Player
import obstracle
from alien import Alien, Extra
from random import choice, randint
from laser import Laser

class Game:
    def __init__(self):
        # player setup
        player_sprite = Player((screen_width/2,screen_height),screen_width,5)
        self.player = pygame.sprite.GroupSingle(player_sprite)

        # health and score
        self.lives =3
        self.live_surf = pygame.image.load('graphics\spc1.png')
        self.live_x_start_pos = screen_width - (self.live_surf.get_size()[0] * 2 + 20)
        self.score =0
        self.font = pygame.font.Font('graphics\Pixeled.ttf',20)
        # obstracle setup
        self.shape = obstracle.shape
        self.block_size=6
        self.blocks = pygame.sprite.Group()
        self.obstracle_amount=5
        self.obstracle_x_pos = [num * (screen_width/self.obstracle_amount) for num in range(self.obstracle_amount)]
        self.create_multi_obstacles(*self.obstracle_x_pos, x_start=screen_width/15,y_start=450)
        # alien group
        self.aliens = pygame.sprite.Group()
        self.alien_lasers = pygame.sprite.Group()
        self.alien_setup(rows=6,cols=13)
        self.alien_direction=1

        # extra setup
        self.extra = pygame.sprite.GroupSingle()
        self.extra_spawn_time = randint(400,800)
        
    def create_obstacle(self, x_start, y_start,offset_x):
        for row_idx,row in enumerate(self.shape):
            for col_idx,col in enumerate(row):
                if col=='x':
                    x= x_start+col_idx*self.block_size+offset_x
                    y= y_start+row_idx*self.block_size
                    block = obstracle.Block(self.block_size,(241,79,80),x,y)
                    self.blocks.add(block)

    def create_multi_obstacles(self,*offset,x_start,y_start):
        for offset_x in offset:
            self.create_obstacle(x_start,y_start,offset_x)

    def alien_setup(self, rows, cols,x_dis=60,y_dis=48,x_offset=70,y_offset=80):
        for row_idx,row in enumerate(range(rows)):
            for col_idx,col in enumerate(range(cols)):
                x= col_idx * x_dis +x_offset
                y= row_idx * y_dis + y_offset
                if row_idx == 0 or row_idx == 1: alien_sprite = Alien('yellow',x,y)
                elif 2 <= row_idx <= 3: alien_sprite = Alien('red',x,y)
                else: alien_sprite = Alien('green',x,y)
                self.aliens.add(alien_sprite)

    def alien_pos_chk(self):
        all_aliens = self.aliens.sprites()
        for alien in all_aliens:
            if alien.rect.right >= screen_width:
                self.alien_direction =-1
                self.alien_mov_dn(2)
            elif alien.rect.left <= 0:
                self.alien_direction =1
                self.alien_mov_dn(2)

    def alien_mov_dn(self,direction):
        if self.aliens:
            for alien in self.aliens.sprites():
                alien.rect.y +=direction

    def alien_shoot(self):
        if self.aliens.sprites():
            random_alien = choice(self.aliens.sprites())
            Laser_sprite = Laser(random_alien.rect.center,6,screen_height)
            self.alien_lasers.add(Laser_sprite)

    def extra_alien_timer(self):
        self.extra_spawn_time -=1
        if self.extra_spawn_time <=0:
            self.extra.add(Extra(choice(['right','left']),screen_width))
            self.extra_spawn_time = randint(400,800)

    def collision_check(self):
        # player
        if self.player.sprite.lasers:
            for laser in self.player.sprite.lasers:
                # obstacle collision
                if pygame.sprite.spritecollide(laser,self.blocks,True):
                    laser.kill()
                # alien  collision
                aliens_hit=pygame.sprite.spritecollide(laser,self.aliens,True)
                if aliens_hit:
                    for alien in aliens_hit:
                        self.score += 100
                    laser.kill()
                # extra  collision
                if pygame.sprite.spritecollide(laser,self.extra,True):
                    self.score +=500
                    laser.kill()
        if self.alien_lasers:
            for laser in self.alien_lasers:
                # obstacle collision
                if pygame.sprite.spritecollide(laser,self.blocks,True):
                    laser.kill()
                # player collision
                if pygame.sprite.spritecollide(laser,self.player,False):
                    laser.kill()
                    self.lives -=1
                    if self.lives <=0:
                        pygame.quit()
                        sys.exit()
        
        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien,self.blocks,True)
                # player collision
                if pygame.sprite.spritecollide(alien,self.player,False):
                    pygame.quit()
                    sys.exit()

    def display_lives(self):
        for live in range(self.lives-1):
            x=self.live_x_start_pos + (live * (self.live_surf.get_size()[0] + 10))
            screen.blit(self.live_surf,(x,8))

    def display_score(self):
        score_surf = self.font.render(f'score: {self.score}',False,'white')
        score_rect = score_surf.get_rect(topleft = (10,-10))
        screen.blit(score_surf,score_rect)

    def run(self):
        #update all alien groups
        self.player.update()
        self.aliens.update(self.alien_direction)
        self.alien_pos_chk()
        self.alien_lasers.update()
        self.extra.update()  
        self.extra_alien_timer()
        self.collision_check()

        #draw all alien groups
        self.player.sprite.lasers.draw(screen)
        self.player.draw(screen)
        self.blocks.draw(screen)
        self.aliens.draw(screen)
        self.alien_lasers.draw(screen)
        self.extra.draw(screen)
        self.display_lives()
        self.display_score()


if __name__ == '__main__':
    pygame.init()
    # Screen settings
    screen_width = 900
    screen_height = 600
    screen =pygame.display.set_mode((screen_width,screen_height))
    # for max frame rate
    clock= pygame.time.Clock()
    game = Game()

    # alien shooting timer
    ALIENLASER = pygame.USEREVENT +1
    pygame.time.set_timer(ALIENLASER,800)


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type ==ALIENLASER:
                game.alien_shoot()


        screen.fill((0,0,0))
        game.run()
        
        pygame.display.flip()
        clock.tick(60)
