import pytest
from datetime import datetime
import json

from gotenberg_client._convert.common import MetadataMixin


def test_metadata_basic():
    """Test basic metadata setting."""
    mixin = MetadataMixin()
    result = mixin.metadata(
        title="Test Document",
        author="Test Author",
        keywords=["test", "document"]
    )

    assert isinstance(result, MetadataMixin)
    assert "metadata" in result._form_data

    metadata = json.loads(result._form_data["metadata"])
    assert metadata["Title"] == "Test Document"
    assert metadata["Author"] == "Test Author"
    assert metadata["Keywords"] == "test, document"


def test_metadata_dates():
    """Test date handling in metadata."""
    mixin = MetadataMixin()
    test_date = datetime(2024, 1, 1, 12, 0)

    result = mixin.metadata(
        creation_date=test_date,
        modification_date=test_date
    )

    metadata = json.loads(result._form_data["metadata"])
    assert metadata["CreationDate"] == "2024-01-01T12:00:00"
    assert metadata["ModDate"] == "2024-01-01T12:00:00"


def test_metadata_trapped():
    """Test trapped status handling."""
    mixin = MetadataMixin()

    # Test boolean values
    result = mixin.metadata(trapped=True)
    metadata = json.loads(result._form_data["metadata"])
    assert metadata["Trapped"] is True

    # Test string values
    result = mixin.metadata(trapped="Unknown")
    metadata = json.loads(result._form_data["metadata"])
    assert metadata["Trapped"] == "Unknown"


def test_metadata_validation():
    """Test metadata validation."""
    mixin = MetadataMixin()

    with pytest.raises(ValueError):
        mixin.metadata(pdf_version=3.0)  # Invalid version

    with pytest.raises(ValueError):
        mixin.metadata(trapped="Invalid")  # Invalid trapped status

    with pytest.raises(ValueError):
        mixin.metadata(keywords=["test,with,comma"])  # Invalid keyword


def test_metadata_empty():
    """Test handling of empty metadata."""
    mixin = MetadataMixin()
    result = mixin.metadata()

    assert "metadata" not in result._form_data


def test_metadata_chaining():
    """Test method chaining."""
    mixin = MetadataMixin()
    result = (
        mixin.metadata(title="First Title")
        .metadata(author="Test Author")
    )

    metadata = json.loads(result._form_data["metadata"])
    assert metadata["Title"] == "First Title"
    assert metadata["Author"] == "Test Author"


@pytest.mark.parametrize("trapped_value,expected", [
    (True, True),
    (False, False),
    ("True", True),
    ("False", False),
    ("Unknown", "Unknown"),
])
def test_metadata_trapped_values(trapped_value, expected):
    """Test various trapped status values."""
    mixin = MetadataMixin()
    result = mixin.metadata(trapped=trapped_value)

    metadata = json.loads(result._form_data["metadata"])
    assert metadata["Trapped"] == expected
