from collections import deque


class Command:
    def execute(self):
        pass

    def undo(self):
        pass


class CommandManager:
    def __init__(self, undo_max_limit=2000):
        self._redo_stack = []
        self._undo_stack = deque(maxlen=undo_max_limit)

    def execute(self, command: Command):
        command.execute()
        self._undo_stack.append(command)
        self._redo_stack.clear()

    def undo(self):
        if self._undo_stack:
            command = self._undo_stack.popleft()
            command.undo()
            self._redo_stack.append(command)

    def redo(self):
        if self._redo_stack:
            command = self._redo_stack.pop()
            command.execute()
            self._undo_stack.append(command)
