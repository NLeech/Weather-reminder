class CoordinateConverter:
    """
    URL path converter for geographical coordinates (latitude, longitude).
    Coordinate like: -+ddd.dddd

    """
    regex = '[-+]?\d{1,3}(\.\d{0,4})?'

    def to_python(self, value):
        return float(value)

    def to_url(self, value):
        return str(value)
