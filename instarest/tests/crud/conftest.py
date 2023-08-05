from collections.abc import Generator
import pytest
from tests.example_app import initializer

@pytest.fixture(scope="function", autouse=True)
def setup_teardown_function(db) -> Generator:
    initializer.init_db()
    yield
    db.close()
    initializer.wipe_db()