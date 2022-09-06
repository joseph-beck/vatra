import pygame, sys

from support import import_csv_layout, import_cut_assets
from settings import *
from tiles import *
from particles import ParticleEffect
from player import Player


class Level:
    def __init__(self, level_data, surface, ):
        # general setup
        self.display_surface = surface
        self.world_shift = 0

        # player setup
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout)

        # dust
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False

        # terrain setup
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout, 'static_tile', 'assets/dungeon/tilesheet-enlarged.png')

        # pillar setup
        pillar_layout = import_csv_layout(level_data['pillars'])
        self.pillar_sprites = self.create_tile_group(pillar_layout, 'static_tile', 'assets/dungeon/tilesheet-enlarged.png')

        # chains setup
        chains_layout = import_csv_layout(level_data['chains'])
        self.chains_sprites = self.create_tile_group(chains_layout, 'static_tile', 'assets/dungeon/tilesheet-enlarged.png')

        # coins setup
        coin_layout = import_csv_layout(level_data['coins'])
        self.coin_sprites = self.create_tile_group(coin_layout, 'offset_animated_tile', 'assets/dungeon/coins')


    def create_tile_group(self, layout, type, path):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout): 
            for col_index, val in enumerate(row):
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == 'static_tile':
                        tile_list = import_cut_assets(path)
                        tile_surface = tile_list[int(val)]

                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'animated_tile':
                        sprite = AnimatedTile(tile_size, x, y, path)

                    if type == 'offset_animated_tile':
                        sprite = OffsetAnimatedTile(tile_size, x, y, path)

                    sprite_group.add(sprite)

        return sprite_group

    def player_setup(self, layout):
        for row_index, row in enumerate(layout): 
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = col_index * tile_size

                if val == '0':
                    sprite = Player((x, y), self.display_surface, self.create_jump_particles)
                    self.player.add(sprite)

                if val == '1':
                    hat_surface = pygame.image.load('assets/player/hat.png').convert_alpha()
                    sprite = StaticTile(tile_size, x, y, hat_surface)
                    self.goal.add(sprite)

    def create_jump_particles(self, pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(10, 5)
        else:
            pos += pygame.math.Vector2(10, -5)

        jump_particles_sprite = ParticleEffect(pos, 'jump')
        self.dust_sprite.add(jump_particles_sprite)

    def create_landing_dust(self):
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10, 15)
            else:
                offset = pygame.math.Vector2(-10, 15)

            fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset, 'land')
            self.dust_sprite.add(fall_dust_particle)

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.collision_rect.x += player.direction.x * player.speed

        collidable_sprites = self.terrain_sprites.sprites()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.x < 0:
                    player.collision_rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.collision_rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right

    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False

    def vertical_movement_collision(self):
        self.get_player_on_ground()

        player = self.player.sprite
        player.apply_gravity()

        collidable_sprites = self.terrain_sprites.sprites()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.y > 0:
                    player.collision_rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.x > 0:
                    player.collision_rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < screen_width / 4 and direction_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > screen_width - (screen_width / 4) and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8

    def check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite, self.goal, False):
            print('finished')

    def check_death(self):
        if self.player.sprite.rect.top > screen_height:
            print('died')
            pygame.quit()
            sys.exit()

    #def check_coin_collisions(self):
    #    collided_coins = pygame.sprite.spritecollide(self.player.sprite, self.coin_sprites, True)
        

    def run(self):
        # run the entire level
        self.terrain_sprites.update(self.world_shift)
        self.terrain_sprites.draw(self.display_surface)

        # pillars
        self.pillar_sprites.update(self.world_shift)
        self.pillar_sprites.draw(self.display_surface)

        # chains
        self.chains_sprites.update(self.world_shift)
        self.chains_sprites.draw(self.display_surface)

        # coins
        self.coin_sprites.update(self.world_shift)
        self.coin_sprites.draw(self.display_surface)

        # player
        self.player.update()
        
        self.horizontal_movement_collision()
        self.vertical_movement_collision()

        self.create_landing_dust()
        self.scroll_x()

        self.player.draw(self.display_surface)
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)

        self.check_win()
        self.check_death()

        #self.check_coin_collisions()
