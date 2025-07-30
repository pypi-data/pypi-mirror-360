# messaging/connection.py
from kombu import Connection
import threading
from django.conf import settings


class BrokerConnection:
    _instances = {}
    _lock = threading.Lock()

    def __new__(cls, broker_url, **kwargs):
        key = (broker_url, tuple(sorted(kwargs.items())))
        if key not in cls._instances:
            with cls._lock:
                if key not in cls._instances:
                    instance = super().__new__(cls)
                    # Initialize instance attributes
                    instance.__dict__['conn'] = Connection(broker_url, **kwargs)
                    instance.__dict__['broker_url'] = broker_url
                    instance.__dict__['kwargs'] = kwargs
                    cls._instances[key] = instance
        return cls._instances[key]

    def get_connection(self):
        return self.__dict__['conn']

    def ensure_connection(self, max_retries=3):
        self.__dict__['conn'].ensure_connection(max_retries=max_retries)
        return self.__dict__['conn'].connected

    def is_connected(self):
        return self.__dict__['conn'].connected

# Helper to get broker url from settings
def get_broker_url():
    return getattr(settings, 'BROKER_URL', 'amqp://guest:guest@localhost:5672//')

# Example usage:
# broker_conn = BrokerConnection('amqp://guest:guest@localhost:5672//')
# broker_conn.ensure_connection()
# conn = broker_conn.get_connection()
