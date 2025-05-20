from typing import Dict
import os
import pytest
from pytest import StashKey, CollectReport

phase_report_key = StashKey[Dict[str, CollectReport]]()

# Set dev mode
os.environ["MEORG_DEV_MODE"] = "1"


# https://docs.pytest.org/en/latest/example/simple.html#making-test-result-information-available-in-fixtures
@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """Have more information on the status for pytests.

    The results can be used within fixtures
    """
    # execute all other hooks to obtain the report object
    rep = yield

    # store test results for each phase of a call, which can
    # be "setup", "call", "teardown"
    item.stash.setdefault(phase_report_key, {})[rep.when] = rep

    return rep


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
