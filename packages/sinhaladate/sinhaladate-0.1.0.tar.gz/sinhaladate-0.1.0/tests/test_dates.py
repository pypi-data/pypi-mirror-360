import pytest
import datetime
from sinhaladate import parse, format_sinhala_dates, SinhalaDateError


class TestParse:
    """Test cases for the parse function."""

    def test_relative_days(self):
        """Test parsing of relative day expressions."""
        now = datetime.datetime.now()
        
        # Test today
        result = parse("අද")
        assert result is not None
        assert result.date() == now.date()
        
        # Test tomorrow
        result = parse("හෙට")
        assert result is not None
        assert result.date() == now.date() + datetime.timedelta(days=1)
        
        # Test yesterday
        result = parse("ඊයේ")
        assert result is not None
        assert result.date() == now.date() - datetime.timedelta(days=1)
        
        # Test day after tomorrow
        result = parse("අනිද්දා")
        assert result is not None
        assert result.date() == now.date() + datetime.timedelta(days=2)
        
        # Test day before yesterday
        result = parse("පෙරේදා")
        assert result is not None
        assert result.date() == now.date() - datetime.timedelta(days=2)

    def test_days_of_week(self):
        """Test parsing of day of week expressions."""
        now = datetime.datetime.now()
        current_weekday = now.weekday()
        
        # Test current day
        day_names = ["සඳුදා", "අඟහරුවාදා", "බදාදා", "බ්‍රහස්පතින්දා", "සිකුරාදා", "සෙනසුරාදා", "ඉරිදා"]
        result = parse(day_names[current_weekday])
        assert result is not None
        assert result.date() == now.date()

    def test_ordinal_dates(self):
        """Test parsing of ordinal date expressions."""
        now = datetime.datetime.now()
        
        # Test 15th
        result = parse("පහළොස්වෙනිදා")
        assert result is not None
        assert result.day == 15
        
        # Test 1st
        result = parse("පළවෙනිදා")
        assert result is not None
        assert result.day == 1
        
        # Test 30th
        result = parse("තිස්වෙනිදා")
        assert result is not None
        assert result.day == 30

    def test_time_expressions(self):
        """Test parsing of time expressions."""
        now = datetime.datetime.now()
        
        # Test morning time
        result = parse("උදේ 10.30ට")
        assert result is not None
        assert result.hour == 10
        assert result.minute == 30
        
        # Test afternoon time
        result = parse("සවස 3යි")
        assert result is not None
        assert result.hour == 15
        assert result.minute == 0
        
        # Test night time
        result = parse("රාත්‍රී 9ට පමණ")
        assert result is not None
        assert result.hour == 21
        assert result.minute == 0

    def test_combined_expressions(self):
        """Test parsing of combined date and time expressions."""
        # Test tomorrow morning
        result = parse("හෙට උදේ 10.30ට")
        assert result is not None
        assert result.hour == 10
        assert result.minute == 30
        
        # Test next Friday
        result = parse("ලබන සිකුරාදා")
        assert result is not None
        assert result.weekday() == 4  # Friday

    def test_invalid_expressions(self):
        """Test that invalid expressions return None."""
        invalid_expressions = [
            "invalid text",
            "",
            "random words",
            "12345",
            "පෙබරවාරි තිස්වෙනිදා",  # February 30th (impossible date)
        ]
        
        for expr in invalid_expressions:
            result = parse(expr)
            assert result is None

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test with extra whitespace
        result = parse("  අද  ")
        assert result is not None
        
        # Test with mixed case (should still work)
        result = parse("අද")
        assert result is not None


class TestFormatSinhalaDates:
    """Test cases for the format_sinhala_dates function."""

    def test_default_formatting(self):
        """Test default date formatting."""
        test_date = datetime.datetime(2024, 12, 25, 19, 30)
        result = format_sinhala_dates(test_date)
        
        # Should contain year, month, day, and time
        assert "2024" in result
        assert "දෙසැම්බර්" in result
        assert "25" in result
        assert "ප.ව." in result

    def test_custom_formatting(self):
        """Test custom format strings."""
        test_date = datetime.datetime(2024, 12, 25, 19, 30)
        
        # Test just day name
        result = format_sinhala_dates(test_date, "%S_A විතර")
        assert "බදාදා" in result
        
        # Test year only
        result = format_sinhala_dates(test_date, "%Y")
        assert result == "2024"
        
        # Test month and day
        result = format_sinhala_dates(test_date, "%S_B %d")
        assert "දෙසැම්බර් 25" in result

    def test_time_formatting(self):
        """Test time-specific formatting."""
        # Test AM time
        am_date = datetime.datetime(2024, 12, 25, 9, 30)
        result = format_sinhala_dates(am_date, "%I:%M %p")
        assert "පෙ.ව." in result
        
        # Test PM time
        pm_date = datetime.datetime(2024, 12, 25, 19, 30)
        result = format_sinhala_dates(pm_date, "%I:%M %p")
        assert "ප.ව." in result

    def test_ordinal_suffix(self):
        """Test ordinal suffix formatting."""
        test_date = datetime.datetime(2024, 12, 25, 19, 30)
        result = format_sinhala_dates(test_date, "%d %S_Do")
        assert "25 වැනිදා" in result

    def test_all_months(self):
        """Test that all months can be formatted correctly."""
        months = [
            (1, "ජනවාරි"),
            (2, "පෙබරවාරි"),
            (3, "මාර්තු"),
            (4, "අප්‍රේල්"),
            (5, "මැයි"),
            (6, "ජූනි"),
            (7, "ජූලි"),
            (8, "අගෝස්තු"),
            (9, "සැප්තැම්බර්"),
            (10, "ඔක්තෝබර්"),
            (11, "නොවැම්බර්"),
            (12, "දෙසැම්බර්"),
        ]
        
        for month_num, expected_name in months:
            test_date = datetime.datetime(2024, month_num, 1)
            result = format_sinhala_dates(test_date, "%S_B")
            assert result == expected_name

    def test_all_days(self):
        """Test that all days of the week can be formatted correctly."""
        days = [
            (0, "සඳුදා"),
            (1, "අඟහරුවාදා"),
            (2, "බදාදා"),
            (3, "බ්‍රහස්පතින්දා"),
            (4, "සිකුරාදා"),
            (5, "සෙනසුරාදා"),
            (6, "ඉරිදා"),
        ]
        
        for day_num, expected_name in days:
            # Create a date that falls on this weekday
            test_date = datetime.datetime(2024, 1, 1)  # Start with Jan 1, 2024
            while test_date.weekday() != day_num:
                test_date += datetime.timedelta(days=1)
            
            result = format_sinhala_dates(test_date, "%S_A")
            assert result == expected_name


class TestSinhalaDateError:
    """Test cases for the SinhalaDateError exception."""

    def test_exception_inheritance(self):
        """Test that SinhalaDateError inherits from ValueError."""
        assert issubclass(SinhalaDateError, ValueError)

    def test_exception_creation(self):
        """Test that SinhalaDateError can be created with a message."""
        error = SinhalaDateError("Test error message")
        assert str(error) == "Test error message"


if __name__ == "__main__":
    pytest.main([__file__]) 