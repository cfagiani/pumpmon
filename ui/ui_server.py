"""
__author__ = 'Christopher Fagiani'
"""
import json
import logging
import os
import threading

RESOURCE_DIR_PATH = os.path.join(os.path.dirname(__file__), 'resources')
CONFIG_SECTION = "ui"

try:
    from flask import Flask, request, send_from_directory
except ImportError:
    raise ImportError("flask is not installed. Please install (sudo apt-get install flask)")

logger = logging.getLogger(__name__)
app = Flask(__name__)
apiInstance = None


@app.route('/')
def root():
    return send_from_directory(RESOURCE_DIR_PATH, 'index.html')


@app.route('/js/<path:path>')
def js(path):
    return send_from_directory(RESOURCE_DIR_PATH + '/js', path)


@app.route('/css/<path:path>')
def css(path):
    return send_from_directory(RESOURCE_DIR_PATH + '/css', path)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(RESOURCE_DIR_PATH + '/img', "favicon.ico")


@app.route("/waterlevels", methods=["GET"])
def get_levels():
    """Returns current workout status
    """
    global apiInstance
    return apiInstance.get_by_date_range(request.args.get('from'), request.args.get('to'))


class PumpmonServer:


    def __init__(self, config, dao):
        """Sets up the Flask webserver to run on the port passed in
        """
        global apiInstance
        self.port = config.getint(CONFIG_SECTION, "port")
        self.dao = dao

        apiInstance = self

    def start(self):
        self.thread = threading.Thread(target=self.run_app)
        self.thread.daemon = False
        self.thread.start()

    def run_app(self):
        app.run(host="0.0.0.0", port=self.port)

    def get_by_date_range(self, from_date, to_date):
        return json.dumps(self.dao.get_by_date_range(from_date, to_date), default=lambda x: x.__dict__)
