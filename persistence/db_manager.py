"""
__author__ = 'Christopher Fagiani'
"""

import logging
import sqlite3
import threading

logger = logging.getLogger(__name__)

CONFIG_SECTION = "database"
DB_CONFIG_ITEM = "db_path"


class DatabaseManager:

    def __init__(self, config):
        self.db_file = config.get(CONFIG_SECTION, DB_CONFIG_ITEM)
        if self.db_file is None:
            raise ValueError(
                "Config must include {item} in the {sec} section".format(item=DB_CONFIG_ITEM, sec=CONFIG_SECTION))
        self.connection_map = {threading.currentThread().ident: sqlite3.connect(self.db_file)}

    def execute_ddl(self, ddl_strings):
        try:
            cursor = self.__get_connection().cursor()
            for sql_str in ddl_strings:
                cursor.execute(sql_str)
        finally:
            cursor.close()

    def execute_transaction(self, query_executor):
        conn = self.__get_connection()
        cursor = None
        results = None
        try:
            cursor = conn.cursor()
            results = query_executor(cursor)
            conn.commit()
        except sqlite3.Error as e:
            logger.error("Could not run db transaction", e)
            conn.rollback()
        finally:
            if cursor is not None:
                cursor.close()
        return results

    def close(self, id=None):
        if id is None:
            thread_id = threading.currentThread().ident
        else:
            thread_id = id
        logger.debug("Closing database connection for {id}".format(id=thread_id))
        conn = self.connection_map.get(thread_id, None)
        if conn is not None:
            conn.close()
            self.connection_map.pop(thread_id)

    def close_all(self):
        logger.debug("Closing all connections")
        for key in self.connection_map.keys():
            self.close(key)

    def __get_connection(self):
        thread_id = threading.currentThread().ident
        conn = self.connection_map.get(thread_id, None)
        if conn is None:
            logger.debug("No connection for thread {id}. Creating one.".format(id=thread_id))
            conn = sqlite3.connect(self.db_file)
            self.connection_map[thread_id] = conn
        else:
            logger.debug("Connection already exists for thread {id}. Reusing.".format(id=thread_id))
        return conn
