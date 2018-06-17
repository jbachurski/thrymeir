import typing


__all__ = ['State', 'StateManager']


class State:
    def update(self):
        pass

    def draw(self):
        pass


class StateManager:
    def __init__(self, initial: State):
        self._stack = [initial]
        self.current: State = self._stack[0]

    def push(self, state: State):
        self._stack.append(state)
        self.current = self._stack[-1]

    def pop(self):
        if len(self._stack) <= 1:
            raise RuntimeError("Operation causes depletion of state stack")
        self.current = self._stack[-2]
        return self._stack.pop()
