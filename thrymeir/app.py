import logging

import pyglet

import letterbox
import level
import states


# noinspection PyMethodOverriding
class App(pyglet.window.Window):
    def __init__(self):
        super().__init__(256, 256, resizable=True)
        self.set_minimum_size(168, 64)  # Go figure.

        self.scene_width, self.scene_height = 256, 256
        self.letterbox = letterbox.LetterboxViewport(self, self.scene_width, self.scene_height)

        self.key_state = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.key_state)

        self.game_time_clock = pyglet.clock.Clock(fps_limit=50)
        pyglet.clock.schedule(self.game_time_clock.tick)
        self.game_time_clock.schedule_interval(lambda dt: self.on_update(), 1 / 50)

        pyglet.resource.path = ['img']
        pyglet.resource.reindex()

        self.state = states.StateManager()
        self.state.current = level.Level(self)

        logging.info(f"New app created: {self}")

    def run(self):
        logging.info("Running main loop.")
        self.activate()
        pyglet.app.run()

    def on_update(self):
        self.state.current.on_update()

    def on_draw(self):
        with self.letterbox.draw():
            self.state.current.on_draw()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    App().run()
