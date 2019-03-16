"""
__author__ = 'Christopher Fagiani'
"""
import time

import RPi.GPIO as GPIO

SPEED_OF_SOUND = 34300  # cm/sec


class SensorDriver:
    """
    This class encapsulates the logic needed to measure distance (in centimeters) with an Ultrasonic Range Finder
    sensor (HR-SR04) module. It takes the pin numbers (using BCM numbering) of the trigger and echo pins as arguments to
    the constructor and will use that to initialize the GPIO subsystem. When you are done using this class, you should
    call cleanup to release GPIO resources.
    """

    def __init__(self, trigger_pin, echo_pin):
        """
        Initializes GPIO.
        :param trigger_pin:
        :param echo_pin:
        """
        GPIO.setmode(GPIO.BCM)
        # set GPIO Pins
        self.GPIO_TRIGGER = trigger_pin
        self.GPIO_ECHO = echo_pin

        # set GPIO direction (IN / OUT)
        GPIO.setup(self.GPIO_TRIGGER, GPIO.OUT)
        GPIO.setup(self.GPIO_ECHO, GPIO.IN)

    def measure_distance(self):
        """
        Returns the distance between the sensor and an object in centimeters. This represents a single sample and thus
        can occasionally be noisy (or even negative). Calling classes should check for validity before using the value.
        :return: distance in cm
        """
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

    def cleanup(self):
        """
        Calls cleanup on the GPIO module.
        """
        GPIO.cleanup()
