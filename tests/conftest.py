import pytest
from app.seeding import trunc_and_seed

@pytest.fixture()
def seed_records():
    trunc_and_seed()
