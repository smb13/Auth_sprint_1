import time

import psycopg
from tests.functional.settings import session_settings

if __name__ == '__main__':
    while True:
        if psycopg.connect(conninfo=session_settings.get_pg_dsn()):
            break
        time.sleep(1)
