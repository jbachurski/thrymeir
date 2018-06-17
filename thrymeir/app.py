import logging

import pyglet

import letterbox
import level
import states


# noinspection PyMethodOverriding,PyAbstractClass
class App(pyglet.window.Window):
    """
    HOW GOOD PROGRAMMING PRACTICES DO NOT DISPROVE, BUT SUPPORT, THE USE OF GOD OBJECTS [READ MORE >>]
    """

    # TODO: investigate: why 30 updates per second?
    tps = 30

    def __init__(self):
        super().__init__(256, 256, resizable=True)
        self.set_minimum_size(168, 64)  # Go figure.

        self.scene_width, self.scene_height = 256, 256
        self.letterbox = letterbox.LetterboxViewport(self, self.scene_width, self.scene_height)

        self.key_state = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.key_state)

        self.game_time_clock = pyglet.clock.Clock()
        pyglet.clock.schedule(self.game_time_clock.tick)
        self.game_time_clock.schedule_interval(lambda dt: self.on_update(dt), 1 / self.tps)

        pyglet.resource.path = ['res/img', 'res/lvl']
        pyglet.resource.reindex()

        self.entities_image = pyglet.resource.image('entities.png')
        self.tileset_image = pyglet.resource.image('tileset.png')

        self.state_manager = states.StateManager(level.Level(self))

        logging.info(f"New app created: {self}")

    def run(self):
        logging.info("Running main loop.")
        self.activate()
        pyglet.app.run()

    def on_update(self, dt):
        self.state_manager.current.update()

    def on_draw(self):
        with self.letterbox.draw():
            self.state_manager.current.draw()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    App().run()
