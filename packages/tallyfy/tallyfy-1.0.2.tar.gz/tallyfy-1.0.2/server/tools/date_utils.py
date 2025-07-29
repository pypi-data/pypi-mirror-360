"""
Date and time extraction utilities for parsing natural language dates from user input.
"""

import re
import dateparser
from datetime import datetime, timedelta
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class DateExtractor:
    """Utility class for extracting dates from natural language text."""

    def __init__(self):
        """Initialize the DateExtractor with common patterns."""
        # Common time expressions mapping
        self.time_mappings = {
            'midday': '12:00 PM',
            'noon': '12:00 PM',
            'midnight': '12:00 AM',
            'morning': '9:00 AM',
            'afternoon': '2:00 PM',
            'evening': '6:00 PM',
            'night': '8:00 PM'
        }

        # Specific deadline extraction patterns
        self.deadline_patterns = [
            r"(?:deadline|due)\s+(?:is\s+)?(.+?)(?:\s+with\s|\s+and\s|$)",
            r"by\s+(.+?)(?:\s+with\s|\s+and\s|$)",
            r"before\s+(.+?)(?:\s+with\s|\s+and\s|$)",
            r"until\s+(.+?)(?:\s+with\s|\s+and\s|$)",
        ]

    def extract_date_from_text(self, text: str) -> Tuple[Optional[str], str]:
        """
        Extract date/time from text and return cleaned text.

        Args:
            text: Input text that may contain date/time information

        Returns:
            Tuple of (extracted_datetime_string, cleaned_text)
            extracted_datetime_string is in "YYYY-mm-dd HH:mm:ss" format or None
        """
        if not text:
            return None, text

        logger.debug(f"Extracting date from text: {text}")

        # First try specific deadline patterns
        for pattern in self.deadline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_text = match.group(1).strip()
                logger.debug(f"Found deadline pattern: {date_text}")

                # Parse the extracted date text
                parsed_date = self._parse_date_with_fallbacks(date_text)
                if parsed_date:
                    # Remove the deadline phrase from the original text
                    cleaned_text = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
                    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
                    return parsed_date, cleaned_text

        # Try to find dates within the text using broader patterns
        # Look for "next [day]", "tomorrow", specific dates, etc.
        date_patterns = [
            r"next\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)(?:\s+at\s+(?:\d{1,2}(?::\d{2})?\s*(?:am|pm)?|midday|noon|midnight|morning|afternoon|evening|night)|\s+\d{1,2}\s*(?:am|pm))?",
            r"tomorrow(?:\s+(?:at\s+)?(?:morning|afternoon|evening|night|midday|noon|midnight|\d{1,2}(?::\d{2})?\s*(?:am|pm)?|\d{1,2}am|\d{1,2}pm))?",
            r"(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)(?:\s+at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?|\s+\d{1,2}\s*(?:am|pm))?",
            r"\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2}:\d{2})?",
            r"(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:st|nd|rd|th)?(?:\s+\d{4})?(?:\s+at\s+\d{1,2}:\d{2}\s*(?:am|pm)?)?",
            r"(?:in\s+)?\d{1,2}\s+(?:days?|weeks?|months?)",
            r"after\s+\d{1,2}\s+(?:days?|weeks?|months?)",
            r"\d{1,2}/\d{1,2}/\d{4}(?:\s+\d{1,2}:\d{2}(?::\d{2})?\s*(?:am|pm)?)?",
            r"(?:for\s+)?(?:next\s+)?\w+day\s+\d{1,2}(?:am|pm)",
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_candidate = match.group(0)
                parsed_date = self._parse_date_with_fallbacks(date_candidate)
                if parsed_date:
                    logger.debug(f"Found date candidate: {date_candidate} -> {parsed_date}")
                    # Remove the date from the text
                    cleaned_text = re.sub(re.escape(date_candidate), "", text, flags=re.IGNORECASE).strip()
                    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
                    return parsed_date, cleaned_text

        logger.debug("No date found in text")
        return None, text

    def _parse_date_with_fallbacks(self, date_text: str) -> Optional[str]:
        """
        Parse a date string using multiple fallback approaches.

        Args:
            date_text: Text that potentially contains a date/time

        Returns:
            Formatted datetime string in "YYYY-mm-dd HH:mm:ss" format or None
        """
        if not date_text.strip():
            return None

        # Try manual parsing for common patterns first
        manual_result = self._manual_date_parse(date_text)
        if manual_result:
            return manual_result

        # Preprocess the text
        processed_text = self._preprocess_date_text(date_text)
        logger.debug(f"Preprocessed: '{date_text}' -> '{processed_text}'")

        # Try multiple parsing approaches
        for attempt in range(3):
            try:
                if attempt == 0:
                    # First attempt: strict parsing with future preference
                    parsed_dt = dateparser.parse(
                        processed_text,
                        settings={
                            'PREFER_DATES_FROM': 'future',
                            'RETURN_AS_TIMEZONE_AWARE': False,
                            'STRICT_PARSING': True,
                        }
                    )
                elif attempt == 1:
                    # Second attempt: more flexible parsing
                    parsed_dt = dateparser.parse(
                        processed_text,
                        settings={
                            'PREFER_DATES_FROM': 'future',
                            'RETURN_AS_TIMEZONE_AWARE': False,
                            'STRICT_PARSING': False,
                        }
                    )
                else:
                    # Third attempt: try with current date as base
                    parsed_dt = dateparser.parse(
                        processed_text,
                        settings={
                            'RETURN_AS_TIMEZONE_AWARE': False,
                            'STRICT_PARSING': False,
                        }
                    )

                if parsed_dt:
                    # Validate the parsed date makes sense
                    now = datetime.now()

                    # If the date is more than 2 years in the future, it's probably wrong
                    if parsed_dt.year > now.year + 2:
                        logger.debug(f"Date too far in future: {parsed_dt}")
                        continue

                    # If no time was specified and we got midnight, set reasonable default
                    if (parsed_dt.hour == 0 and parsed_dt.minute == 0 and
                            'midnight' not in processed_text.lower() and
                            not re.search(r'\d{1,2}:\d{2}|00:00', date_text)):
                        parsed_dt = parsed_dt.replace(hour=9, minute=0, second=0)

                    result = parsed_dt.strftime("%Y-%m-%d %H:%M:%S")
                    logger.debug(f"Successfully parsed '{date_text}' -> '{result}' (attempt {attempt + 1})")
                    return result

            except Exception as e:
                logger.debug(f"Parsing attempt {attempt + 1} failed for '{date_text}': {e}")
                continue

        logger.warning(f"All parsing attempts failed for '{date_text}'")
        return None

    def _manual_date_parse(self, date_text: str) -> Optional[str]:
        """
        Manually parse common date patterns that dateparser struggles with.

        Args:
            date_text: Raw date text

        Returns:
            Formatted datetime string or None
        """
        text = date_text.lower().strip()
        now = datetime.now()

        # Handle "next [weekday]" patterns
        next_weekday_match = re.search(
            r'next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)(?:\s+at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?|\s+(\d{1,2})\s*(am|pm)|\s+at\s+(midday|noon|midnight|morning|afternoon|evening|night))?',
            text)
        if next_weekday_match:
            weekday_name = next_weekday_match.group(1)
            hour_part = next_weekday_match.group(2) or next_weekday_match.group(5)
            minute_part = next_weekday_match.group(3) or "0"
            am_pm = next_weekday_match.group(4) or next_weekday_match.group(6)

            weekdays = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4, 'saturday': 5,
                        'sunday': 6}
            target_weekday = weekdays[weekday_name]

            # Calculate next occurrence of this weekday
            days_ahead = target_weekday - now.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7

            target_date = now + timedelta(days=days_ahead)

            # Parse time if provided
            if hour_part:
                hour = int(hour_part)
                minute = int(minute_part) if minute_part else 0

                if am_pm:
                    if am_pm.lower() == 'pm' and hour != 12:
                        hour += 12
                    elif am_pm.lower() == 'am' and hour == 12:
                        hour = 0

                target_date = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            elif am_pm and am_pm.lower() in ['midday', 'noon']:
                target_date = target_date.replace(hour=12, minute=0, second=0, microsecond=0)
            elif am_pm and am_pm.lower() == 'midnight':
                target_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            elif am_pm and am_pm.lower() in self.time_mappings:
                # Convert named time to hour
                time_str = self.time_mappings[am_pm.lower()].replace(' ', '')
                try:
                    time_obj = datetime.strptime(time_str, "%I:%M%p").time()
                    target_date = target_date.replace(hour=time_obj.hour, minute=time_obj.minute, second=0,
                                                      microsecond=0)
                except:
                    target_date = target_date.replace(hour=9, minute=0, second=0, microsecond=0)
            else:
                target_date = target_date.replace(hour=9, minute=0, second=0, microsecond=0)

            result = target_date.strftime("%Y-%m-%d %H:%M:%S")
            logger.debug(f"Manual parse: '{date_text}' -> '{result}'")
            return result

        # Handle "tomorrow" patterns
        tomorrow_match = re.search(r'tomorrow(?:\s+(morning|afternoon|evening|night|\d{1,2}(?::\d{2})?\s*(?:am|pm)?))?',
                                   text)
        if tomorrow_match:
            target_date = now + timedelta(days=1)
            time_part = tomorrow_match.group(1) if tomorrow_match.group(1) else None

            if time_part:
                if time_part in self.time_mappings:
                    # Convert to standard time format
                    time_str = self.time_mappings[time_part].replace(' ', '')  # Remove space from "12:00 PM"
                    try:
                        time_obj = datetime.strptime(time_str, "%I:%M%p").time()
                        target_date = target_date.replace(hour=time_obj.hour, minute=time_obj.minute, second=0,
                                                          microsecond=0)
                    except:
                        target_date = target_date.replace(hour=9, minute=0, second=0, microsecond=0)
                else:
                    # Try to parse time directly
                    time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', time_part)
                    if time_match:
                        hour = int(time_match.group(1))
                        minute = int(time_match.group(2)) if time_match.group(2) else 0
                        am_pm = time_match.group(3)

                        if am_pm:
                            if am_pm.lower() == 'pm' and hour != 12:
                                hour += 12
                            elif am_pm.lower() == 'am' and hour == 12:
                                hour = 0

                        target_date = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    else:
                        target_date = target_date.replace(hour=9, minute=0, second=0, microsecond=0)
            else:
                target_date = target_date.replace(hour=9, minute=0, second=0, microsecond=0)

            result = target_date.strftime("%Y-%m-%d %H:%M:%S")
            logger.debug(f"Manual parse: '{date_text}' -> '{result}'")
            return result

        return None

    def _preprocess_date_text(self, date_text: str) -> str:
        """
        Preprocess date text to handle common expressions.

        Args:
            date_text: Raw date text

        Returns:
            Preprocessed date text
        """
        text = date_text.strip()

        # Handle common time expressions
        for expression, replacement in self.time_mappings.items():
            text = re.sub(r'\b' + expression + r'\b', replacement, text, flags=re.IGNORECASE)

        # Normalize time formats
        text = re.sub(r'(\d{1,2})\s*(pm|am)', r'\1 \2', text, flags=re.IGNORECASE)
        text = re.sub(r'\bat\s+(\d{1,2})\s*(pm|am)', r'at \1 \2', text, flags=re.IGNORECASE)

        # Handle "3PM" without space
        text = re.sub(r'(\d{1,2})(pm|am)', r'\1 \2', text, flags=re.IGNORECASE)

        return text

    def extract_task_info(self, user_input: str) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Extract task title, description, and deadline from user input.

        Args:
            user_input: Full user input text

        Returns:
            Tuple of (title, description, deadline)
        """
        # Extract deadline first to clean the text
        deadline, cleaned_input = self.extract_date_from_text(user_input)

        # Try to match different task creation patterns
        patterns = [
            # "Create a task called [title] with description [desc]"
            (r"create\s+a\s+task\s+(?:called\s+)([^\"']+?)\s+with\s+description\s+(.+)", 2),
            # "Create a task [title] due/by..."
            (r"create\s+a\s+task\s+([^\"']+?)(?:\s+(?:due|by)|\s*$)", 1),
            # "Task: [title]"
            (r"task:\s*(.+)", 1),
            # "[title] due/by..."
            (r"(.+?)\s+(?:due|by)(?:\s|$)", 1),
            # Fallback: use cleaned input
            (r"(.+)", 1),
        ]

        for pattern, groups in patterns:
            match = re.search(pattern, cleaned_input, re.IGNORECASE)
            if match:
                if groups == 2:
                    title = match.group(1).strip()
                    description = match.group(2).strip()
                    return title, description, deadline
                else:
                    title = match.group(1).strip()
                    if len(title) > 1:  # Ensure meaningful title
                        return title, None, deadline

        # Final fallback
        return cleaned_input or user_input, None, deadline