from typing import TypeVar
from pydantic import BaseModel
from sqlalchemy.orm import Session
from instarest import CRUDBase
from .document import DocumentModel
import datetime

DocumentModelType = TypeVar("DocumentModelType", bound=DocumentModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDDocument(CRUDBase[DocumentModelType, CreateSchemaType, UpdateSchemaType]):
    def get_by_created_date_range(
        self, db: Session, *, start_date: datetime.datetime, end_date: datetime.datetime
    ) -> list[DocumentModelType]:
        if not end_date:
            end_date = datetime.datetime.now()

        # pull 100 years of data if no start date is provided
        if not start_date:
            start_date = end_date - datetime.timedelta(days=36500)

        return (
            db.query(self.model)
            .filter(self.model.original_created_time.between(start_date, end_date))
            .all()
        )
