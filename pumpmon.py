"""
__author__ = 'Christopher Fagiani'
"""
import argparse
import configparser
import logging
import sys
import threading
import time

from prometheus_client import start_http_server, Gauge

from model.waterlevel import WaterLevel
from monitor.pump import PumpMonitor
from persistence.db_manager import DatabaseManager
from persistence.water_level_dao import WaterLevelDao


class MonitorDriver:
    """
    Driver class that will initialize the PumpMonitor and call it repeatedly in a loop until it is told to stop. After
    each measurement is recorded, it will be peristed in the database using the dao instance passed in.
    """

    def __init__(self, config, dao):
        self.meas_freq = self.measurement_frequency = config.getfloat("monitor", "measurement_frequency")
        self.persist = config.getboolean("monitor", "persist_readings")
        self.dao = dao
        self.monitor = PumpMonitor(config)
        self.keep_running = True
        self.level_gauge = Gauge('water_depth', 'Depth of water in cm')
        # start prometheus
        start_http_server(config.getint("prometheus", "prometheus_port"))

    def run(self):
        """
        This method will repeatedly take a distance measurement using the PumpMonitor and store it in the database
        using the WaterLevelDao. It will then sleep for measurement_frequency seconds.
        This method should be invoked in its own thread. It will run until another thread calls the stop method.
        :return:
        """

        while self.keep_running:
            val = self.monitor.get_measurement()
            if val >= 0:
                self.level_gauge.set(val)
                if self.persist:
                    self.dao.save(WaterLevel(time.time() * 1000, val))
            time.sleep(self.measurement_frequency)
        self.monitor.cleanup()

    def stop(self):
        """
        Sets the keep_running flag to false so the run loop will exit.
        :return:
        """
        self.keep_running = False


def main(args):
    config = configparser.RawConfigParser()
    config.read(args.config)
    monitor = None
    configure_logger(args.debug)
    try:
        db_mgr = DatabaseManager(config)
        dao = WaterLevelDao(db_mgr)
        monitor = MonitorDriver(config, dao)
        if not args.headless:
            from ui.ui_server import PumpmonServer
            server = PumpmonServer(config, dao)
            server.start()

        monitor_thread = threading.Thread(target=monitor.run)
        monitor_thread.start()
        while True:
            time.sleep(2)

    except KeyboardInterrupt as ki:
        print("shutting down")
    finally:
        if monitor is not None:
            monitor.cleanup()
        if db_mgr is not None:
            db_mgr.close_all()


def configure_logger(is_debug):
    """
    Configures the logger to use either INFO (default) or DEBUG (if the debug flag is set) log levels.
    :param is_debug:
    :return:
    """
    root = logging.getLogger()
    if is_debug:
        root.setLevel(logging.DEBUG)
    else:
        root.setLevel(logging.INFO)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description="""
        Uses an ultrasonic range finder to compute water level in a sump pump and exposes the data via a web interface
        """)
    argparser.add_argument("-c", "--config", metavar='config', default="pumpmon.ini", help='Configuration file to use',
                           dest='config')
    argparser.add_argument("-d", "--debug", action="store_true", default=False)
    argparser.add_argument("-hl", "--headless", default=False, action="store_true",
                           help="If true, no ui server will be started")
    main(argparser.parse_args())
