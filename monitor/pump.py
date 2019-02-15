import time

import RPi.GPIO as GPIO

from model.waterlevel import WaterLevel

CONFIG_SECTION = "monitor"

SPEED_OF_SOUND = 34300  # cm/sec


class PumpMonitor:

    def __init__(self, config, dao):
        self.__init_GPIO(config.getint(CONFIG_SECTION, "trigger_pin"), config.getint(CONFIG_SECTION, "echo_pin"))
        self.num_samples = config.getint(CONFIG_SECTION, "num_samples")
        self.drop_extremes = config.getboolean(CONFIG_SECTION, "drop_extremes")
        self.sample_delay = config.getfloat(CONFIG_SECTION, "sample_delay")
        self.measurement_frequency = config.getfloat(CONFIG_SECTION, "measurement_frequency")
        self.is_running = False
        self.dist_to_bottom = config.getfloat(CONFIG_SECTION, "distance_to_bottom")
        self.dao = dao

    def __init_GPIO(self, trigger_pin, echo_pin):
        GPIO.setmode(GPIO.BCM)
        # set GPIO Pins
        self.GPIO_TRIGGER = trigger_pin
        self.GPIO_ECHO = echo_pin

        # set GPIO direction (IN / OUT)
        GPIO.setup(self.GPIO_TRIGGER, GPIO.OUT)
        GPIO.setup(self.GPIO_ECHO, GPIO.IN)

    def measure_distance(self):
        # set Trigger to HIGH
        GPIO.output(self.GPIO_TRIGGER, True)

        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(self.GPIO_TRIGGER, False)

        start_time = time.time()
        stop_time = time.time()

        # save StartTime
        while GPIO.input(self.GPIO_ECHO) == 0:
            start_time = time.time()

        # save time of arrival
        while GPIO.input(self.GPIO_ECHO) == 1:
            stop_time = time.time()

        # time difference between start and arrival
        elapsed = stop_time - start_time
        # divide by 2 to get one-way time
        distance = (elapsed * SPEED_OF_SOUND) / 2

        return distance

    def avg_sample(self):
        samples = [0] * self.num_samples
        for i in range(self.num_samples):
            samples[i] = self.measure_distance()
            time.sleep(self.sample_delay)
        if self.drop_extremes:
            samples.sort()
            samples = samples[1:-1]
            return sum(samples) / len(samples)

    def convert_to_depth(self, dist):
        return self.dist_to_bottom - dist

    def start(self):
        self.is_running = True
        while self.is_running:
            depth = self.convert_to_depth(self.avg_sample())
            if depth >= 0:
                self.dao.save(WaterLevel(time.time() * 1000, depth))
            time.sleep(self.measurement_frequency)

    def stop(self):
        self.is_running = False
        GPIO.cleanup()
