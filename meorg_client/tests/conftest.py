import os
import pytest

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
store.set("experiment_id", os.environ.get("MEORG_EXPERIMENT_ID"))
store.set("model_profile_id", os.environ.get("MEORG_MODEL_PROFILE_ID"))
store.set("model_output_name", os.environ.get("MEORG_MODEL_OUTPUT_NAME"))


@pytest.fixture
def model_profile_id() -> str:
    """Get the experiment ID out of the environment.

    Returns
    -------
    str
        Model Profile ID.
    """
    return os.getenv("MEORG_MODEL_PROFILE_ID")


@pytest.fixture
def experiment_id() -> str:
    """Get the experiment ID out of the environment.

    Returns
    -------
    str
        Experiment ID.
    """
    return os.getenv("MEORG_EXPERIMENT_ID")


@pytest.fixture
def model_output_name() -> str:
    """Get the model output name.

    Returns
    -------
    str
        Model output name.
    """
    return os.getenv("MEORG_MODEL_OUTPUT_NAME") or "meorg-client-model-output"
