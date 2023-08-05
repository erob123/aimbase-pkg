from uuid import uuid4
from unittest.mock import patch
from fastapi.testclient import TestClient
from tests.example_app import EmptyTestModel, crud_schemas
from fastapi.encoders import jsonable_encoder


@patch("tests.example_app.test_router.crud_base", autospec=True)
def test_update_valid_request(mock_crud, client: TestClient):
    # setup the request body
    id = uuid4()
    title = "test title 2"
    body = crud_schemas.EntityUpdate(title=title)

    # mock the db get call
    mock_crud.get.return_value = EmptyTestModel(
        id=id, bool_field=True, title="title"
    )

    # mock the db update call
    mock_crud.update.return_value = EmptyTestModel(
        id=id, bool_field=True, title=title
    )

    # make the request
    response = client.put(
        f"/test/{id}/",
        headers={},
        json=jsonable_encoder(body),
    )

    # check that the mock was called with the correct method
    mock_crud.get.assert_called_once()
    mock_crud.update.assert_called_once()

    assert response.status_code == 200
    assert response.json()["id"] == str(id)
    assert response.json()["title"] == title
    assert response.json()["bool_field"] == True


@patch("tests.example_app.test_router.crud_base", autospec=True)
def test_update_invalid_id(mock_crud, client: TestClient):
    # setup the request body
    id = uuid4()
    title = "test title 2"
    body = crud_schemas.EntityUpdate(title=title)

    # mock the db get call
    mock_crud.get.return_value = None

    # make the request
    response = client.put(
        f"/test/{id}/",
        headers={},
        json=jsonable_encoder(body),
    )

    # check that the mock was called with the correct method
    mock_crud.get.assert_called_once()
    mock_crud.update.assert_not_called()

    assert response.status_code == 400
    assert response.json()["detail"] == f"EmptyTest with id: {id} not found"

@patch("tests.example_app.test_router.crud_base", autospec=True)
def test_update_invalid_request(mock_crud, client: TestClient):
    # setup the request body
    id = uuid4()
    body = {"fake": 42}

    # mock the db get call
    mock_crud.get.return_value = EmptyTestModel(
        id=id, bool_field=True, title="title"
    )

    # mock the db update call
    mock_crud.update.return_value = EmptyTestModel(
        id=id, bool_field=True, title="title"
    )

    # make the request
    response = client.put(
        f"/test/{id}/",
        headers={},
        json=jsonable_encoder(body),
    )

    # check that the mock was called with the correct method
    mock_crud.get.assert_called_once()
    mock_crud.update.assert_called_once()

    # nothing should change
    assert response.status_code == 200
    assert response.json()["id"] == str(id)
    assert response.json()["title"] == "title"
    assert response.json()["bool_field"] == True
