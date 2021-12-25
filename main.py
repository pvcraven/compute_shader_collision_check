import array
import random
import arcade

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
SCREEN_TITLE = "Compute collision detect"

COIN_COUNT = 30000
SPRITE_SCALING_COIN = 0.25
SPRITE_SCALING_PLAYER = 0.25


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        # --- Shaders
        # Load in the shader source code
        file = open("collision_detect.glsl")
        compute_shader_source = file.read()
        self.compute_shader = self.ctx.compute_shader(source=compute_shader_source)

        self.ssbo_0 = None
        self.ssbo_1 = None
        self.ssbo_2 = None

        # Don't forget to turn the spatial has on or off, depending on how you want to check
        self.coin_list = arcade.SpriteList(use_spatial_hash=True)
        self.player_list = arcade.SpriteList()

        # Set up the player
        img = ":resources:images/animated_characters/female_person/femalePerson_idle.png"
        self.player_sprite = arcade.Sprite(img, SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.player_list.append(self.player_sprite)

        # Coins
        for i in range(COIN_COUNT):

            # Create the coin instance
            scaling = [0.1, 0.25]
            coin = arcade.Sprite(":resources:images/items/coinGold.png", random.choice(scaling))

            # Position the coin
            coin.center_x = random.randrange(SCREEN_WIDTH)
            coin.center_y = random.randrange(SCREEN_HEIGHT)

            # Add the coin to the lists
            self.coin_list.append(coin)

        # Create the coin instance
        coin = arcade.SpriteSolidColor(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, arcade.color.WHITE)

        # Position the coin
        coin.center_x = SCREEN_WIDTH // 2
        coin.center_y = SCREEN_HEIGHT // 2

        # Add the coin to the lists
        self.coin_list.append(coin)

        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        """ Render the screen. """

        arcade.start_render()

        self.coin_list.draw()
        self.player_list.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        """ Handle Mouse Motion """

        # Move the center of the player sprite to match the mouse x, y
        self.player_sprite.center_x = x
        self.player_sprite.center_y = y

    def new_check_for_collision_with_list(self, sprite, sprite_list):

        # Don't recreate the buffer if it already exists
        # if not self.ssbo_0:
        self.ssbo_0 = self.ctx.buffer(data=sprite_list._sprite_pos_data)
        self.ssbo_1 = self.ctx.buffer(data=sprite_list._sprite_size_data)
        self.ssbo_2 = self.ctx.buffer(reserve=self.ssbo_0.size // 2)

        self.ssbo_0.bind_to_storage_buffer(binding=0)
        self.ssbo_1.bind_to_storage_buffer(binding=1)
        self.ssbo_2.bind_to_storage_buffer(binding=2)

        self.compute_shader["check_pos"] = sprite.position
        self.compute_shader["check_size"] = sprite.width, sprite.height

        # Run compute shader
        self.compute_shader.run(group_x=256, group_y=1)

        # Get the results for the compute shader
        # This is a list of sprites that can collide, but might not be colliding
        data = self.ssbo_2.read()
        arr = array.array('i')
        arr.frombytes(data)
        sub_list = [sprite_list[index] for index, number in enumerate(arr) if number == 222]

        # Now do a more detailed check and see if they collided
        collision_list = [cur_sprite for cur_sprite in sub_list if arcade.check_for_collision(sprite, cur_sprite)]

        return collision_list

    def on_update(self, delta_time):
        # Get collision list the new way
        list_length1 = self.new_check_for_collision_with_list(self.player_sprite, self.coin_list)
        # Get collision list the old way
        list_length2 = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)
        # Check the length is the same
        assert len(list_length1) == len(list_length2)


def main():
    """ Main function """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
