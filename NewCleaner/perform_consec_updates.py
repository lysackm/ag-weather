import MySQLdb
from config import database_host, database_port, database_user, database_pass, database_name
import log

def run(list_of_updates):
    log.main("perform consec updates")

    conn = MySQLdb.Connection(
        host=database_host,
        port=database_port,
        user=database_user,
        passwd=database_pass,
        db=database_name
    )

    curs = conn.cursor()

    def execute(sql):
        log.query(sql)
        curs.execute(sql)
        curs.nextset()

    for update in list_of_updates:
        execute(update)
        # commit the changes to the DB after each update
        conn.commit()

    # close the cursor
    curs.close()

    # close the connection to the database
    conn.close()
