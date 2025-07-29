from collections import deque


class Command:
    def execute(self):
        return None

    def undo(self):
        return None


class CommandManager:
    def __init__(self, undo_max_limit=5000):
        self._redo_stack = []
        self._undo_stack = deque(maxlen=undo_max_limit)

    def execute(self, command):
        result = command.execute()
        self._undo_stack.append(command)
        self._redo_stack.clear()
        return result

    def undo(self):
        if not self._undo_stack:
            return None
        command = self._undo_stack.popleft()
        result = command.undo()
        self._redo_stack.append(command)
        return result

    def redo(self):
        if not self._redo_stack:
            return None
        command = self._redo_stack.pop()
        result = command.execute()
        self._undo_stack.append(command)
        return result
