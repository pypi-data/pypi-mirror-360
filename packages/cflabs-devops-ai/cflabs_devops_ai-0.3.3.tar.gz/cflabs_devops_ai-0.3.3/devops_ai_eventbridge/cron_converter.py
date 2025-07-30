"""
Natural language to cron expression converter.
"""

import re
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import openai

logger = logging.getLogger(__name__)


class TimeUnit(Enum):
    """Time units for cron expressions."""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class CronConverter:
    """Converts natural language descriptions to cron expressions."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the cron converter with patterns and mappings."""
        # Initialize OpenAI
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
            self.client = openai.OpenAI(api_key=self.openai_api_key)
        else:
            self.client = None
            logger.warning("OpenAI API key not found. Fallback to regex patterns only.")
        
        self.time_patterns = {
            # Rate expressions (check these first)
            r'\bevery\s+(\d+)\s*minutes?\b': self._handle_rate_minutes,
            r'\bevery\s+(\d+)\s*hours?\b': self._handle_rate_hours,
            r'\bevery\s+(\d+)\s*days?\b': self._handle_rate_days,
            r'\bevery\s+(\d+)\s*weeks?\b': self._handle_rate_weeks,
            
            # Minutes
            r'\b(\d+)\s*minutes?\b': self._handle_minutes,
            r'\b(\d+)\s*mins?\b': self._handle_minutes,
            
            # Hours
            r'\b(\d+)\s*hours?\b': self._handle_hours,
            r'\b(\d+)\s*hrs?\b': self._handle_hours,
            
            # Days
            r'\b(\d+)\s*days?\b': self._handle_days,
            
            # Weeks
            r'\b(\d+)\s*weeks?\b': self._handle_weeks,
            
            # Months
            r'\b(\d+)\s*months?\b': self._handle_months,
            
            # Specific times
            r'\b(\d{1,2}):(\d{2})\s*(am|pm)?\b': self._handle_specific_time,
            r'\b(\d{1,2})am\b': self._handle_am_pm_time,
            r'\b(\d{1,2})pm\b': self._handle_am_pm_time,
            
            # Daily patterns
            r'\bdaily\b': self._handle_daily,
            r'\bevery\s+day\b': self._handle_daily,
            
            # Weekly patterns
            r'\bweekly\b': self._handle_weekly,
            r'\bevery\s+week\b': self._handle_weekly,
            r'\bevery\s+(\w+)\s+at\s+(\d{1,2}):(\d{2})\s*(am|pm)?\b': self._handle_weekly_specific,
            r'\bevery\s+(\w+)\s+at\s+(\d{1,2})pm\b': self._handle_weekly_am_pm,
            r'\bevery\s+(\w+)\s+at\s+(\d{1,2})am\b': self._handle_weekly_am_pm,
            
            # Monthly patterns
            r'\bmonthly\b': self._handle_monthly,
            r'\bevery\s+month\b': self._handle_monthly,
            
            # Yearly patterns
            r'\byearly\b': self._handle_yearly,
            r'\bevery\s+year\b': self._handle_yearly,
            
            # Business days
            r'\bweekdays?\b': self._handle_weekdays,
            r'\bweekends?\b': self._handle_weekends,
            
            # Specific days (check these before general patterns)
            r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b': self._handle_specific_day,
        }
        
        self.day_mapping = {
            'monday': 1, 'tuesday': 2, 'wednesday': 3, 'thursday': 4,
            'friday': 5, 'saturday': 6, 'sunday': 0
        }
        
        self.month_mapping = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
    
    def text_to_cron(self, text: str) -> str:
        """
        Convert natural language text to cron expression or rate expression.
        
        Args:
            text: Natural language description of schedule
            
        Returns:
            Cron expression string or rate expression string
        """
        text = text.lower().strip()
        
        # Check for rate expressions first
        rate_expr = self._detect_rate_expression(text)
        if rate_expr:
            return rate_expr
        
        # Check for Indian timezone references
        is_indian_time = any(keyword in text for keyword in ['indian time', 'ist', 'india time', 'indian'])
        
        # Try to match patterns
        for pattern, handler in self.time_patterns.items():
            match = re.search(pattern, text)
            if match:
                try:
                    cron_expr = handler(match, text)
                    if is_indian_time:
                        cron_expr = self._apply_indian_timezone_offset(cron_expr)
                    return cron_expr
                except Exception as e:
                    logger.warning(f"Failed to process pattern {pattern}: {e}")
                    continue
        
        # If no regex pattern matched, try OpenAI
        if self.client:
            logger.info(f"No regex pattern matched for: {text}. Trying OpenAI...")
            try:
                cron_expr = self._generate_cron_with_openai(text)
                if is_indian_time:
                    cron_expr = self._apply_indian_timezone_offset(cron_expr)
                return cron_expr
            except Exception as e:
                logger.warning(f"OpenAI fallback failed: {e}")
        
        # Default to daily at midnight if no pattern matches
        logger.warning(f"No pattern matched for text: {text}. Using default daily schedule.")
        cron_expr = "cron(0 0 * * ? *)"
        if is_indian_time:
            cron_expr = self._apply_indian_timezone_offset(cron_expr)
        return cron_expr
    
    def _detect_rate_expression(self, text: str) -> Optional[str]:
        """
        Detect and convert rate expressions from natural language.
        
        Args:
            text: Natural language description
            
        Returns:
            Rate expression string or None if not a rate expression
        """
        # Patterns for rate expressions
        rate_patterns = [
            (r'\bevery\s+(\d+)\s*minutes?\b', 'minute', 'minutes'),
            (r'\bevery\s+(\d+)\s*hours?\b', 'hour', 'hours'),
            (r'\bevery\s+(\d+)\s*days?\b', 'day', 'days'),
            (r'\bevery\s+(\d+)\s*weeks?\b', 'week', 'weeks'),
        ]
        
        for pattern, singular_unit, plural_unit in rate_patterns:
            match = re.search(pattern, text)
            if match:
                value = int(match.group(1))
                if value < 1:
                    raise ValueError(f"Invalid rate value: {value}")
                
                # Handle weeks specially - convert to days
                if singular_unit == 'week':
                    days = value * 7
                    return f"rate({days} days)"
                
                # Use singular for value=1, plural for values>1
                unit = singular_unit if value == 1 else plural_unit
                return f"rate({value} {unit})"
        
        return None
    
    def _handle_rate_minutes(self, match: re.Match, text: str) -> str:
        """Handle rate expressions for minutes."""
        minutes = int(match.group(1))
        if minutes < 1:
            raise ValueError(f"Invalid minutes: {minutes}")
        
        unit = "minute" if minutes == 1 else "minutes"
        return f"rate({minutes} {unit})"
    
    def _handle_rate_hours(self, match: re.Match, text: str) -> str:
        """Handle rate expressions for hours."""
        hours = int(match.group(1))
        if hours < 1:
            raise ValueError(f"Invalid hours: {hours}")
        
        unit = "hour" if hours == 1 else "hours"
        return f"rate({hours} {unit})"
    
    def _handle_rate_days(self, match: re.Match, text: str) -> str:
        """Handle rate expressions for days."""
        days = int(match.group(1))
        if days < 1:
            raise ValueError(f"Invalid days: {days}")
        
        unit = "day" if days == 1 else "days"
        return f"rate({days} {unit})"
    
    def _handle_rate_weeks(self, match: re.Match, text: str) -> str:
        """Handle rate expressions for weeks."""
        weeks = int(match.group(1))
        if weeks < 1:
            raise ValueError(f"Invalid weeks: {weeks}")
        
        # Convert weeks to days for rate expression
        days = weeks * 7
        return f"rate({days} days)"
    
    def _handle_minutes(self, match: re.Match, text: str) -> str:
        """Handle minute-based intervals."""
        minutes = int(match.group(1))
        if minutes < 1 or minutes > 59:
            raise ValueError(f"Invalid minutes: {minutes}")
        return f"cron(*/{minutes} * * * * *)"
    
    def _handle_hours(self, match: re.Match, text: str) -> str:
        """Handle hour-based intervals."""
        hours = int(match.group(1))
        if hours < 1 or hours > 23:
            raise ValueError(f"Invalid hours: {hours}")
        return f"cron(0 */{hours} * * * *)"
    
    def _handle_days(self, match: re.Match, text: str) -> str:
        """Handle day-based intervals."""
        days = int(match.group(1))
        if days < 1 or days > 31:
            raise ValueError(f"Invalid days: {days}")
        return f"cron(0 0 */{days} * * *)"
    
    def _handle_weeks(self, match: re.Match, text: str) -> str:
        """Handle week-based intervals."""
        weeks = int(match.group(1))
        if weeks < 1 or weeks > 52:
            raise ValueError(f"Invalid weeks: {weeks}")
        return f"cron(0 0 * * */{weeks} *)"
    
    def _handle_months(self, match: re.Match, text: str) -> str:
        """Handle month-based intervals."""
        months = int(match.group(1))
        if months < 1 or months > 12:
            raise ValueError(f"Invalid months: {months}")
        return f"cron(0 0 1 */{months} * *)"
    
    def _handle_specific_time(self, match: re.Match, text: str) -> str:
        """Handle specific time patterns."""
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        
        # Handle AM/PM
        if match.group(3):
            ampm = match.group(3).lower()
            if ampm == 'pm' and hour != 12:
                hour += 12
            elif ampm == 'am' and hour == 12:
                hour = 0
        elif 'pm' in text and hour != 12:
            hour += 12
        elif 'am' in text and hour == 12:
            hour = 0
        
        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            raise ValueError(f"Invalid time: {hour}:{minute}")
        
        return f"cron({minute} {hour} * * ? *)"
    
    def _handle_am_pm_time(self, match: re.Match, text: str) -> str:
        """Handle AM/PM time patterns."""
        hour = int(match.group(1))
        minute = 0  # Default to 0 minutes
        
        # Determine if it's AM or PM from the matched text
        matched_text = match.group(0).lower()
        if 'pm' in matched_text and hour != 12:
            hour += 12
        elif 'am' in matched_text and hour == 12:
            hour = 0
        
        if hour < 0 or hour > 23:
            raise ValueError(f"Invalid hour: {hour}")
        
        return f"cron({minute} {hour} * * ? *)"
    
    def _handle_daily(self, match: re.Match, text: str) -> str:
        """Handle daily patterns."""
        # Check for specific time in the text
        time_match = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm)?', text)
        if time_match:
            return self._handle_specific_time(time_match, text)
        return "cron(0 0 * * ? *)"  # Daily at midnight
    
    def _handle_weekly(self, match: re.Match, text: str) -> str:
        """Handle weekly patterns."""
        # Check for specific day and time
        day_match = re.search(r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', text)
        time_match = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm)?', text)
        
        if day_match and time_match:
            day_num = self.day_mapping[day_match.group(1)]
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            
            # Handle AM/PM
            if time_match.group(3):
                ampm = time_match.group(3).lower()
                if ampm == 'pm' and hour != 12:
                    hour += 12
                elif ampm == 'am' and hour == 12:
                    hour = 0
            
            # For weekly patterns with day-of-week, use ? for day-of-month
            return f"cron({minute} {hour} ? * {day_num} *)"
        
        return "cron(0 0 ? * 0 *)"  # Weekly on Sunday at midnight
    
    def _handle_weekly_specific(self, match: re.Match, text: str) -> str:
        """Handle specific weekly patterns."""
        day = match.group(1).lower()
        hour = int(match.group(2))
        minute = int(match.group(3))
        
        # Handle AM/PM
        if match.group(4):
            ampm = match.group(4).lower()
            if ampm == 'pm' and hour != 12:
                hour += 12
            elif ampm == 'am' and hour == 12:
                hour = 0
        
        day_num = self.day_mapping.get(day)
        if day_num is None:
            raise ValueError(f"Invalid day: {day}")
        
        return f"cron({minute} {hour} ? * {day_num} *)"
    
    def _handle_weekly_day_only(self, match: re.Match, text: str) -> str:
        """Handle weekly patterns with just day name (e.g., 'every friday')."""
        day = match.group(1).lower()
        day_num = self.day_mapping.get(day)
        if day_num is None:
            raise ValueError(f"Invalid day: {day}")
        
        # Default to 9 AM for day-only patterns
        return f"cron(0 9 ? * {day_num} *)"
    
    def _handle_weekly_am_pm(self, match: re.Match, text: str) -> str:
        """Handle weekly patterns with AM/PM times."""
        day = match.group(1).lower()
        hour = int(match.group(2))
        minute = 0  # Default to 0 minutes
        
        # Determine if it's AM or PM from the matched text
        matched_text = match.group(0).lower()
        if 'pm' in matched_text and hour != 12:
            hour += 12
        elif 'am' in matched_text and hour == 12:
            hour = 0
        
        day_num = self.day_mapping.get(day)
        if day_num is None:
            raise ValueError(f"Invalid day: {day}")
        
        # For weekly patterns with day-of-week, use ? for day-of-month
        return f"cron({minute} {hour} ? * {day_num} *)"
    
    def _handle_monthly(self, match: re.Match, text: str) -> str:
        """Handle monthly patterns."""
        # Check for specific day of month
        day_match = re.search(r'\b(\d{1,2})(st|nd|rd|th)?\b', text)
        if day_match:
            day = int(day_match.group(1))
            if day < 1 or day > 31:
                raise ValueError(f"Invalid day of month: {day}")
            return f"cron(0 0 {day} * ? *)"
        
        return "cron(0 0 1 * ? *)"  # Monthly on the 1st
    
    def _handle_yearly(self, match: re.Match, text: str) -> str:
        """Handle yearly patterns."""
        # Check for specific month and day
        month_match = re.search(r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b', text)
        day_match = re.search(r'\b(\d{1,2})(st|nd|rd|th)?\b', text)
        
        if month_match and day_match:
            month = self.month_mapping[month_match.group(1)]
            day = int(day_match.group(1))
            if day < 1 or day > 31:
                raise ValueError(f"Invalid day: {day}")
            return f"cron(0 0 {day} {month} ? *)"
        
        return "cron(0 0 1 1 ? *)"  # Yearly on January 1st
    
    def _handle_weekdays(self, match: re.Match, text: str) -> str:
        """Handle weekdays (Monday-Friday)."""
        time_match = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm)?', text)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            
            # Handle AM/PM
            if time_match.group(3):
                ampm = time_match.group(3).lower()
                if ampm == 'pm' and hour != 12:
                    hour += 12
                elif ampm == 'am' and hour == 12:
                    hour = 0
            
            return f"cron({minute} {hour} ? * 1-5 *)"
        
        return "cron(0 9 ? * 1-5 *)"  # Weekdays at 9 AM
    
    def _handle_weekends(self, match: re.Match, text: str) -> str:
        """Handle weekends (Saturday-Sunday)."""
        time_match = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm)?', text)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            
            # Handle AM/PM
            if time_match.group(3):
                ampm = time_match.group(3).lower()
                if ampm == 'pm' and hour != 12:
                    hour += 12
                elif ampm == 'am' and hour == 12:
                    hour = 0
            
            return f"cron({minute} {hour} ? * 0,6 *)"
        
        return "cron(0 9 ? * 0,6 *)"  # Weekends at 9 AM
    
    def _handle_specific_day(self, match: re.Match, text: str) -> str:
        """Handle specific day of week."""
        day = match.group(1).lower()
        day_num = self.day_mapping[day]
        
        time_match = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm)?', text)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            
            # Handle AM/PM
            if time_match.group(3):
                ampm = time_match.group(3).lower()
                if ampm == 'pm' and hour != 12:
                    hour += 12
                elif ampm == 'am' and hour == 12:
                    hour = 0
            
            return f"cron({minute} {hour} ? * {day_num} *)"
        
        return f"cron(0 9 ? * {day_num} *)"  # Specific day at 9 AM
    
    def validate_cron(self, cron_expression: str) -> bool:
        """
        Validate a cron expression or rate expression.
        
        Args:
            cron_expression: Cron expression or rate expression to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check if it's a rate expression
            if cron_expression.startswith("rate(") and cron_expression.endswith(")"):
                return self._validate_rate_expression(cron_expression)
            
            # Check if it's AWS EventBridge format with cron() wrapper
            if cron_expression.startswith("cron(") and cron_expression.endswith(")"):
                inner_expr = cron_expression[5:-1]  # Remove "cron(" and ")"
                parts = inner_expr.split()
            else:
                # Fallback to standard cron format
                parts = cron_expression.split()
            
            if len(parts) != 6:
                return False
            
            # Basic validation - could be expanded
            for i, part in enumerate(parts):
                if part == '*' or part == '?':
                    continue
                if ',' in part:
                    values = part.split(',')
                    for value in values:
                        if not self._is_valid_field(value, i):
                            return False
                elif '/' in part:
                    range_part, step = part.split('/')
                    if not self._is_valid_field(range_part, i) or not step.isdigit():
                        return False
                elif '-' in part:
                    start, end = part.split('-')
                    if not self._is_valid_field(start, i) or not self._is_valid_field(end, i):
                        return False
                else:
                    if not self._is_valid_field(part, i):
                        return False
            
            return True
        except Exception:
            return False
    
    def _validate_rate_expression(self, rate_expression: str) -> bool:
        """
        Validate a rate expression.
        
        Args:
            rate_expression: Rate expression to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Extract the rate expression from the rate() wrapper
            if rate_expression.startswith("rate(") and rate_expression.endswith(")"):
                inner_expr = rate_expression[5:-1]  # Remove "rate(" and ")"
            else:
                return False
            
            parts = inner_expr.split()
            if len(parts) != 2:
                return False
            
            value_str, unit = parts
            
            # Validate value
            if not value_str.isdigit():
                return False
            
            value = int(value_str)
            if value < 1:
                return False
            
            # Validate unit
            valid_units = ['minute', 'minutes', 'hour', 'hours', 'day', 'days']
            if unit not in valid_units:
                return False
            
            # Check singular/plural consistency
            if value == 1 and unit.endswith('s'):
                return False
            if value > 1 and not unit.endswith('s'):
                return False
            
            return True
        except Exception:
            return False
    
    def _is_valid_field(self, value: str, field_index: int) -> bool:
        """Check if a field value is valid for the given field index."""
        if not value.isdigit():
            return False
        
        num = int(value)
        max_values = [59, 23, 31, 12, 6, 2199]  # minute, hour, day, month, day_of_week, year
        min_values = [0, 0, 1, 1, 0, 1970]
        
        if field_index >= len(max_values):
            return False
        
        return min_values[field_index] <= num <= max_values[field_index]

    def _apply_indian_timezone_offset(self, cron_expression: str) -> str:
        """
        Apply Indian timezone offset (UTC+5:30) to convert to UTC.
        Indian time is 5 hours 30 minutes ahead of UTC, so we subtract this offset.
        """
        try:
            # Rate expressions don't need timezone conversion
            if cron_expression.startswith("rate("):
                return cron_expression
            
            # Extract the cron expression from the cron() wrapper
            if cron_expression.startswith("cron(") and cron_expression.endswith(")"):
                inner_expr = cron_expression[5:-1]  # Remove "cron(" and ")"
            else:
                return cron_expression
            
            parts = inner_expr.split()
            if len(parts) != 6:
                return cron_expression
            
            # Parse minute and hour fields
            minute_part = parts[0]
            hour_part = parts[1]
            
            # Convert Indian time to UTC by subtracting 5:30
            # For simplicity, we'll handle common cases
            
            # If it's a specific time (not wildcard)
            if minute_part != '*' and hour_part != '*':
                try:
                    minute = int(minute_part)
                    hour = int(hour_part)
                    
                    # Subtract 5 hours 30 minutes
                    total_minutes = hour * 60 + minute - 330  # 5*60 + 30 = 330
                    
                    if total_minutes < 0:
                        # Roll back to previous day
                        total_minutes += 24 * 60
                    
                    new_hour = total_minutes // 60
                    new_minute = total_minutes % 60
                    
                    # Update the cron expression
                    parts[0] = str(new_minute)
                    parts[1] = str(new_hour)
                    
                    return f"cron({' '.join(parts)})"
                except ValueError:
                    # If conversion fails, return original
                    return cron_expression
            
            # For wildcard cases, we can't easily convert, so return original
            # with a warning that user should specify exact times for Indian timezone
            logger.warning("Indian timezone offset applied to wildcard time. Consider specifying exact times for better accuracy.")
            return cron_expression
            
        except Exception as e:
            logger.warning(f"Failed to apply Indian timezone offset: {e}")
            return cron_expression 

    def _generate_cron_with_openai(self, text: str) -> str:
        """
        Use OpenAI to generate cron expression for complex natural language descriptions.
        
        Args:
            text: Natural language description of schedule
            
        Returns:
            Cron expression string
        """
        if not self.client:
            logger.warning("OpenAI client not available. Using default cron expression.")
            return "cron(0 0 * * ? *)"
        
        try:
            system_prompt = """You are an expert at converting natural language descriptions to AWS EventBridge cron expressions or rate expressions.

AWS EventBridge supports two formats:
1. Cron expressions: cron(Minutes Hours Day-of-month Month Day-of-week Year)
2. Rate expressions: rate(value unit)

Rules:
1. When specifying day-of-week, use ? for day-of-month
2. When specifying day-of-month, use ? for day-of-week
3. For Indian timezone (IST), subtract 5:30 hours to convert to UTC
4. Day-of-week: 0=Sunday, 1=Monday, ..., 6=Saturday
5. Year field can be * for any year, or specific year range like 2024-2025
6. For rate expressions: use singular unit for value=1, plural for values>1

Examples:
- "daily at 9am" → "cron(0 9 * * ? *)"
- "every friday at 9pm" → "cron(0 21 ? * 5 *)"
- "every friday at 9pm indian time" → "cron(30 15 ? * 5 *)" (9pm IST = 3:30pm UTC)
- "every 6 hours" → "rate(6 hours)"
- "every 2 minutes" → "rate(2 minutes)"
- "every day" → "rate(1 day)"
- "monthly on the 15th" → "cron(0 0 15 * ? *)"
- "weekdays at 9am" → "cron(0 9 ? * 1-5 *)"

Return ONLY the expression, nothing else."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.1,
                max_tokens=50
            )
            
            result = response.choices[0].message.content.strip()
            
            # Validate the result
            if result.startswith("cron(") and result.endswith(")"):
                return result
            else:
                logger.warning(f"OpenAI returned invalid cron format: {result}")
                return "cron(0 0 * * * *)"
                
        except Exception as e:
            logger.warning(f"Failed to generate cron with OpenAI: {e}")
            return "cron(0 0 * * * *)" 