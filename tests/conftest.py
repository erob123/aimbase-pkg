from collections.abc import Generator
import random
import pytest
from fastapi.testclient import TestClient
from tests.example_app import app
from instarest import SessionLocal

# in case you are wondering why we use yield instead of return, check this
# https://stackoverflow.com/questions/64763770/why-we-use-yield-to-get-sessionlocal-in-fastapi-with-sqlalchemy
@pytest.fixture(scope="session")
def db() -> Generator:
    yield SessionLocal()

@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c