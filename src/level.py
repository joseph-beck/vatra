import pygame

from support import import_csv_layout, import_cut_assets
from settings import tile_size
from tiles import StaticTile
from coin import Coin

class Level:
    def __init__(self, level_data, surface):
        # general setup
        self.display_surface = surface
        self.world_shift = 0

        # terrain setup
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain')

        # pillar setup
        pillar_layout = import_csv_layout(level_data['pillars'])
        self.pillar_sprites = self.create_tile_group(pillar_layout, 'pillars')

        # chains setup
        chains_layout = import_csv_layout(level_data['chains'])
        self.chains_sprites = self.create_tile_group(chains_layout, 'chains')

        # coins setup
        coin_layout = import_csv_layout(level_data['coins'])
        self.coin_sprites = self.create_tile_group(coin_layout, 'coins')


    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout): 
            for col_index, val in enumerate(row):
                if val != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == 'terrain' or 'chains' or 'pillars':
                        tile_list = import_cut_assets('assets/dungeon/tilesheet-enlarged.png')
                        tile_surface = tile_list[int(val)]

                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    if type == 'coins':
                        sprite = Coin(tile_size, x, y,'assets/dungeon/coins')

                    sprite_group.add(sprite)

        return sprite_group

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
