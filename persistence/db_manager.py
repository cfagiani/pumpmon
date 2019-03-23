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
    """
    This class serves as a wrapper over a SQLite3 database. It provides convenience methods for executing DML statements
    within a transaction as well a mechanism to run DDL statements. This class also maintains a mapping of threads to
    connections so each thread only needs to incur the overhead of connecting to the database once.
    """

    def __init__(self, config):
        """Opens a connection to the database specified via the db_path config item."""
        self.db_file = config.get(CONFIG_SECTION, DB_CONFIG_ITEM)
        if self.db_file is None:
            raise ValueError(
                "Config must include {item} in the {sec} section".format(item=DB_CONFIG_ITEM, sec=CONFIG_SECTION))
        self.connection_map = {threading.currentThread().ident: sqlite3.connect(self.db_file)}

    def execute_ddl(self, ddl_strings):
        """
        Executes 1 or more DDL statements.
        :param ddl_strings: array of DDL statements
        """
        try:
            cursor = self.__get_connection().cursor()
            for sql_str in ddl_strings:
                cursor.execute(sql_str)
        finally:
            cursor.close()

    def execute_transaction(self, query_executor):
        """
        Opens a cursor on the database and passes it to the query_executor function. If that function returns without
        and error, this method will call commit on the cursor. If an exception is raised, it will call rollback.
        :param query_executor: function that takes a cursor as a parameter that it uses to run database statements.
        :return: results of the query_executor call
        """
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
        """
        Closes the connection for the id (thread id) passed in. If no id is specified, the ident of the current thread
        will be assumed.
        :param id: thread id or None
        """
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
        """
        Closes all connections to the database.
        """
        logger.debug("Closing all connections")
        # need copy of keys to avoid concurrent modification
        for key in [k for k, v in self.connection_map.items()]:
            self.close(key)

    def __get_connection(self):
        """
        Gets a connection to the database. If no connection exists for the thread of execution that is calling this
        method, a new connection will be opened.
        :return:
        """
        thread_id = threading.currentThread().ident
        conn = self.connection_map.get(thread_id, None)
        if conn is None:
            logger.debug("No connection for thread {id}. Creating one.".format(id=thread_id))
            conn = sqlite3.connect(self.db_file)
            self.connection_map[thread_id] = conn
        else:
            logger.debug("Connection already exists for thread {id}. Reusing.".format(id=thread_id))
        return conn
