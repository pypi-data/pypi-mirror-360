from typing import Generic, List, TypeVar
from ..utils.utils import make_request, convert_dict_keys_to_snake_case, is_uuid

T = TypeVar("T")


class BaseEntity:
    def __init__(
        self,
        id: str = None,
        created_at: str = None,
        updated_at: str = None,
        deleted_at: str = None,
    ):
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at

    def to_dict(self) -> dict:
        result = {}
        for attr_name, attr_value in self.__dict__.items():
            # Convert snake_case to camelCase for API
            camel_case_name = "".join(
                word.capitalize() if i > 0 else word
                for i, word in enumerate(attr_name.split("_"))
            )

            if attr_value is not None:
                result[camel_case_name] = attr_value

        return result


class BaseRepository(Generic[T]):
    def __init__(self, name: str, endpoint: str, entity_class: T):
        self.name = name
        self.endpoint = endpoint
        self.entity_class = entity_class

    def get(self, query: dict = {}) -> List[T]:
        query_string = "&".join(
            [
                f"filters[{key}]={value}"
                for key, value in query.items()
                if value is not None
            ]
        )
        response = make_request(f"{self.endpoint}?{query_string}")
        if response and "data" in response:
            entities = []
            for item in response["data"]:
                snake_case_item = convert_dict_keys_to_snake_case(item)
                entities.append(self.entity_class(**snake_case_item))
            return entities

        return []

    def get_by_id(self, id: str) -> T:
        response = make_request(f"{self.endpoint}/{id}")
        if response and "data" in response:
            snake_case_item = convert_dict_keys_to_snake_case(response["data"])
            return self.entity_class(**snake_case_item)

        return None

    def get_by_name_or_id(self, name_or_id: str) -> T:
        if is_uuid(name_or_id):
            return self.get_by_id(name_or_id)

        entities = self.get()
        for entity in entities:
            if entity.name == name_or_id:
                return entity

        return None

    def create(self, item: T) -> T:
        item_dict = item.to_dict()

        response = make_request(self.endpoint, "POST", json=item_dict)
        if response and "data" in response:
            snake_case_item = convert_dict_keys_to_snake_case(response["data"])
            return self.entity_class(**snake_case_item)

        return None

    def update_by_id(self, id: str, item: T) -> T:
        item_dict = item.to_dict()

        # Remove id if it exists in the dictionary
        if "id" in item_dict:
            del item_dict["id"]

        response = make_request(f"{self.endpoint}/{id}", "PATCH", json=item_dict)
        if response and "data" in response:
            snake_case_item = convert_dict_keys_to_snake_case(response["data"])
            return self.entity_class(**snake_case_item)

        return None

    def delete_by_id(self, id: str) -> bool:
        response = make_request(f"{self.endpoint}/{id}", "DELETE")
        return response is not None
