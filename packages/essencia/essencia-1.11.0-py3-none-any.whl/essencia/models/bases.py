__all__ = [
    'StrEnum',
    'MongoModel',
    'MongoId',
    'ObjectReferenceId'
]

import json
import logging
import re
import uuid
from collections import UserString
from enum import Enum
from typing import Any, Optional, Type, TypeVar

from bson import json_util, ObjectId
from pydantic import BaseModel, ConfigDict, Field, computed_field
from pydantic_core import core_schema
from typing_extensions import ClassVar, Self, TypedDict
from unidecode import unidecode

logger = logging.getLogger(__name__)


class Names(TypedDict):
    """A class representing a naming convention"""
    singular: str
    plural: str
    key: str
    instance: str


class BaseEnum(Enum):
    """Base class for enums with utility methods, including validation and display."""

    @classmethod
    def __get_pydantic_core_schema__(
            cls, source: Type[Any], handler: Any
    ) -> core_schema.CoreSchema:
        """Pydantic core schema integration for BaseEnum."""
        ...

    @classmethod
    def validate(cls, value: str) -> Self:
        """Validate input and return a member of the enum, raising ValueError if invalid."""
        ...

    @classmethod
    def _missing_(cls, value: str) -> Optional[Self]:
        """Handle missing enum values by attempting to find a match."""
        ...

    @property
    def display(self) -> str:
        """Return a friendly display value for the enum."""
        return self.value

    @classmethod
    def values(cls) -> list:
        """Return a list of all values in the enum."""
        return [member.value for member in cls.__members__.values()]


class StrEnum(BaseEnum):
    """Enum subclass for string-based enums with additional validation and case-insensitive matching."""

    @classmethod
    def __get_pydantic_core_schema__(
            cls, source: Type[Any], handler: Any
    ) -> core_schema.CoreSchema:
        """Define the Pydantic schema for serialized string enums, allowing for validation."""
        return core_schema.no_info_after_validator_function(
                cls.validate,
                core_schema.str_schema(),
                serialization=core_schema.plain_serializer_function_ser_schema(
                        lambda obj: obj.name,
                        return_schema=core_schema.str_schema()
                )
        )

    @classmethod
    def validate(cls, value: str) -> Self:
        """Validate an input string, attempting a match by value or name, with case-insensitivity."""
        try:
            return cls(value)
        except ValueError:
            try:
                return cls[value.upper()]
            except KeyError:
                raise ValueError(f"'{value}' is not a valid value for {cls.__name__}")

    @classmethod
    def _missing_(cls, value: str) -> Optional[Self]:
        """Find a match for the value in the enum, ignoring case and diacritics."""
        normalized = unidecode(value).lower()
        for member in cls:
            if unidecode(member.value).lower() == normalized:
                return member
        return None


StrEnumType = TypeVar('StrEnumType', bound=StrEnum)


class ObjectReferenceId(UserString):
    """Class representing a reference ID in the format '<collection>.<key>', with validation."""

    PATTERN: ClassVar[str] = r'(?P<collection>\w+)\.(?P<key>\w+)'

    def __init__(self, value: str):
        """Initialize and validate a reference ID, raising ValueError if invalid."""
        if result := re.match(self.PATTERN, value):
            data = result.groupdict()
            self.collection = data['collection']
            self.key = data['key']
        else:
            raise ValueError(
                    f"'{value}' is not a valid object reference. Expected format '<collection>.<key>'"
            )
        super().__init__(value)

    @classmethod
    def __get_pydantic_core_schema__(
            cls, source: Type[Any], handler: Any
    ) -> core_schema.CoreSchema:
        """Define the Pydantic schema for ObjectReferenceId, allowing for validation."""
        return core_schema.no_info_after_validator_function(
                cls.validate,
                core_schema.str_schema(),
                serialization=core_schema.plain_serializer_function_ser_schema(
                        lambda obj: obj.data if hasattr(obj, 'data') else str(obj),
                        return_schema=core_schema.str_schema()
                )
        )

    @classmethod
    def validate(cls, value: str) -> Self:
        """Validate an ObjectReferenceId, returning the instance if valid."""
        if isinstance(value, cls):
            return value
        return cls(value)


class MongoId(str):
    """String wrapper for MongoDB ObjectId with validation, ensuring valid ObjectId format."""

    @classmethod
    def __get_pydantic_core_schema__(
            cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        """Define the Pydantic schema for MongoId, allowing for validation against ObjectId."""
        return core_schema.json_or_python_schema(
                json_schema=core_schema.str_schema(),
                python_schema=core_schema.union_schema([
                        core_schema.is_instance_schema(ObjectId),
                        core_schema.chain_schema([
                                core_schema.str_schema(),
                                core_schema.no_info_plain_validator_function(cls.validate)
                        ])
                ]),
                serialization=core_schema.plain_serializer_function_ser_schema(
                        lambda x: str(x)
                )
        )

    @classmethod
    def validate(cls, value: Any) -> ObjectId:
        """Validate and convert the input to an ObjectId, raising ValueError if invalid."""
        if not ObjectId.is_valid(value):
            raise ValueError(f"'{value}' is not a valid MongoDB ObjectId.")
        return ObjectId(value)


from .async_models import AsyncModelMixin


class MongoModel(BaseModel, AsyncModelMixin):
    """Base model integrating Pydantic with MongoDB, providing a class interface for CRUD operations.
    
    This class includes both sync and async operations. The AsyncModelMixin provides
    async methods like afind(), asave(), aupdate(), etc.
    """

    COLLECTION_NAME: ClassVar[Optional[str]] = None
    SEARCH_FIELDS: ClassVar[Optional[set[str]]] = None
    EXCLUDED_FIELDS: ClassVar[set[str]] = set()
    NAMES: ClassVar[Optional[Names]] = None

    DATABASE: ClassVar[Optional[Any]] = None  # Will be set by consuming applications

    model_config = ConfigDict(
            extra='allow',
            populate_by_name=False,
            arbitrary_types_allowed=True
    )

    mongo_id: Optional[MongoId] = Field(None, alias='_id')
    key: str = Field(default_factory=lambda: uuid.uuid4().hex)

    @classmethod
    def get_database(cls):
        """Get the database instance. Must be implemented by consuming applications."""
        if cls.DATABASE is None:
            raise NotImplementedError(
                "DATABASE must be set on the model class or get_database must be overridden"
            )
        return cls.DATABASE

    def as_json(self, **kwargs) -> dict:
        """Serialize the model to a JSON-compatible dictionary, excluding specified fields."""
        return json_util.loads(self.model_dump_json(**kwargs))

    def model_dump_json(self, *args, **kwargs) -> str:
        """Dump the model data as a JSON string with custom configurations, excluding None values."""
        config = {
                'exclude': self.EXCLUDED_FIELDS,
                'by_alias': True,
                'exclude_none': True
        }
        config.update(kwargs)
        data: dict = json_util.loads(super().model_dump_json(*args, **config))
        return json.dumps(data)

    @computed_field(repr=False)
    @property
    def search(self) -> str:
        """Generate a searchable string from specified fields, normalizing the output."""
        data = ' '.join(
                [v for v in (getattr(self, field, '') for field in self.SEARCH_FIELDS or []) if v]
        )
        return ' '.join(unidecode(f"{self} {data}").lower().split())

    @classmethod
    def find(cls, query: dict) -> list[Self]:
        """Execute a MongoDB find query and return a list of model instances."""
        try:
            docs = cls.get_database().find(cls.validate_collection_name(), query)
            return [cls(**doc) for doc in docs]
        except Exception as e:
            logger.error(f"Error finding {cls.__name__} documents: {e}")
            return []

    @classmethod
    def count(cls, query: dict) -> int:
        """Execute a MongoDB count_documents query and return the count."""
        try:
            collection = cls.get_database().get_collection(cls.validate_collection_name())
            return collection.count_documents(query)
        except Exception as e:
            logger.error(f"Error counting {cls.__name__} documents: {e}")
            return 0

    @classmethod
    def find_sorted(cls, query: dict, sort: list = None, limit: int = None) -> list[Self]:
        """Execute a MongoDB find query with sorting and limiting options.

        Args:
            query: MongoDB query dict
            sort: List of (field, direction) tuples, e.g. [('date', -1)]
            limit: Maximum number of results

        Returns:
            List of model instances
        """
        try:
            collection = cls.get_database().get_collection(cls.validate_collection_name())
            cursor = collection.find(query)

            if sort:
                cursor = cursor.sort(sort)
            if limit:
                cursor = cursor.limit(limit)

            return [cls(**doc) for doc in cursor]
        except Exception as e:
            logger.error(f"Error finding sorted {cls.__name__} documents: {e}")
            return []

    @classmethod
    def find_one(cls, query: dict) -> Optional[Self]:
        """Execute a MongoDB find_one query and return a single model instance or None."""
        try:
            data = cls.get_database().find_one(cls.validate_collection_name(), query)
            return cls(**data) if data else None
        except Exception as e:
            logger.error(f"Error finding {cls.__name__} document: {e}")
            return None

    @classmethod
    def validate_collection_name(cls) -> str:
        """Ensure COLLECTION_NAME is defined, raising ValueError if not."""
        if not cls.COLLECTION_NAME:
            raise ValueError("COLLECTION_NAME is not defined.")
        return cls.COLLECTION_NAME

    def exist(self) -> Optional[Self]:
        return self.find_one({'search': self.search})

    def save_self(self, **kwargs) -> Self:
        """Save the current instance to the database."""
        data = self.as_json(**kwargs)
        result = self.get_database().save_one(self.COLLECTION_NAME, data)
        if result:
            return type(self)(**result)
        return None

    def delete_self(self) -> None:
        self.get_database().delete_one(self.COLLECTION_NAME, self.objectId)

    def update_self(self, updates) -> Self:
        self.get_database().update_one(self.COLLECTION_NAME, self.objectId, updates)
        return self.find_one(self.objectId)

    def find_self(self):
        if self.mongo_id:
            return self.find_one(self.objectId)
        return None

    @classmethod
    def save_many(cls, objects: list[Self], **kwargs) -> list[Self]:
        data = cls.get_database().save_many(cls.COLLECTION_NAME, [i.as_json(**kwargs) for i in objects])
        return [cls(**i) for i in data]

    @property
    def objectId(self):
        return {'_id': self.mongo_id}

    @classmethod
    def search_query(cls, **kwargs) -> dict:
        return kwargs