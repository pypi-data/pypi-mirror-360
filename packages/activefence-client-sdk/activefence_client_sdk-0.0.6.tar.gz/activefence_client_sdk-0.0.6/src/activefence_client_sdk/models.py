from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    PROMPT = "prompt"
    RESPONSE = "response"


class Actions(str, Enum):
    BLOCK = "BLOCK"
    DETECT = "DETECT"
    MASK = "MASK"
    NO_ACTION = ""


class SpanDetection(BaseModel):
    start: int
    end: int
    explanation: str


class DetectionResults(BaseModel):
    type: str
    score: float
    span: Optional[SpanDetection] = None


class ErrorResponse(BaseModel):
    violation: str
    status: int
    type: str
    message: str


class EvaluateMessageResponse(BaseModel):
    correlation_id: str
    action: Actions
    action_text: Optional[str] = None
    detections: list[DetectionResults] = Field(default_factory=list)
    errors: list[ErrorResponse] = Field(default_factory=list)


class AnalysisContext(BaseModel):
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    provider: Optional[str] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    platform: Optional[str] = None


@dataclass(frozen=True)
class CustomField:
    name: str
    value: Union[str, int, float, bool, list[str]]

    def __hash__(self) -> int:
        """Custom hash method that handles unhashable values by converting them to strings."""
        # Convert the value to a string representation for hashing
        # this is a workaround to handle unhashable values like lists and dicts
        value_str = str(self.value)
        return hash((self.name, value_str))

    def to_dict(self) -> dict[str, Union[str, int, float, bool, list[str]]]:
        return {self.name: self.value}
