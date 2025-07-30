"""
Utility functions for SinhalaPy library.
"""

import datetime
import re
from typing import Optional, List, Dict, Any
from .dates import parse, format_sinhala_dates, MONTHS, DAYS_OF_WEEK, ORDINAL_DAYS


def normalize_sinhala_text(text: str) -> str:
    """
    Normalize Sinhala text by removing extra spaces and common variations.
    
    Args:
        text (str): Input Sinhala text
        
    Returns:
        str: Normalized text
    """
    if not text:
        return text
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Common variations and typos
    replacements = {
        'පලවෙනිදා': 'පළවෙනිදා',  # Common typo
        'නමවෙනිදා': 'නවවෙනිදා',  # Common typo
        'දොලොස්වෙනිදා': 'දොළොස්වෙනිදා',  # Common typo
        'පහලොස්වෙනිදා': 'පහළොස්වෙනිදා',  # Common typo
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text


def is_valid_sinhala_date(text: str) -> bool:
    """
    Check if a text string contains valid Sinhala date expressions.
    
    Args:
        text (str): Text to check
        
    Returns:
        bool: True if the text contains valid Sinhala date expressions
        
    Examples:
        >>> is_valid_sinhala_date("අද")
        True
        >>> is_valid_sinhala_date("hello world")
        False
    """
    if not text:
        return False
    
    # Check for any known Sinhala date words
    all_words = set(MONTHS.keys()) | set(DAYS_OF_WEEK.keys()) | set(ORDINAL_DAYS.keys())
    
    for word in all_words:
        if word in text:
            return True
    
    return False


def extract_date_components(text: str) -> Dict[str, Any]:
    """
    Extract date components from Sinhala text without parsing to datetime.
    
    Args:
        text (str): Sinhala text to analyze
        
    Returns:
        Dict[str, Any]: Dictionary containing found components
        
    Examples:
        >>> extract_date_components("හෙට උදේ 10.30ට")
        {'relative_day': 'හෙට', 'time_of_day': 'උදේ', 'hour': 10, 'minute': 30}
    """
    components = {}
    
    # Check for relative days
    from .dates import RELATIVE_DAYS
    for word, offset in RELATIVE_DAYS.items():
        if word in text:
            components['relative_day'] = word
            components['relative_offset'] = offset
            break
    
    # Check for days of week
    for word, day_index in DAYS_OF_WEEK.items():
        if word in text:
            components['day_of_week'] = word
            components['weekday_index'] = day_index
            break
    
    # Check for months
    for word, month_num in MONTHS.items():
        if word in text:
            components['month'] = word
            components['month_number'] = month_num
            break
    
    # Check for ordinal days
    for word, day_num in ORDINAL_DAYS.items():
        if word in text:
            components['ordinal_day'] = word
            components['day_number'] = day_num
            break
    
    # Check for time of day
    from .dates import TIME_OF_DAY
    for word, am_pm in TIME_OF_DAY.items():
        if word in text:
            components['time_of_day'] = word
            components['am_pm'] = am_pm
            break
    
    return components


def get_sinhala_calendar_info(year: int, month: int) -> Dict[str, Any]:
    """
    Get Sinhala calendar information for a specific month.
    
    Args:
        year (int): Year
        month (int): Month (1-12)
        
    Returns:
        Dict[str, Any]: Calendar information including month name, days, etc.
        
    Examples:
        >>> get_sinhala_calendar_info(2024, 12)
        {'year': 2024, 'month': 12, 'month_name': 'දෙසැම්බර්', 'days_in_month': 31, ...}
    """
    if not (1 <= month <= 12):
        raise ValueError("Month must be between 1 and 12")
    
    # Get month name
    from .dates import _REVERSE_MONTHS
    month_name = _REVERSE_MONTHS.get(month, '')
    
    # Get days in month
    import calendar
    days_in_month = calendar.monthrange(year, month)[1]
    
    # Get first day of month
    first_day = datetime.date(year, month, 1)
    first_weekday = first_day.weekday()
    
    # Get Sinhala day name for first day
    from .dates import _REVERSE_DAYS
    first_day_name = _REVERSE_DAYS.get(first_weekday, '')
    
    return {
        'year': year,
        'month': month,
        'month_name': month_name,
        'days_in_month': days_in_month,
        'first_day_weekday': first_weekday,
        'first_day_name': first_day_name,
    }


def format_relative_time(dt: datetime.datetime, reference: Optional[datetime.datetime] = None) -> str:
    """
    Format a datetime as a relative time expression in Sinhala.
    
    Args:
        dt (datetime.datetime): The datetime to format
        reference (datetime.datetime, optional): Reference time (defaults to now)
        
    Returns:
        str: Relative time expression in Sinhala
        
    Examples:
        >>> format_relative_time(datetime.datetime.now() + datetime.timedelta(days=1))
        'හෙට'
        >>> format_relative_time(datetime.datetime.now() - datetime.timedelta(days=1))
        'ඊයේ'
    """
    if reference is None:
        reference = datetime.datetime.now()
    
    delta = dt - reference
    days_diff = delta.days
    
    if days_diff == 0:
        return "අද"
    elif days_diff == 1:
        return "හෙට"
    elif days_diff == -1:
        return "ඊයේ"
    elif days_diff == 2:
        return "අනිද්දා"
    elif days_diff == -2:
        return "පෙරේදා"
    else:
        # For other cases, use the full date format
        return format_sinhala_dates(dt)


def get_sinhala_month_names() -> List[str]:
    """
    Get list of all Sinhala month names.
    
    Returns:
        List[str]: List of Sinhala month names
        
    Examples:
        >>> get_sinhala_month_names()
        ['ජනවාරි', 'පෙබරවාරි', 'මාර්තු', ...]
    """
    return list(MONTHS.keys())


def get_sinhala_day_names() -> List[str]:
    """
    Get list of all Sinhala day names.
    
    Returns:
        List[str]: List of Sinhala day names
        
    Examples:
        >>> get_sinhala_day_names()
        ['සඳුදා', 'අඟහරුවාදා', 'බදාදා', ...]
    """
    return list(DAYS_OF_WEEK.keys())


def get_sinhala_ordinal_names() -> List[str]:
    """
    Get list of all Sinhala ordinal day names.
    
    Returns:
        List[str]: List of Sinhala ordinal day names
        
    Examples:
        >>> get_sinhala_ordinal_names()
        ['පළවෙනිදා', 'දෙවෙනිදා', 'තුන්වෙනිදා', ...]
    """
    return list(ORDINAL_DAYS.keys()) 