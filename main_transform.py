import random
import struct
import time

import arcade

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Compute collision detect"

COIN_COUNT = 500
SPRITE_SCALING_COIN = 0.10
SPRITE_SCALING_PLAYER = 0.25


class CollisionTransform(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        # Sprites
        self.coin_list = arcade.SpriteList(use_spatial_hash=False)
        self.player_list = arcade.SpriteList()
        self.avg = 0

        # Set up the player
        img = ":resources:images/animated_characters/female_person/femalePerson_idle.png"
        self.player_sprite = arcade.Sprite(
            img,
            SPRITE_SCALING_PLAYER,
            center_x = 50,
            center_y = 50,
            hit_box_algorithm='None',
        )
        self.player_list.append(self.player_sprite)

        # Coins
        for i in range(COIN_COUNT):
            # Create the coin instance
            scaling = [0.1, 0.25]
            coin = arcade.Sprite(
                ":resources:images/items/coinGold.png",
                random.choice(scaling),
                center_x=random.randrange(SCREEN_WIDTH),
                center_y=random.randrange(SCREEN_HEIGHT),
                hit_box_algorithm='None',
            )
            self.coin_list.append(coin)

        # Create large square
        coin = arcade.SpriteSolidColor(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4, arcade.color.WHITE)
        coin.center_x = SCREEN_WIDTH // 4
        coin.center_y = SCREEN_HEIGHT // 4
        self.coin_list.append(coin)
        # Create large square
        coin = arcade.SpriteSolidColor(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4, arcade.color.WHITE)
        coin.center_x = SCREEN_WIDTH * 3 // 4
        coin.center_y = SCREEN_HEIGHT * 3 // 4
        coin.angle = 45
        self.coin_list.append(coin)

        self.program = self.ctx.load_program(
            vertex_shader="shaders/col_trans_vs.glsl",
            geometry_shader="shaders/col_trans_gs.glsl",
        )
        self.buffer = self.ctx.buffer(reserve=len(self.coin_list) * 4)
        self.query = self.ctx.query()

    def on_draw(self):
        self.clear()
        self.coin_list.draw()
        self.coin_list.draw_hit_boxes(color=(0, 255, 0, 255))
        self.player_list.draw()
        self.player_list.draw_hit_boxes(color=(255, 255, 255, 255))

    def on_update(self, delta_time: float):
        t = time.perf_counter()
        sprites = self.new_check_for_collision_with_list(self.player_sprite, self.coin_list)
        t = time.perf_counter() - t
        if self.avg == 0:
            self.avg = t
        else:
            self.avg += t
            self.avg /= 2.0

        # print(f"col check {len(sprites)}: {t} avg {self.avg}")
        for sprite in sprites:
            sprite.color = 255, 0, 0, 255

    def on_mouse_motion(self, x, y, dx, dy):
        """ Handle Mouse Motion """
        # Move the center of the player sprite to match the mouse x, y
        self.player_sprite.center_x = x
        self.player_sprite.center_y = y

    def new_check_for_collision_with_list(self, sprite, sprite_list):
        # Update the position and size to check
        self.program["check_pos"] = sprite.position
        self.program["check_size"] = sprite.width, sprite.height

        # Ensure the result buffer can fit all the sprites (worst case)
        self.buffer.orphan(size=len(sprite_list) * 4)
        # Run the transform shader emitting sprites close to the configured position and size.
        # This runs in a query so we can measure the number of sprites emitted.
        with self.query:
            self.coin_list._geometry.transform(self.program, self.buffer, vertices=len(sprite_list))

        # Store the number of sprites emitted
        num_sprites = self.query.primitives_generated
        # print(num_sprites, self.query.time_elapsed, self.query.time_elapsed / 1_000_000_000)

        # If no sprites emitted we can just return an empty list
        if num_sprites == 0:
            return []

        # .. otherwise build and return a list of the sprites selected by the transform
        return [
            sprite_list[i] 
            for i in struct.unpack(f'{num_sprites}i', self.buffer.read(size=num_sprites * 4))
        ]


CollisionTransform().run()
