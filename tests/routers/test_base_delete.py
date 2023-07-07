from uuid import uuid4
from unittest.mock import patch
from fastapi.testclient import TestClient
from tests.example_app import EmptyTestModel


@patch("tests.example_app.test_router.crud_base", autospec=True)
def test_delete_valid_id(mock_crud, client: TestClient):
    # setup the request body
    id = uuid4()

    # mock the db call
    mock_crud.remove.return_value = EmptyTestModel(
        id=id, bool_field=False, title="test"
    )

    # make the request
    response = client.delete(
        f"/test/{id}/",
        headers={},
    )

    # check that the mock was called with the correct method
    mock_crud.remove.assert_called_once()

    assert response.status_code == 200
    assert response.json() == {}


@patch("tests.example_app.test_router.crud_base", autospec=True)
def test_delete_invalid_id(mock_crud, client: TestClient):
    # setup the request body
    id = uuid4()

    # mock the db call for bad id
    mock_crud.remove.return_value = None

    # make the request
    response = client.delete(
        f"/test/{id}/",
        headers={},
    )

    # check that the mock was called with the correct method
    mock_crud.remove.assert_called_once()

    assert response.status_code == 400
    assert response.json()["detail"] == f"EmptyTest with id: {id} not found"
