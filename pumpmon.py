"""
__author__ = 'Christopher Fagiani'
"""
import ConfigParser
import argparse
import logging
import sys
import threading
import time

from monitor.pump import PumpMonitor
from persistence.db_manager import DatabaseManager
from persistence.water_level_dao import WaterLevelDao


def main(args):
    config = ConfigParser.RawConfigParser()
    config.read(args.config)
    monitor = None
    configure_logger(args.debug)
    try:
        db_mgr = DatabaseManager(config)
        dao = WaterLevelDao(db_mgr)
        monitor = PumpMonitor(config, dao)
        if not args.headless:
            from ui.ui_server import PumpmonServer
            server = PumpmonServer(config, dao)
            server.start()

        monitor_thread = threading.Thread(target=monitor.start)
        monitor_thread.start()
        while True:
            time.sleep(2)

    except KeyboardInterrupt as ki:
        print("shutting down")
    finally:
        if monitor is not None:
            monitor.stop()
        if db_mgr is not None:
            db_mgr.close_all()


def configure_logger(is_debug):
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
