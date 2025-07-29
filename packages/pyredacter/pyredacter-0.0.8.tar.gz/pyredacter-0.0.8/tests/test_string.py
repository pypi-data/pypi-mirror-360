import pytest

from redact import redact_string

# Define a fixture for common test data
@pytest.fixture
def default_redaction():
    return "*****"

# Parameterized test function
@pytest.mark.parametrize("input_str, expected_output", [
    ("testpassword", "te********rd"),
    ("a", "*****"),
    ("ab", "*****"),
    ("abcd", "*****"),
    ("abcde", "ab*de"),
    ("!@#$%^&*()", "!@******()"),
    ("1234567890", "12******90"),
    ("a1b2c3d4", "a1****d4"),
    ("abcde", "ab*de"),
    ("abcdef", "ab**ef"),
    ("", "*****"),
    ("foo", "*****"),
])
def test_redact_string(default_redaction, input_str, expected_output):
    if len(input_str) <= 4:
        assert redact_string(input_str) == default_redaction
    else:
        assert redact_string(input_str) == expected_output
