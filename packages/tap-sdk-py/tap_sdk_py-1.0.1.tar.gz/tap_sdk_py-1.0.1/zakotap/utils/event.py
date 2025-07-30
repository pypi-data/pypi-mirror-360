from eventemitter import EventEmitter

class EmitterManager(EventEmitter):
    def __init__(self):
        super().__init__()
        self._events = {}

    def on(self, event: str, listener):
        if event not in self._events:
            self._events[event] = []
        self._events[event].append(listener)
        super().on(event, listener)

    def emit(self, event: str, *args, **kwargs):
        if event in self._events:
            for listener in self._events[event]:
                listener(*args, **kwargs)
        super().emit(event, *args, **kwargs)
