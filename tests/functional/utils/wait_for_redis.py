import time

from redis import Redis
from tests.functional.settings import session_settings

if __name__ == '__main__':
    redis_client = Redis(host=session_settings.redis_host, port=session_settings.redis_port)
    while True:
        if redis_client.ping():
            break
        time.sleep(1)
