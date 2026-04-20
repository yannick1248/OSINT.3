from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, ClassVar, Generic, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

TParams = TypeVar("TParams", bound=BaseModel)
TOutput = TypeVar("TOutput", bound=BaseModel)


class ConfidenceLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class OsintResultStatus(StrEnum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class OsintResult(BaseModel, Generic[TOutput]):
    model_config = ConfigDict(frozen=True)

    result_id: UUID = Field(default_factory=uuid4)
    module: str
    status: OsintResultStatus
    confidence: ConfidenceLevel
    executed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    duration_ms: int = 0
    data: TOutput | None = None
    errors: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class OsintModule(ABC, Generic[TParams, TOutput]):
    """Interface commune à tous les modules OSINT.

    Chaque module concret déclare ses schémas d'entrée/sortie via Pydantic,
    expose un `name` unique et un `description` lisible, puis implémente
    `validate_input` et `execute`.
    """

    name: ClassVar[str]
    description: ClassVar[str]
    input_schema: ClassVar[type[BaseModel]]
    output_schema: ClassVar[type[BaseModel]]
    confidence_levels: ClassVar[tuple[ConfidenceLevel, ...]] = (
        ConfidenceLevel.LOW,
        ConfidenceLevel.MEDIUM,
        ConfidenceLevel.HIGH,
    )

    @abstractmethod
    async def validate_input(self, params: TParams) -> bool: ...

    @abstractmethod
    async def execute(self, params: TParams) -> OsintResult[TOutput]: ...

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema.model_json_schema(),
            "output_schema": self.output_schema.model_json_schema(),
            "confidence_levels": [c.value for c in self.confidence_levels],
        }
