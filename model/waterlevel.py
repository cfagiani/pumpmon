"""
__author__ = 'Christopher Fagiani'
"""

class WaterLevel:
    """
    This class is a simple datastructure for holding water level readings at a specific time.
    """

    def __init__(self, timestamp, value):
        self.timestamp = timestamp
        self.value = value

    def validate(self):
        """
        Validates that this reading instance is valid by ensuring both the timestamp and value are populated and
        non-negative. If not vaild, this method will raise a ValueError.
        """
        errors = []
        if self.timestamp is None or self.timestamp < 0:
            errors.append("Timestamp must be greater than 0")
        if self.value is None or self.value < 0:
            errors.append("Value must be greater than 0")
        if len(errors) > 0:
            raise ValueError(", ".join(errors))
