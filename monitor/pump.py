"""
__author__ = 'Christopher Fagiani'
"""
import time

CONFIG_SECTION = "monitor"


class PumpMonitor:
    """
    This class is used in conjunction with a Sensor to measure the water level in a sump pump pit. Since the raw
    sensor values can be noisy, this class will use a multiple measurement samples and return the average
    value of all the measurements each time the get_measurement method is called. The value returned by the
    get_measurement method is the depth of the water in centimeters.

    The number of samples, as well as the delay between readings can be configured via num_samples and sample_delay
    configuration parameters (in the 'monitor' section of a config object). Additionally, the drop_extremes flag can be
    passed in the config to instruct this class to drop the min and max measurements when calculating the average (this
    is helpful if to negate the impact of an aberrant reading skewing the average). The distance_to_bottom configuration
    parameter is the distance from the sensor to the bottom of the pump pit in centimeters.
    """

    def __init__(self, config, sensor=None):
        """
        Initializes the class by reading the config values and constructing a sensor (if not passed in). In the normal
        case, the sensor value should be None, thus allowing this class to use the trigger_pin and echo_pin config
        values to initialize its own Sensor instance. The only time one should need to pass in a Sensor instance is for
        testing with a mocked sensor object.
        :param config:
        :param sensor:
        """
        if sensor is None:
            from monitor.sensor import SensorDriver
            self.sensor = SensorDriver(config.getint(CONFIG_SECTION, "trigger_pin"),
                                       config.getint(CONFIG_SECTION, "echo_pin"))
        else:
            self.sensor = sensor
        self.num_samples = config.getint(CONFIG_SECTION, "num_samples")
        self.drop_extremes = config.getboolean(CONFIG_SECTION, "drop_extremes")
        self.sample_delay = config.getfloat(CONFIG_SECTION, "sample_delay")
        self.is_running = False
        self.dist_to_bottom = config.getfloat(CONFIG_SECTION, "distance_to_bottom")

    def _avg_sample(self):
        """
        Takes num_samples measurements from the sensor and returns the average. If drop_extremes is true, the min and
        max values will be omitted before calculating the average.

        Since this method takes num_samples with a delay of sample_delay seconds between samples, it could take a non-
        trivial amount of time to return if either of those values are high.
        :return: average distance from sensor to top of water in centimeters
        """
        samples = [0] * self.num_samples
        for i in range(self.num_samples):
            samples[i] = self.sensor.measure_distance()
            time.sleep(self.sample_delay)
        if self.drop_extremes:
            samples.sort()
            samples = samples[1:-1]
            return sum(samples) / len(samples)

    def _convert_to_depth(self, dist):
        """
        Converts a distance measure to water depth.
        :param dist: distance from sensor to top of water in centimeters
        :return: depth in centimeters
        """
        return self.dist_to_bottom - dist

    def get_measurement(self):
        """
        Returns the depth of the water in the pump.
        :return: depth in centimeters
        """
        return self._convert_to_depth(self._avg_sample())

    def cleanup(self):
        """
        Calls cleanup on sensor.
        """
        self.sensor.cleanup()
