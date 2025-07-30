from enum import Enum
from typing import List, Optional

from ...utils.from_camel_case_base_model import FromCamelCaseBaseModel


class EvaluationParams(Enum):
    INPUT = "input"
    ACTUAL_OUTPUT = "actual output"
    EXPECTED_OUTPUT = "expected output"
    CONTEXT = "context"
    RETRIEVAL_CONTEXT = "retrieval context"
    # TOOLS_CALLED = 'tools called'
    # EXPECTED_TOOLS = 'expected tools'


class MetricTypeBase(FromCamelCaseBaseModel):
    name: str
    criteria: Optional[str] = None
    evaluation_steps: Optional[List[str]] = None
    evaluation_params: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    source: Optional[str] = None
    description: Optional[str] = None
    documentation_url: Optional[str] = None


class MetricType(MetricTypeBase):
    id: str
    organization_id: Optional[str] = None
    created_at: str
    deleted_at: Optional[str] = None
