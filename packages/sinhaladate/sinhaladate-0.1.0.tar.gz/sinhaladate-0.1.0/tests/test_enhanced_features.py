import pytest
import datetime
from sinhaladate import (
    parse, 
    ParseResult, 
    normalize_sinhala_text,
    is_valid_sinhala_date
)


class TestParseResult:
    """Test the new ParseResult class and detailed parsing."""

    def test_parse_with_details(self):
        """Test parsing with return_details=True."""
        result = parse("හෙට උදේ 10.30ට", return_details=True)
        
        assert isinstance(result, ParseResult)
        assert result.datetime is not None
        assert "relative_day" in result.components
        assert result.components["relative_day"] == "හෙට"
        assert "time_of_day" in result.components
        assert result.components["time_of_day"] == "උදේ"
        assert result.original_text == "හෙට උදේ 10.30ට"

    def test_parse_failure_with_details(self):
        """Test parsing failure with return_details=True."""
        result = parse("invalid text", return_details=True)
        
        assert isinstance(result, ParseResult)
        assert result.datetime is None
        assert len(result.warnings) > 0
        assert result.original_text == "invalid text"

    def test_parse_result_boolean(self):
        """Test ParseResult boolean behavior."""
        success_result = parse("අද", return_details=True)
        failure_result = parse("invalid", return_details=True)
        
        assert bool(success_result) is True
        assert bool(failure_result) is False

    def test_parse_result_str(self):
        """Test ParseResult string representation."""
        result = parse("හෙට", return_details=True)
        str_repr = str(result)
        
        assert "ParseResult" in str_repr
        assert "datetime=" in str_repr


class Test24HourTime:
    """Test 24-hour time format parsing."""

    def test_24_hour_time(self):
        """Test parsing 24-hour time format."""
        result = parse("14:30ට", return_details=True)
        
        assert result.datetime is not None
        assert result.datetime.hour == 14
        assert result.datetime.minute == 30
        assert result.components.get("format") == "24h"

    def test_24_hour_time_with_date(self):
        """Test 24-hour time with date."""
        result = parse("හෙට 15:45ට", return_details=True)
        
        assert result.datetime is not None
        assert result.datetime.hour == 15
        assert result.datetime.minute == 45
        assert result.components.get("format") == "24h"

    def test_invalid_24_hour_time(self):
        """Test invalid 24-hour time."""
        result = parse("25:30ට", return_details=True)
        
        assert result.datetime is not None  # Should still parse the date
        assert "Invalid 24-hour time format" in result.warnings


class TestTextNormalization:
    """Test text normalization features."""

    def test_normalize_common_typos(self):
        """Test normalization of common typos."""
        # Test common typos
        assert normalize_sinhala_text("පලවෙනිදා") == "පළවෙනිදා"
        assert normalize_sinhala_text("නමවෙනිදා") == "නවවෙනිදා"
        assert normalize_sinhala_text("දොලොස්වෙනිදා") == "දොළොස්වෙනිදා"

    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        text = "  හෙට   උදේ   10.30ට  "
        normalized = normalize_sinhala_text(text)
        
        assert normalized == "හෙට උදේ 10.30ට"
        assert "  " not in normalized  # No double spaces

    def test_parse_with_normalization(self):
        """Test that parsing works with normalized text."""
        # Test with common typo
        result1 = parse("පලවෙනිදා")
        result2 = parse("පළවෙනිදා")
        
        assert result1 is not None
        assert result2 is not None
        assert result1.day == result2.day == 1


class TestEnhancedFeatures:
    """Test various enhanced features."""

    def test_warnings_for_ambiguous_expressions(self):
        """Test warnings for ambiguous expressions."""
        # Test day of week without explicit modifier
        result = parse("සිකුරාදා", return_details=True)
        
        if result.datetime and result.datetime.date() != datetime.datetime.now().date():
            # If it's not today, there should be a warning about assuming future date
            assert any("Assuming" in warning for warning in result.warnings)

    def test_month_inference_warning(self):
        """Test warning when month is inferred."""
        result = parse("පහළොස්වෙනිදා", return_details=True)
        
        if "month" not in result.components:
            # If no month was specified, there should be a warning
            assert any("Month not specified" in warning for warning in result.warnings)

    def test_time_context_warning(self):
        """Test warning for time context assumptions."""
        result = parse("රාත්‍රී 9ට", return_details=True)
        
        if result.datetime and result.datetime.hour == 21:
            # If PM was assumed, there should be a warning
            assert any("Assuming PM" in warning for warning in result.warnings)

    def test_component_tracking(self):
        """Test that all components are properly tracked."""
        result = parse("හෙට උදේ 10.30ට", return_details=True)
        
        expected_components = ["relative_day", "time_of_day", "hour", "minute"]
        for component in expected_components:
            assert component in result.components

    def test_backward_compatibility(self):
        """Test that the old API still works."""
        # Test that parse still returns datetime.datetime by default
        result = parse("අද")
        assert isinstance(result, datetime.datetime)
        
        # Test that parse with return_details=False returns datetime.datetime
        result = parse("අද", return_details=False)
        assert isinstance(result, datetime.datetime)


if __name__ == "__main__":
    pytest.main([__file__]) 