from collections.abc import Generator
import pytest
from fastapi.testclient import TestClient
from tests.example_app import app, initializer
from instarest import SessionLocal

# in case you are wondering why we use yield instead of return, check this
# https://stackoverflow.com/questions/64763770/why-we-use-yield-to-get-sessionlocal-in-fastapi-with-sqlalchemy
# wipe then init because we init then wipe at the function level
@pytest.fixture(scope="session")
def db() -> Generator:
    initializer.wipe_db()
    yield SessionLocal()
    initializer.init_db()

@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c
