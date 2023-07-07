from uuid import uuid4
from unittest.mock import patch
from fastapi.testclient import TestClient
from tests.example_app import EmptyTestModel, crud_schemas
from fastapi.encoders import jsonable_encoder


@patch("tests.example_app.test_router.crud_base", autospec=True)
def test_create_valid_request(mock_crud, client: TestClient):
    # setup the request body
    title = "test title"
    body = crud_schemas.EntityCreate(title=title)

    # mock the db call
    mock_crud.create.return_value = EmptyTestModel(
        id=uuid4(), bool_field=False, title=title
    )

    # make the request
    response = client.post(
        "/test",
        headers={},
        json=jsonable_encoder(body),
    )

    # check that the mock was called with the correct method
    mock_crud.create.assert_called_once()

    assert response.status_code == 200
    assert response.json()["id"] is not None
    assert response.json()["title"] == title
    assert response.json()["bool_field"] == False


@patch("tests.example_app.test_router.crud_base", autospec=True)
def test_create_empty_request(mock_crud, client: TestClient):
    # setup the request body
    body = {}

    # mock the db call
    mock_crud.create.return_value = EmptyTestModel(
        id=uuid4(), bool_field=False, title="title"
    )

    # make the request
    response = client.post(
        "/test",
        headers={},
        json=jsonable_encoder(body),
    )

    # check that the mock was called with the correct method
    mock_crud.create.assert_called_once()

    assert response.status_code == 200
    assert response.json()["id"] is not None
    assert response.json()["title"] == "title"
    assert response.json()["bool_field"] == False


@patch("tests.example_app.test_router.crud_base", autospec=True)
def test_create_invalid_request(mock_crud, client: TestClient):
    # setup the request body
    body = None

    # make the request
    response = client.post(
        "/test",
        headers={},
        json=jsonable_encoder(body),
    )

    # check that the mock was not called
    mock_crud.create.assert_not_called()

    assert response.status_code == 422
    assert response.json()["detail"] is not None