# Import all the models, so that Base has them before being
# imported by Alembic
# pylint: disable=unused-import
from instarest.db.base_class import DeclarativeBase  # noqa
from instarest.aimodels.bertopic.models.bertopic_embedding_pretrained import BertopicEmbeddingPretrainedModel # noqa
from instarest.aimodels.bertopic.models.bertopic_trained import BertopicTrainedModel # noqa
from instarest.aimodels.bertopic.models.document import DocumentModel # noqa
from instarest.aimodels.bertopic.models.document_embedding_computation import DocumentEmbeddingComputationModel # noqa
from instarest.aimodels.bertopic.models.document_bertopic_trained_model import DocumentBertopicTrainedModel # noqa
from instarest.aimodels.gpt4all.models.gpt4all_pretrained import Gpt4AllPretrainedModel # noqa
