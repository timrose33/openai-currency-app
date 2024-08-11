from datetime import date
from datetime import timedelta, datetime


class DateRange:
    def __init__(self, start_date=None, end_date=None):
       # If both dates are None, set the DateRange as empty
        if start_date is None and end_date is None:
            self.empty = True
            self.start_date = None
            self.end_date = None
        else:
            # Convert strings to date objects if necessary
            if isinstance(start_date, str):
                try:
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError("start_date must be in 'YYYY-MM-DD' format")
            if isinstance(end_date, str):
                try:
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError("end_date must be in 'YYYY-MM-DD' format")

            # Check if dates are instances of date and are valid
            if isinstance(start_date, date) and isinstance(end_date, date) and start_date <= end_date:
                self.start_date = start_date
                self.end_date = end_date
                self.empty = False
            else:
                raise ValueError("Invalid dates for DateRange")

    def contains(self, check_date):
        if not isinstance(check_date, date):
            raise TypeError("check_date must be a datetime.date instance")
        return not self.empty and self.start_date <= check_date <= self.end_date

    def __iter__(self):
        if self.empty:
            return iter([])
        current_date = self.start_date
        while current_date <= self.end_date:
            yield current_date
            current_date += timedelta(days=1)

    def __str__(self):
        if self.empty:
            return "DateRange(empty)"
        return f"DateRange({self.start_date}, {self.end_date})"
    
    def overlaps(self, other):
        if not isinstance(other, DateRange):
            raise TypeError("other must be a DateRange instance")
        if self.empty or other.empty:
            return False
        return self.start_date <= other.end_date and other.start_date <= self.end_date
    
    def is_empty(self):
        return self.empty

    def merge(self, other):
        if not isinstance(other, DateRange):
            raise TypeError("other must be a DateRange instance")
        if self.overlaps(other):
            new_start_date = min(self.start_date, other.start_date)
            new_end_date = max(self.end_date, other.end_date)
            return DateRange(new_start_date, new_end_date)
        else:
            return DateRange()
        
    def intersection(self, other):
        if not isinstance(other, DateRange):
            raise TypeError("other must be a DateRange instance")
        if self.overlaps(other):
            new_start_date = max(self.start_date, other.start_date)
            new_end_date = min(self.end_date, other.end_date)
            return DateRange(new_start_date, new_end_date)
        else:
            return DateRange()    
        
    def subtract(self, other):
        if not isinstance(other, DateRange):
            raise TypeError("other must be a DateRange instance")
        if self.empty or other.empty:
            return [self]
        
        result = []
        
        # Case 1: No overlap
        if other.end_date < self.start_date or other.start_date > self.end_date:
            return [self]
        
        # Case 2: Other fully overlaps this DateRange
        if other.start_date <= self.start_date and other.end_date >= self.end_date:
            return []
        
        # Case 3: Partial overlaps
        if other.start_date > self.start_date:
            result.append(DateRange(self.start_date, other.start_date - timedelta(days=1)))
        
        if other.end_date < self.end_date:
            result.append(DateRange(other.end_date + timedelta(days=1), self.end_date))
        
        return result
        
def create_date_range(date_dict):
    """
    Create a DateRange object from a dictionary with 'start_date' and 'end_date'.
    If the keys are not found, return an empty DateRange.

    :param date_dict: Dictionary with 'start_date' and 'end_date' keys.
    :return: DateRange object
    """
    try:
        start_date_str = date_dict['start_date']
        end_date_str = date_dict['end_date']
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        return DateRange(start_date, end_date)
    except KeyError:
        return DateRange()
    except ValueError:
        return DateRange()

