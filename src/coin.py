from tiles import AnimatedTile

class Coin(AnimatedTile):
    def __init__(self, size, x, y, path):
        super().__init__(size, x, y, path)

        center_x = x + int(size / 2)
        center_y = y + int(size / 2)

        self.rect = self.image.get_rect(center = (center_x, center_y))
