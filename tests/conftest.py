import pytest
from app.seeding import drop_create_tables, add_records

@pytest.fixture()
def seed_records():
    drop_create_tables(3, 5)
    add_records()
