# mlslib/date_utils.py

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

def generate_periodic_date_ranges(
    start_date_str: str,
    num_periods: int,
    period_days: int
) -> list[tuple[str, str]]:
    """
    Generates a list of date ranges based on a fixed number of days.

    Args:
        start_date_str (str): The starting date in "yyyy-mm-dd" format.
        num_periods (int): The number of periodic ranges to generate.
        period_days (int): The duration of each period in days (e.g., 7 for weekly).

    Returns:
        list[tuple[str, str]]: A list of (start_date_string, end_date_string) tuples.
    
    Example:
        # Generate 4 periods of 7 days each
        generate_periodic_date_ranges("2024-01-01", 4, 7)
        # Returns:
        # [('2024-01-01', '2024-01-07'),
        #  ('2024-01-08', '2024-01-14'),
        #  ('2024-01-15', '2024-01-21'),
        #  ('2024-01-22', '2024-01-28')]
    """
    date_ranges = []
    current_start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()

    for _ in range(num_periods):
        current_end_date = current_start_date + timedelta(days=period_days - 1)
        
        date_ranges.append(
            (current_start_date.strftime("%Y-%m-%d"), current_end_date.strftime("%Y-%m-%d"))
        )
        
        # The next period starts the day after the current one ends
        current_start_date = current_end_date + timedelta(days=1)
        
    return date_ranges

def get_relative_day_range(days: int, offset_days: int, base_date_str: str = 'today') -> tuple[str, str]:
    """
    Gets a date range for a specific number of days relative to a base date.

    Args:
        days (int): The duration of the date range (e.g., 7 for a 7-day period).
        offset_days (int): The number of days to shift the *end* of the range from the
                         base date. 0 means the range ends *on* the base_date.
                         -1 means the range ends the day *before* the base_date.
        base_date_str (str): The base date for the calculation ("yyyy-mm-dd" or "today").

    Returns:
        tuple[str, str]: A (start_date_string, end_date_string) tuple.

    Example - Get the last 30 days of data, ending yesterday:
        # Assuming today is 2025-06-29
        get_relative_day_range(days=30, offset_days=-1)
        # Returns: ('2025-05-30', '2025-06-28')

    Example - Get a 7-day period ending today:
        # Assuming today is 2025-06-29
        get_relative_day_range(days=7, offset_days=0)
        # Returns: ('2025-06-23', '2025-06-29')
    """
    if base_date_str.lower() == 'today':
        base_date = date.today()
    else:
        base_date = datetime.strptime(base_date_str, "%Y-%m-%d").date()

    # Calculate the end date of the range
    end_date = base_date + timedelta(days=offset_days)
    
    # Calculate the start date of the range
    # We subtract 'days - 1' because the range includes the end date itself
    start_date = end_date - timedelta(days=days - 1)
    
    return (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))