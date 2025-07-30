from pymongo import MongoClient
from bson import ObjectId
from typing import Generic, TypeVar, List, Type
from pydantic.v1 import BaseModel
from sharedkernel.string_extentions import camel_to_snake

T = TypeVar("T", bound=BaseModel)


class MongoGenericRepository(Generic[T]):
    def __init__(self, database: MongoClient, model: Type[T]):
        self.database = database
        self.__collection_name = camel_to_snake(model.__name__)
        self.collection = self.database[self.__collection_name]
        self.model = model

    def _map_to_model(self, document: dict) -> T:
        document["id"] = str(document.pop("_id"))
        return self.model.model_validate(document)

    def find_one(self, id: str) -> T:
        query = {"_id": ObjectId(id), "is_deleted": False}
        result = self.collection.find_one(query)
        return self._map_to_model(result) if result else None   

    def insert_one(self, data: T) -> str:
        delattr(data, "id")
        result = self.collection.insert_one(data.dict())
        return str(result.inserted_id)

    def insert_many(self, data: List[T]) -> List[str]:
        data_list = [delattr(d.dict(), "id") for d in data]
        result = self.collection.insert_many(data_list)
        return [str(id_) for id_ in result.inserted_ids]

    def update_one(self, id: str, data: T) -> int:
        delattr(data, "id")
        query = {"_id": ObjectId(id)}
        result = self.collection.update_one(query, {"$set": data.dict()})
        return result.modified_count

    def delete_one(self, id: str) -> int:
        query = {"_id": ObjectId(id)}
        result = self.collection.delete_one(query)
        return result.deleted_count

    def get_all(self, page_number=1, page_size=10) -> List[T]:
        skip_count = (page_number - 1) * page_size
        query = {"is_deleted": False}
        result = self.collection.find(query).skip(skip_count).limit(page_size)
        return [self._map_to_model(doc) for doc in result]
