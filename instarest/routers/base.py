from fastapi import Depends, APIRouter, HTTPException
from pydantic import UUID4, BaseModel
from instarest.schemas.base import SchemaBase
from instarest.dependencies import get_db
from instarest.crud.base import CRUDBase
from sqlalchemy.orm import Session
from typing import Generic, TypeVar

SchemaBaseType = TypeVar("SchemaBaseType", bound=SchemaBase)
CRUDBaseType = TypeVar("CRUDBaseType", bound=CRUDBase)


class RouterBase(Generic[SchemaBaseType]):
    class ErrorMessage(BaseModel):
        detail: str = ""

    responses = {
        "400": {"model": ErrorMessage, "description": "Bad or Improper Request"},
        "422": {"model": ErrorMessage, "description": "Unprocessable Entity"},
    }

    def __init__(
        self,
        schema_base: type[SchemaBaseType],
        crud_base: type[CRUDBaseType],
        prefix: str = "/",
        allow_delete: bool = False,
    ):
        """
        Router object with default endpoints to Create, Read, Update, Delete (CRUD),
        based on underlying schema.

        **Parameters**

        * `schema_base`: Class inheriting from SchemaBase, which contains Pydantic validation schemas
        * `crud_base`: Class inheriting from CRUDBase, which contains database CRUD SQLAlchemy-based methods
        * `prefix`: Path prefix following same rules as fastapi.APIRouter (e.g., "/" or "/example"). Defaults to "/".
        * `allow_delete`: Boolean representing whether or not to allow open a deletion endpoint.  Defaults to False.
        """

        assert isinstance(schema_base, SchemaBase)
        assert isinstance(crud_base, CRUDBase)

        self.schema_base = schema_base
        self.crud_base = crud_base
        self.allow_delete = allow_delete
        self.router = APIRouter(
            prefix=prefix, tags=[self.schema_base.get_schema_prefix()]
        )
        self._define_single_item_crud()

    def get_router(self):
        return self.router

    # Single-Item CRUD Endpoints
    def _define_single_item_crud(self):

        def build_id_not_found_error(id):
            return HTTPException(
                status_code=400,
                detail=f"{self.schema_base.Entity.__name__} with id: {id} not found",
            )

        # CREATE
        @self.router.post(
            "/",
            response_model=self.schema_base.Entity,
            responses=type(self).responses,
            summary=f"Create single {self.schema_base.Entity.__name__} object",
            response_description=f"Created {self.schema_base.Entity.__name__} object",
        )
        async def create_entity(
            entity_create: self.schema_base.EntityCreate, db: Session = Depends(get_db)
        ) -> self.schema_base.Entity:
            new_entity_obj: self.schema_base.get_model_type() = self.crud_base.create(
                db, obj_in=entity_create
            )
            return new_entity_obj

        # READ
        @self.router.get(
            "/{id}/",
            response_model=self.schema_base.Entity,
            responses=type(self).responses,
            summary=f"Read single {self.schema_base.Entity.__name__} object",
            response_description=f"Returned {self.schema_base.Entity.__name__} object",
        )
        async def read_entity(
            id: UUID4, db: Session = Depends(get_db)
        ) -> self.schema_base.Entity:
            entity_obj: self.schema_base.get_model_type() = self.crud_base.get(db, id)

            if entity_obj is None:
                raise build_id_not_found_error(id)

            return entity_obj

        # UPDATE
        @self.router.put(
            "/{id}/",
            response_model=self.schema_base.Entity,
            responses=type(self).responses,
            summary=f"Update single {self.schema_base.Entity.__name__} object",
            response_description=f"Updated {self.schema_base.Entity.__name__} object",
        )
        async def update_entity(
            entity_update: self.schema_base.EntityUpdate,
            id: UUID4,
            db: Session = Depends(get_db),
        ) -> self.schema_base.Entity:
            # check to make sure id exists
            entity_obj: self.schema_base.get_model_type() = self.crud_base.get(db, id)
            if not entity_obj:
                raise build_id_not_found_error(id)

            # update the entity and return
            updated_entity_obj: self.schema_base.get_model_type() = (
                self.crud_base.update(db, db_obj=entity_obj, obj_in=entity_update)
            )
            return updated_entity_obj

        # DELETE
        if self.allow_delete:

            @self.router.delete(
                "/{id}/",
                response_model={},
                responses=type(self).responses,
                summary=f"Delete single {self.schema_base.Entity.__name__} object",
                response_description=f"Empty JSON object if successfully deleted",
            )
            async def delete_entity(id: UUID4, db: Session = Depends(get_db)) -> dict:
                
                deleted_obj = self.crud_base.remove(db, id=id)
                if not deleted_obj:
                    raise build_id_not_found_error(id)
                
                return {}


# # ***************START: Multi-Item CRUD Endpoints**************************************
# @router.post(
#     "/",
#     response_model=list[Entity],
#     responses=responses,
#     summary="Create Entities from list",
#     response_description="List of created Entity objects",
# )
# def create_Entity_objects_post(
#     Entities: list[EntityCreate], db: Session = Depends(get_db)
# ) -> list[Entity]:
#     """
#     List of created Entity objects.
#     """

#     # pydantic handles validation
#     return crud.Entity.create_all_using_id(db, obj_in_list=Entities)


# # ***************END: Multi-Item CRUD Endpoints**************************************
