import time
from typing import List, Optional, Type, TypeVar

from pydantic import BaseModel, Field, create_model

T = TypeVar("T", bound="MemoryEntrySchema")


class MetadataSchema(BaseModel):
    source: str = ""
    tags: List[str] = Field(default_factory=list)
    extra: str = "{}"


class MemoryEntrySchema(BaseModel):
    id: str
    content: str
    vector: Optional[List[float]] = None
    type: str = ""
    importance_score: float = 0.0
    metadata: MetadataSchema = Field(default_factory=MetadataSchema)
    created_at: float = Field(default_factory=time.time)
    last_accessed_at: float = Field(default_factory=time.time)

    class Config:
        extra = "allow"


_vector_type_imported = False
try:
    from lancedb.pydantic import vector as lancedb_vector_type

    _vector_type_imported = True
except ImportError:

    def lancedb_vector_type(dim: int):  # Basic fallback
        # print(f"Warning: lancedb.pydantic.vector not found. Using List[float] for vector type with dimension {dim}.")
        return List[float]


def create_dynamic_memory_entry_schema(
    base_schema: Type[MemoryEntrySchema], vector_dimension: int
) -> Type[MemoryEntrySchema]:
    if not issubclass(base_schema, BaseModel):
        raise TypeError("base_schema must be a Pydantic BaseModel subclass")

    if _vector_type_imported:
        vector_field_definition = (
            lancedb_vector_type(vector_dimension),
            Field(..., description=f"Vector embedding of dimension {vector_dimension}"),
        )
    else:
        vector_field_definition = (
            List[float],
            Field(..., description=f"Vector embedding of dimension {vector_dimension}"),
        )

    dynamic_schema_name = f"{base_schema.__name__}WithVector"

    DynamicSchema = create_model(
        dynamic_schema_name,
        vector=vector_field_definition,
        __base__=base_schema,
    )
    return DynamicSchema
