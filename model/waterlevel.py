class WaterLevel:

    def __init__(self, timestamp, value):
        self.timestamp = timestamp
        self.value = value

    def validate(self):
        errors = []
        if self.timestamp is None or self.timestamp < 0:
            errors.append("Timestamp must be greater than 0")
        if self.value is None or self.value < 0:
            errors.append("Value must be greater than 0")
        if len(errors) > 0:
            raise ValueError(", ".join(errors))
