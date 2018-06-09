
__all__ = ['State', 'StateManager']


class State:
    def on_update(self):
        pass

    def on_draw(self):
        pass


class StateManager:
    def __init__(self):
        self.current: State = State()
