from typing import Optional

from ...utils.from_camel_case_base_model import FromCamelCaseBaseModel


class TestCaseBase(FromCamelCaseBaseModel):
    """
    Base model for a test case.

    Attributes:
        test_id (str): ID of the test.
        input (str): Input for the test case.
        expected_output (Optional[str]): Expected output for the test case.
        context (Optional[str]): Context for the test case.
        source (Optional[str]): Source of the test case.
        strategy (Optional[str]): Strategy for the test case.
        variant (Optional[str]): Variant for the test case.
        reviewed_by_id (Optional[str]): ID of the user who reviewed the test case.
    """

    test_id: str
    input: Optional[str] = None
    expected_output: Optional[str] = None
    context: Optional[str] = None
    source: Optional[str] = None
    strategy: Optional[str] = None
    variant: Optional[str] = None
    reviewed_by_id: Optional[str] = None
    goal: Optional[str] = None
    scenario: Optional[str] = None
    userPersona: Optional[str] = None
    maxIterations: Optional[int] = None
    initialPrompt: Optional[str] = None
    stoppingCriterias: Optional[list[str]] = None


class TestCase(TestCaseBase):
    """
    Model for a test case, including database identifiers and timestamps.

    Attributes:
        id (str): Unique identifier for the test case.
        created_at (str): Creation timestamp.
        deleted_at (Optional[str]): Deletion timestamp, if deleted.
    """

    id: str
    created_at: str
    deleted_at: Optional[str] = None
