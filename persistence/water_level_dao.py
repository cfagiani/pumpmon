"""
__author__ = 'Christopher Fagiani'
"""
import time

from model.waterlevel import WaterLevel

table_name = "WATER_LEVELS"
ddl_strings = [
    "CREATE TABLE IF NOT EXISTS {table} ( ID INTEGER PRIMARY KEY, TIMESTAMP INTEGER, VALUE REAL);".format(
        table=table_name)
]


class WaterLevelDao:
    """
    Data access object for persisting/retrieving WaterLevel instances from the database.
    """

    def __init__(self, db_manager):
        """
        Initializes the dao and creates the Water_Levels table if it doesn't already exist.
        :param db_manager:
        """
        self.db_mgr = db_manager
        db_manager.execute_ddl(ddl_strings)

    def save(self, level):
        """
        Inserts a WaterLevel entry into the database if it is valid.
        :param level: WaterLevel instance
        """

        def insert(cur):
            cur.execute(
                "INSERT into {table} (timestamp, value) VALUES (?,?)".format(table=table_name),
                (level.timestamp, level.value))
            return None

        level.validate()
        self.db_mgr.execute_transaction(insert)

    def get_by_date_range(self, start=0, end=time.time() * 1000):
        """
        Returns a list of WaterLevel instances that have a timestamp between the time range passed in.
        :param start: Start timestamp
        :param end: End Timestamp
        :return: list of WaterLevel objects
        """

        def run_query(cur):
            results = []
            for row in cur.execute(
                    "SELECT TIMESTAMP, VALUE from {table} WHERE timestamp BETWEEN ? AND ? ".format(table=table_name),
                    (start, end)):
                results.append(WaterLevel(row[0], row[1]))
            return results

        return self.db_mgr.execute_transaction(run_query)
