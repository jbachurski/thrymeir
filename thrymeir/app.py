import logging

import pyglet

import letterbox
import level
import states


# noinspection PyMethodOverriding,PyAbstractClass
class App(pyglet.window.Window):
    tps = 30
    base_resize_delay = 0.1
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

        pyglet.resource.path = ['res', 'res/tiles']
        pyglet.resource.reindex()

        self.state_manager = states.StateManager(level.Level(self))

        # Set up resizing context
        self.resize_set = None
        self.resize_delay = None

        logging.info(f"New app created: {self}")

    def run(self):
        logging.info("Running main loop.")
        self.activate()
        pyglet.app.run()

    def on_update(self, dt):
        self.state_manager.current.on_update()
        if self.resize_delay is not None:
            if self.resize_delay <= 0:
                self.set_size(self.resize_set, self.resize_set)
                self.resize_delay = self.resize_set = None
            else:
                self.resize_delay -= dt

    def on_draw(self):
        with self.letterbox.draw():
            self.state_manager.current.on_draw()

    def on_resize(self, width, height):
        self.resize_set = width
        self.resize_delay = self.base_resize_delay

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    App().run()
