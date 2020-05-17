import pytest

from seeds.test import test_seed


@pytest.fixture()
def seed_records():
    test_seed()
