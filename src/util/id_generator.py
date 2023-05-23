

class IdGen:
    """

    Singleton to generate IDs to Simulation Elements

    """

    _nextId = 0

    def __new__(self):

        out = self._nextId
        self._nextId += 1

        return out


