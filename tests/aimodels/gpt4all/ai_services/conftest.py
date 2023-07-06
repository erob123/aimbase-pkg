from unittest.mock import create_autospec
from sqlalchemy.orm import Session
from instarest.aimodels.gpt4all import crud

from instarest.aimodels.gpt4all.models.gpt4all_pretrained import Gpt4AllPretrainedModel
from instarest.aimodels.gpt4all.schemas.gpt4all_pretrained import Gpt4AllPretrainedCreate

import pytest

@pytest.fixture(scope="function")
def mock_gpt4all_pretrained_obj(valid_sha256: str, db: Session) -> Gpt4AllPretrainedModel:
    # need to set any attributes that could be validated and only do one wrong at a time
    gpt4all_pretrained_obj = create_autospec(Gpt4AllPretrainedModel)
    gpt4all_pretrained_obj.model_type = "ggml-gpt4all-l13b-snoozy.bin"
    gpt4all_pretrained_obj.uploaded = True

    return gpt4all_pretrained_obj
