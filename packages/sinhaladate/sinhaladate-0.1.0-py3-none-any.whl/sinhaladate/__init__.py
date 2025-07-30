"""
SinhalaPy - A Python library for parsing and formatting Sinhala dates and times.

This library provides functionality to parse natural language date expressions
in Sinhala and format datetime objects into Sinhala text.

Example:
    >>> from sinhalapy import parse, format_sinhala_dates
    >>> parse("හෙට උදේ 10.30ට")
    datetime.datetime(2024, 12, 16, 10, 30)
    >>> format_sinhala_dates(datetime.datetime.now())
    '2024 දෙසැම්බර් 15 වැනිදා, සිකුරාදා, 02:30 ප.ව.'
"""

from .dates import parse, format_sinhala_dates, SinhalaDateError, ParseResult
from .utils import (
    is_valid_sinhala_date,
    extract_date_components,
    get_sinhala_calendar_info,
    format_relative_time,
    get_sinhala_month_names,
    get_sinhala_day_names,
    get_sinhala_ordinal_names,
    normalize_sinhala_text,
)

__version__ = "0.1.0"
__author__ = "Ravindu Pabasara Karunarathna"
__email__ = "karurpabe@gmail.com"

__all__ = [
    "parse",
    "format_sinhala_dates", 
    "SinhalaDateError",
    "ParseResult",
    "is_valid_sinhala_date",
    "extract_date_components",
    "get_sinhala_calendar_info",
    "format_relative_time",
    "get_sinhala_month_names",
    "get_sinhala_day_names",
    "get_sinhala_ordinal_names",
    "normalize_sinhala_text",
]