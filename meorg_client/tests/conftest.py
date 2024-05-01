class ValueStorage:
    def __init__(self):
        self.data = dict()

    def get(self, key):
        return self.data.get(key, None)

    def set(self, key, value):
        self.data[key] = value
