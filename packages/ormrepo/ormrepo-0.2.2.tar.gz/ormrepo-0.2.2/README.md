A library using the "Repository" pattern for working with a database. The library is based on Sqlalchemy 2.0 (DeclarativeBase).
Additionally, work with DTO based on pydantic 2.0 schemas (BaseModel)

Main Components:

DatabaseRepository: This is the main class that provides methods for interacting with the database. It includes methods for creating, reading, updating, and deleting data.
The repository supports working with nested models. You just need to describe the model in relationship (sqlalchemy) and pass the instance to the methods of create, update. The library itself will resolve the parent model and child models of any nesting.
You can flexibly configure filtering to get models from the database. All filtering is collected in the function DatabaseRepository._get(). You can add global filters for the entire class (switchable parameter), as well as for a specific repository function.



DTORepository: This class provides methods for working with DTOs, including validation and conversion to and from database models.
This class is a wrapper over the main DataBaseRepository. In our work we often need to transform models into their representations (DTO), especially when working with FastAPI.
This class can do everything a DatabaseRepository can do. He just knows how to work with pydantic schemas.
Important: When working with nested models (relationships), the schema must also be nested, where the field name matches the relationship name in the model, and the field must also be an instance of the class BaseModel.
Example:
```python
class Model1(OrmBase): <- OrmBase(DeclarativeBase)
    id: Mapped[int]
    name: Mapped[str]
    model2: Mapped["Model2"] = relationship("Model2", back_populates="model1")

class Model2(OrmBase):
    id: Mapped[int]
    name: Mapped[str]
    model1_id: Mapped[int]
    model1: Mapped["Model1"] = relationship("Model1", back_populates="model2")
    
class Schema1(BaseModel):
    id: int
    name: str
class Schema2(BaseModel):
    id: int
    name: str
    model1: Schema1 <- important field name and instance BaseModel
```
ConfigORM: This class is a global configuration class. You can change the configuration at any time.
Limit for outputting records from the database if no local limit is set when working with the repository.
Global filters for models. These filters are applied to all queries for all tables. Don't worry, if the table doesn't have such a field, it will simply be discarded and won't give an error. This filter can be enabled or disabled at any time in a repository instance.
For example, the most common filter: {'is_active': True}.

# Example of work:
```python
from pydantic import BaseModel
from sqlalchemy import Sequence
from sqlalchemy.orm import joinedload

from ormrepo.db_settings import config_orm
from ormrepo.orm import DatabaseRepository, DTORepository
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker

from tests.models import TModel1, TModel1Schema, RelationModel1, TModel1Rel1Schema, RelationModel1Schema
from tests.session import uri

config_orm.configure(limit=100, global_filters={'is_active': True})

engine: AsyncEngine = create_async_engine(uri, echo=True)
sessionmaker = async_sessionmaker(engine)


async def get_session() -> AsyncSession:
    """Session Manager"""
    async with sessionmaker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```
## Example of working with a repository:
```python
async def get_models() -> Sequence[TModel1]:
    async with get_session() as session:
        repo = DatabaseRepository(TModel1,
                                  session,
                                  local_filters=[TModel1.name.like("%model%")],
                                  use_global_filters=False)
        res = await repo.get_many(filters=[TModel1.id == 1],
                                  load=[joinedload(TModel1.relation_models)],
                                  relation_filters={RelationModel1: [RelationModel1.id.in_([1, 2, 3])]},
                                  offset=10,
                                  limit=10)
        return res
```
## Example of working with a DTO:
```python
async def get_dto() -> list[BaseModel]:
    async with get_session() as session:
        repo = DTORepository(DatabaseRepository(TModel1, session),
                             TModel1Schema)
        res = await repo.get_many(filters=[TModel1.id > 1])
        return res
```
## Example of creation
```python
async def create_dto() -> TModel1Rel1Schema:
    async with get_session() as session:
        repo = DTORepository(DatabaseRepository(TModel1, session),
                             TModel1Rel1Schema)
        return await repo.create(TModel1Rel1Schema(name='test',
                                                   serial=1,
                                                   relation_models=[
                                                       RelationModel1Schema(),
                                                       RelationModel1Schema(),
                                                       RelationModel1Schema()
                                                   ]))
```
## Example of update
```python
async def update_dto() -> TModel1Rel1Schema:
    async with get_session() as session:
        repo = DTORepository(DatabaseRepository(TModel1, session),
                             TModel1Rel1Schema)
        return await repo.update(1, TModel1Rel1Schema(name='test_new',
                                                      relation_models=None))
"""
Important:
There will be two changes to the databases here.
1: Model TModel1 name changes. Since in the update function, only those fields that are explicitly set are updated.
Because model_dump(exclude_unset=True).
2: Since we explicitly set relation_models, all records from the related table related to this record will be deleted!!!
"""
```