"""Smart gate db module
"""
import logging
import subprocess
import tzlocal
import psycopg2
from config import Config as config

root_logger = logging.getLogger("root")

class DB:
    """ DB class for managing the connections, tables, insertions
    """
    def __init__(self):
        try:
            self.connection = psycopg2.connect(
                database="smart-gate",
                host="localhost",
                user="smart-gate",
                password=str(config.DB_PASSWORD),
                )

            self.cursor = self.connection.cursor()
            self.create_entry_table()
            self.db_running = True
        except psycopg2.OperationalError as err:
            # Likely the db is not running, so continue without it.
            self.db_running = False
            root_logger.warning("DB did not connect, proceeding without db: %s", err)

    def create_entry_table(self):
        """ Creates entry table in the smart-gate db
        """
        self.cursor.execute("CREATE TABLE IF NOT EXISTS EntryTable( \
            entry_id SERIAL PRIMARY KEY, \
            datetime TIMESTAMP NOT NULL, \
            timezone VARCHAR(50) NOT NULL, \
            button VARCHAR(20), \
            media_filename TEXT UNIQUE);")
        self.connection.commit()

    def add_entry(self, button, entry_dt, media_filename=None):
        """Add an entry into the db
        """
        if self.db_running:
            sql = "INSERT INTO entrytable(button, datetime, timezone, media_filename) \
                    VALUES (%s, %s, %s, %s)"
            tzname = tzlocal.get_localzone().zone
            self.cursor.execute(sql, (button, entry_dt, tzname, media_filename))
            self.connection.commit()

    def cleanup(self):
        """ Cleanup db by closing connection
        """
        if self.db_running:
            self.connection.close()
