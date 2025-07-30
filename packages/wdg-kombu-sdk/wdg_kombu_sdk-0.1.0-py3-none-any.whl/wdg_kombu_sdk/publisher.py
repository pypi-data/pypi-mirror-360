from kombu import Producer, Exchange, Queue
from .connection import BrokerConnection, get_broker_url
import uuid
import queue as py_queue
from kombu import Consumer

class EventPublisher:
    def __init__(self, broker_url=None, exchange_name="events", exchange_type="fanout", **conn_kwargs):
        if broker_url is None:
            broker_url = get_broker_url()
        self.connection = BrokerConnection(broker_url, **conn_kwargs)
        self.exchange = Exchange(exchange_name, type=exchange_type)

    def publish_event(self, event_type, payload, routing_key="", serializer="json", headers=None, **kwargs):
        conn = self.connection.get_connection()
        if headers is None:
            headers = {}
        headers["event_type"] = event_type
        with conn.channel() as channel:
            producer = Producer(channel)
            producer.publish(
                payload,
                exchange=self.exchange,
                routing_key=routing_key,
                serializer=serializer,
                headers=headers,
                retry=True,
                retry_policy={"interval_start": 0, "interval_step": 2, "interval_max": 30},
                **kwargs
            )

    def publish_delayed_event(self, event_type, payload, delay_seconds, routing_key="", serializer="json", headers=None, queue_name="delayed_events", **kwargs):
        """
        Publish a delayed message using message TTL and dead-letter exchange pattern.
        Requires broker support (e.g., RabbitMQ with delayed message plugin or TTL+DLX).
        """
        conn = self.connection.get_connection()
        if headers is None:
            headers = {}
        headers["event_type"] = event_type
        # Setup delayed queue with TTL and dead-lettering
        delayed_queue = Queue(
            name=queue_name,
            exchange=self.exchange,
            routing_key=routing_key,
            queue_arguments={
                'x-message-ttl': int(delay_seconds * 1000),  # milliseconds
                'x-dead-letter-exchange': self.exchange.name,
                'x-dead-letter-routing-key': routing_key,
            }
        )
        with conn.channel() as channel:
            delayed_queue.maybe_bind(conn)
            delayed_queue.declare()
            producer = Producer(channel)
            producer.publish(
                payload,
                exchange=self.exchange,
                routing_key=routing_key,
                serializer=serializer,
                headers=headers,
                retry=True,
                retry_policy={"interval_start": 0, "interval_step": 2, "interval_max": 30},
                declare=[delayed_queue],
                **kwargs
            )

class RpcPublisher(EventPublisher):
    def call(self, event_type, payload, reply_queue_name=None, timeout=10, routing_key="", serializer="json", headers=None, **kwargs):
        """
        Send an RPC request and wait for a reply.
        """
        conn = self.connection.get_connection()
        correlation_id = str(uuid.uuid4())
        if reply_queue_name is None:
            reply_queue_name = f"rpc.reply.{correlation_id}"
        reply_queue = Queue(name=reply_queue_name, exclusive=True, auto_delete=True)
        response_queue = py_queue.Queue()
        def on_response(body, message):
            if message.properties.get('correlation_id') == correlation_id:
                response_queue.put(body)
                message.ack()
        with conn.channel() as channel:
            consumer = Consumer(channel, queues=[reply_queue], callbacks=[on_response], accept=[serializer])
            consumer.consume()
            self.publish_event(
                event_type,
                payload,
                routing_key=routing_key,
                serializer=serializer,
                headers={**(headers or {}), 'correlation_id': correlation_id},
                reply_to=reply_queue_name,
                **kwargs
            )
            try:
                return response_queue.get(timeout=timeout)
            except py_queue.Empty:
                raise TimeoutError("RPC reply timed out")

class TopicPublisher(EventPublisher):
    def __init__(self, broker_url=None, exchange_name="topic_events", **conn_kwargs):
        super().__init__(broker_url=broker_url, exchange_name=exchange_name, exchange_type="topic", **conn_kwargs)

    def publish_topic_event(self, event_type, payload, routing_key, serializer="json", headers=None, **kwargs):
        self.publish_event(event_type, payload, routing_key=routing_key, serializer=serializer, headers=headers, **kwargs)

# Example usage:
# publisher = EventPublisher()  # Uses settings.BROKER_URL by default
# publisher.publish_event('user.created', {"id": 1, "name": "Alice"})
# publisher.publish_delayed_event('user.created', {"id": 1}, delay_seconds=10)
# rpc = RpcPublisher()
# result = rpc.call('rpc.request', {'action': 'get_user', 'user_id': 42})
# print(result)
# topic_publisher = TopicPublisher()
# topic_publisher.publish_topic_event('user.signup', {"id": 1}, routing_key='user.signup')
