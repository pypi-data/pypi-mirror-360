import pytest
from pytest_snapshot.plugin import Snapshot


@pytest.fixture(autouse=True)
def set_snapshot_dir(snapshot: Snapshot) -> None:
    snapshot.snapshot_dir = "tests/snapshots"
