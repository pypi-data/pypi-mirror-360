import pytest
from therix.utils.pii_filter import pii_filter

@pytest.mark.parametrize("text, entities, expected_output", [
    ("John Doe's email is john@example.com", ["PERSON"], "<strong>John Doe's</strong> email is john@example.com"),
    ("Please contact me at john@example.com", ["EMAIL_ADDRESS"], "Please contact me at <strong>john@example.com</strong>"),
    ("Please call 123-456-7890 for assistance", ["PHONE_NUMBER"], "Please call <strong>123-456-7890</strong> for assistance")
])
def test_pii_filter(text, entities, expected_output):
    assert pii_filter(text, entities) == expected_output