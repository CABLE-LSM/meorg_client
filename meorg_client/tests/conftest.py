import os

# Set dev mode
os.environ["MEORG_DEV_MODE"] = "1"


class ValueStorage:
    def __init__(self):
        self.data = dict()

    def get(self, key):
        return self.data.get(key, None)

    def set(self, key, value):
        self.data[key] = value

    def __repr__(self):
        lines = ""
        for k, v in self.data.items():
            lines += f"{k} = {v}\n"

        return lines


# Add some things to the store
store = ValueStorage()
store.set("email", os.environ.get("MEORG_EMAIL"))
store.set("password", os.environ.get("MEORG_PASSWORD"))
store.set("model_output_id", os.environ.get("MEORG_MODEL_OUTPUT_ID"))
