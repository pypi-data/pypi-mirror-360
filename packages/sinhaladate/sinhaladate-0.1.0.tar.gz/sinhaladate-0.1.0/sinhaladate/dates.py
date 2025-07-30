from __future__ import annotations

import re
import datetime
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class ParseResult:
    """Result of parsing a Sinhala date/time expression."""
    datetime: Optional[datetime.datetime]
    components: Dict[str, Any]
    warnings: list[str]
    original_text: str
    
    def __bool__(self) -> bool:
        return self.datetime is not None
    
    def __str__(self) -> str:
        if self.datetime:
            return f"ParseResult(datetime={self.datetime}, warnings={self.warnings})"
        return f"ParseResult(None, warnings={self.warnings})"


class SinhalaDateError(ValueError):
    """Custom exception for parsing errors."""
    pass


# --- DATA MAPS ---
MONTHS = {'ජනවාරි': 1, 'පෙබරවාරි': 2, 'මාර්තු': 3, 'අප්‍රේල්': 4, 'මැයි': 5, 'ජූනි': 6, 'ජූලි': 7, 'අගෝස්තු': 8,
          'සැප්තැම්බර්': 9, 'ඔක්තෝබර්': 10, 'නොවැම්බර්': 11, 'දෙසැම්බර්': 12}
DAYS_OF_WEEK = {'සඳුදා': 0, 'අඟහරුවාදා': 1, 'බදාදා': 2, 'බ්‍රහස්පතින්දා': 3, 'සිකුරාදා': 4, 'සෙනසුරාදා': 5, 'ඉරිදා': 6}
RELATIVE_DAYS = {'අද': 0, 'හෙට': 1, 'අනිද්දා': 2, 'ඉන් අනිද්දා':3,'ඉන්අනිද්දා':3, 'ඊයේ': -1, 'පෙරේදා': -2, 'පෙරෙයිදා': -2}
MODIFIERS = {'පසුගිය': -1, 'ගිය': -1, 'ලබන': 1, 'එළඹෙන': 1, 'එන':1}
TIME_OF_DAY = {'උදේ': 'AM', 'උදෑසන': 'AM', 'සවස': 'PM', 'හවස': 'PM', 'රාත්‍රී': 'PM', 'රෑ': 'PM', 'දහවල්': 'PM',
               'පාන්දර': 'AM'}
# In sinhalapy/sinhalapy/dates.py, add this new map

# Maps Sinhala ordinal day names to the day of the month
ORDINAL_DAYS = {
    'පළවෙනිදා': 1, 'පලවෙනිදා': 1,
    'දෙවෙනිදා': 2,
    'තුන්වෙනිදා': 3,
    'හතරවෙනිදා': 4,
    'පස්වෙනිදා': 5,
    'හයවෙනිදා': 6,
    'හත්වෙනිදා': 7,
    'අටවෙනිදා': 8,
    'නවවෙනිදා': 9, 'නමවෙනිදා': 9,
    'දහවෙනිදා': 10,
    'එකොළොස්වෙනිදා': 11,
    'දොළොස්වෙනිදා': 12, 'දොලොස්වෙනිදා': 12,
    'දහතුන්වෙනිදා': 13,
    'දාහතරවෙනිදා': 14,
    'පහළොස්වෙනිදා': 15, 'පහලොස්වෙනිදා': 15,
    'දාසයවෙනිදා': 16,
    'දාහත්වෙනිදා': 17,
    'දහඅටවෙනිදා': 18,
    'දහනවවෙනිදා': 19,
    'විසිවෙනිදා': 20,
    'විසිඑක්වෙනිදා': 21,
    'විසිදෙවෙනිදා': 22,
    'විසිතුන්වෙනිදා': 23,
    'විසිහතරවෙනිදා': 24,
    'විසිපස්වෙනිදා': 25,
    'විසිහයවෙනිදා': 26,
    'විසිහත්වෙනිදා': 27,
    'විසිඅටවෙනිදා': 28,
    'විසිනවවෙනිදා': 29,
    'තිස්වෙනිදා': 30,
    'තිස්එක්වෙනිදා': 31,
}

_REVERSE_MONTHS = {v: k for k, v in MONTHS.items()}
_REVERSE_DAYS = {v: k for k, v in DAYS_OF_WEEK.items()}

TIME_REGEX = re.compile(
    r"(?P<time_of_day_word>\b(?:{})\b)?\s*(?P<hour>\d{{1,2}})(?P<separator>[:.]|යි)?(?P<minute>\d{{2}})?(?P<am_pm_marker>\s*(?:ට|ට පමණ))?".format(
        '|'.join(TIME_OF_DAY.keys())), re.VERBOSE | re.UNICODE)

# Regex for 24-hour format
TIME_24H_REGEX = re.compile(
    r"(?P<hour>\d{1,2}):(?P<minute>\d{2})(?P<am_pm_marker>\s*(?:ට|ට පමණ))?", re.VERBOSE | re.UNICODE)


def parse(text: str, return_details: bool = False) -> datetime.datetime | None | ParseResult:
    """
    Parse Sinhala date and time expressions into datetime objects.
    
    This function can parse various Sinhala date expressions including:
    - Relative dates: "අද" (today), "හෙට" (tomorrow), "ඊයේ" (yesterday)
    - Days of week: "සඳුදා" (Monday), "ලබන සිකුරාදා" (next Friday)
    - Ordinal dates: "පහළොස්වෙනිදා" (15th), "ජූලි හතරවෙනිදා" (July 4th)
    - Time expressions: "උදේ 10.30ට" (10:30 AM), "සවස 3යි" (3:00 PM)
    - Combined expressions: "හෙට උදේ 10.30ට" (tomorrow morning at 10:30)
    
    Args:
        text (str): The Sinhala text to parse
        return_details (bool): If True, return ParseResult with detailed information
        
    Returns:
        datetime.datetime | None | ParseResult: Parsed datetime object, ParseResult with details, or None if parsing fails
        
    Examples:
        >>> parse("අද")
        datetime.datetime(2024, 12, 15, 0, 0)  # Today at midnight
        
        >>> parse("හෙට උදේ 10.30ට")
        datetime.datetime(2024, 12, 16, 10, 30)  # Tomorrow at 10:30 AM
        
        >>> parse("invalid text")
        None
        
        >>> parse("හෙට උදේ 10.30ට", return_details=True)
        ParseResult(datetime=..., components={...}, warnings=[], original_text="හෙට උදේ 10.30ට")
    """
    if not text or not isinstance(text, str):
        if return_details:
            return ParseResult(None, {}, ["Empty or invalid input"], text)
        return None

    # Normalize the text
    from .utils import normalize_sinhala_text
    text = normalize_sinhala_text(text)

    # Check for 24-hour time format first
    time_24h_match = TIME_24H_REGEX.search(text)
    has_24h_time = time_24h_match is not None
    
    # Only proceed if the text contains at least one Sinhala date or time word, or has 24-hour time
    if not (has_24h_time or any(word in text for word in list(MONTHS.keys()) + list(DAYS_OF_WEEK.keys()) + list(ORDINAL_DAYS.keys()) + list(RELATIVE_DAYS.keys()) + list(TIME_OF_DAY.keys()))):
        if return_details:
            return ParseResult(None, {}, ["No Sinhala date/time words found"], text)
        return None

    try:
        now = datetime.datetime.now()
        target_date = now.date()
        date_found = False
        components = {}
        warnings = []

        # Check for relative days first
        for word, offset in RELATIVE_DAYS.items():
            if word in text:
                target_date = now.date() + datetime.timedelta(days=offset)
                date_found = True
                components['relative_day'] = word
                components['relative_offset'] = offset
                break

        if not date_found:
            modifier = 1
            for word, value in MODIFIERS.items():
                if word in text:
                    modifier = value
                    break

            for word, day_index in DAYS_OF_WEEK.items():
                if word in text:
                    current_weekday = now.weekday()
                    if modifier == 1:
                        days_ahead = (day_index - current_weekday + 7) % 7
                        if days_ahead == 0:
                            if any(m in text for m in ["ලබන", "එළඹෙන", "එන"]):
                                days_ahead = 7  # Explicitly "next"
                            else:
                                days_ahead = 0  # Today
                    else:
                        days_behind = (current_weekday - day_index + 7) % 7
                        if days_behind == 0:
                            days_behind = 7
                        days_ahead = -days_behind

                    target_date = now.date() + datetime.timedelta(days=days_ahead)
                    date_found = True
                    components['day_of_week'] = word
                    components['weekday_index'] = day_index
                    components['modifier'] = modifier
                    if modifier == 1 and days_ahead == 7:
                        warnings.append(f"Assuming 'next {word}' (7 days ahead)")
                    elif modifier == 1 and days_ahead > 0:
                        warnings.append(f"Assuming '{word}' is {days_ahead} days ahead")
                    break

        if not date_found:
            sorted_ordinals = sorted(ORDINAL_DAYS.keys(), key=len, reverse=True)
            for word in sorted_ordinals:
                day_number = ORDINAL_DAYS[word]
                if word in text:
                    target_month = now.month
                    target_year = now.year

                    # Check if a month is also mentioned
                    month_found = False
                    for month_word, month_number in MONTHS.items():
                        if month_word in text:
                            target_month = month_number
                            month_found = True
                            # If the parsed date is in a past month, assume it's for next year
                            if target_month < now.month:
                                target_year += 1
                            break

                    # If no month is specified, infer it
                    if not month_found:
                        # If the day has already passed this month, assume next month
                        if day_number < now.day:
                            target_month += 1
                            if target_month > 12:  # Handle year transition
                                target_month = 1
                                target_year += 1

                    try:
                        target_date = datetime.date(target_year, target_month, day_number)
                        date_found = True
                        components['ordinal_day'] = word
                        components['day_number'] = day_number
                        components['month'] = target_month
                        components['year'] = target_year
                        if not month_found:
                            warnings.append(f"Month not specified, assuming {_REVERSE_MONTHS.get(target_month, '')}")
                    except ValueError:
                        # Handle invalid dates like "පෙබරවාරි තිස්වෙනිදා"
                        if return_details:
                            return ParseResult(None, {}, [f"Invalid date: {word} in month {target_month}"], text)
                        return None
                    break  # Stop searching for other ordinals

        # Find time - check 24-hour format first
        time_24h_match = TIME_24H_REGEX.search(text)
        time_match = TIME_REGEX.search(text)
        target_time = datetime.time(0, 0)

        if time_24h_match:
            # Handle 24-hour format
            data = time_24h_match.groupdict()
            hour = int(data['hour'])
            minute = int(data['minute'])
            
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                target_time = datetime.time(hour, minute)
                components['hour'] = hour
                components['minute'] = minute
                components['format'] = '24h'
            else:
                warnings.append("Invalid 24-hour time format")
                target_time = datetime.time(0, 0)  # Default to midnight
        elif time_match:
            data = time_match.groupdict()
            hour = int(data['hour'])
            minute = int(data['minute'] or 0)

            time_of_day_word = data.get('time_of_day_word')
            if time_of_day_word:
                am_pm = TIME_OF_DAY.get(time_of_day_word)
                components['time_of_day'] = time_of_day_word
                components['am_pm'] = am_pm
                if am_pm == 'PM' and 1 <= hour <= 11:
                    hour += 12
                elif am_pm == 'AM' and hour == 12:
                    hour = 0
            else:
                # If no time of day word, assume PM for hours 1-11 if no AM/PM context
                if 1 <= hour <= 11 and ('රාත්‍රී' in text or 'රෑ' in text):
                    hour += 12
                    warnings.append("Assuming PM for night time context")
                elif 1 <= hour <= 11:
                    # Check if any time-of-day words are in the text
                    for word in TIME_OF_DAY.keys():
                        if word in text:
                            components['time_of_day'] = word
                            components['am_pm'] = TIME_OF_DAY[word]
                            break

            target_time = datetime.time(hour, minute)
            components['hour'] = hour
            components['minute'] = minute
        elif not date_found and not time_match and not time_24h_match:
            # If no date and no time was found, the string is unparseable
            if return_details:
                return ParseResult(None, {}, ["No date or time found"], text)
            return None

        result_datetime = datetime.datetime.combine(target_date, target_time)
        
        if return_details:
            return ParseResult(result_datetime, components, warnings, text)
        return result_datetime

    except (ValueError, TypeError):
        if return_details:
            return ParseResult(None, {}, ["Parsing error occurred"], text)
        return None


def format_sinhala_dates(dt: datetime.datetime, format_string: str = "%Y %S_B %d %S_Do, %S_A, %I:%M %p") -> str:
    """
    Format datetime objects into Sinhala text.
    
    This function formats datetime objects using custom format codes that output
    Sinhala text for months, days, and time periods.
    
    Args:
        dt (datetime.datetime): The datetime object to format
        format_string (str): Format string with custom codes
        
    Returns:
        str: Formatted Sinhala text
        
    Format Codes:
        %Y - Year (2024)
        %S_B - Sinhala month name (දෙසැම්බර්)
        %d - Day of month (25)
        %S_A - Sinhala day name (බදාදා)
        %I - Hour in 12-hour format (07)
        %M - Minute (30)
        %p - AM/PM in Sinhala (ප.ව.)
        %S_Do - Ordinal suffix (වැනිදා)
        
    Examples:
        >>> format_sinhala_dates(datetime.datetime(2024, 12, 25, 19, 30))
        '2024 දෙසැම්බර් 25 වැනිදා, බදාදා, 07:30 ප.ව.'
        
        >>> format_sinhala_dates(datetime.datetime(2024, 12, 25), "%S_A විතර")
        'බදාදා විතර'
    """
    if not isinstance(dt, datetime.datetime):
        raise TypeError("dt must be a datetime.datetime object")
        
    output = format_string
    replacements = {
        '%Y': str(dt.year),
        '%S_B': _REVERSE_MONTHS.get(dt.month, ''),
        '%d': str(dt.day),
        '%S_A': _REVERSE_DAYS.get(dt.weekday(), ''),
        '%I': dt.strftime('%I'),
        '%M': dt.strftime('%M'),
        '%p': 'පෙ.ව.' if dt.strftime('%p') == 'AM' else 'ප.ව.',
        '%S_Do': 'වැනිදා',
    }
    for code, value in replacements.items():
        output = output.replace(code, value)
    return output