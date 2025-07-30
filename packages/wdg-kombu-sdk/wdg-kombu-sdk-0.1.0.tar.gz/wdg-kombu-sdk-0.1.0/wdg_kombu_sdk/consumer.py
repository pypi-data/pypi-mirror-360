import logging
from kombu import Consumer, Exchange, Queue, Producer
from .connection import BrokerConnection, get_broker_url

logger = logging.getLogger(__name__)


class EventConsumer:
    def __init__(
        self,
        queue_name,
        broker_url=None,
        exchange_name="events",
        exchange_type="fanout",
        routing_key="",
        callback=None,
        **conn_kwargs,
    ):
        if broker_url is None:
            broker_url = get_broker_url()
        self.connection = BrokerConnection(broker_url, **conn_kwargs)
        self.exchange = Exchange(exchange_name, type=exchange_type)
        self.queue = Queue(
            name=queue_name, exchange=self.exchange, routing_key=routing_key
        )
        self.callback = callback or self.default_callback

    def default_callback(self, body, message):
        event_type = message.headers.get("event_type")
        logger.info(f"[EventConsumer] Received event: {event_type} | payload: {body}")
        message.ack()

    def start(self, accept=["json"], timeout=60, max_retries=5):
        conn = self.connection.get_connection()
        with conn.channel() as channel:
            consumer = Consumer(
                channel,
                queues=[self.queue],
                callbacks=[self.callback],
                accept=accept,
            )
            logger.info(
                f"[EventConsumer] Waiting for events on queue '{self.queue.name}'..."
            )
            while True:
                try:
                    conn.drain_events(timeout=timeout)
                except Exception as e:
                    logger.error(f"[EventConsumer] Error: {e}")
                    conn.ensure_connection(max_retries=max_retries)


class RpcConsumer(EventConsumer):
    def __init__(
        self,
        queue_name,
        broker_url=None,
        exchange_name="events",
        exchange_type="fanout",
        routing_key="",
        callback=None,
        **conn_kwargs,
    ):
        super().__init__(
            queue_name,
            broker_url,
            exchange_name,
            exchange_type,
            routing_key,
            callback,
            **conn_kwargs,
        )

    def start(self, accept=["json"], timeout=60, max_retries=5):
        conn = self.connection.get_connection()
        with conn.channel() as channel:
            consumer = Consumer(
                channel,
                queues=[self.queue],
                callbacks=[self._rpc_callback],
                accept=accept,
            )
            logger.info(
                f"[RpcConsumer] Waiting for RPC requests on queue '{self.queue.name}'..."
            )
            while True:
                try:
                    conn.drain_events(timeout=timeout)
                except Exception as e:
                    logger.error(f"[RpcConsumer] Error: {e}")
                    conn.ensure_connection(max_retries=max_retries)

    def _rpc_callback(self, body, message):
        if self.callback:
            response = self.callback(body, message)
            reply_to = message.properties.get("reply_to")
            correlation_id = message.properties.get("correlation_id")
            if reply_to:
                with self.connection.get_connection().channel() as channel:
                    producer = Producer(channel)
                    producer.publish(
                        response,
                        exchange="",
                        routing_key=reply_to,
                        serializer=message.content_type or "json",
                        headers={},
                        correlation_id=correlation_id,
                    )
        message.ack()


class TopicConsumer(EventConsumer):
    def __init__(
        self,
        queue_name,
        routing_key,
        broker_url=None,
        exchange_name="topic_events",
        callback=None,
        **conn_kwargs,
    ):
        super().__init__(
            queue_name=queue_name,
            broker_url=broker_url,
            exchange_name=exchange_name,
            exchange_type="topic",
            routing_key=routing_key,
            callback=callback,
            **conn_kwargs
        )

    def start(self, accept=["json"], timeout=60, max_retries=5):
        conn = self.connection.get_connection()
        with conn.channel() as channel:
            consumer = Consumer(
                channel,
                queues=[self.queue],
                callbacks=[self.callback],
                accept=accept,
            )
            logger.info(
                f"[TopicConsumer] Waiting for events on queue '{self.queue.name}' with routing key '{self.queue.routing_key}'..."
            )
            while True:
                try:
                    conn.drain_events(timeout=timeout)
                except Exception as e:
                    logger.error(f"[TopicConsumer] Error: {e}")
                    conn.ensure_connection(max_retries=max_retries)


# Example usage:
# def my_callback(body, message):
#     print(body)
#     message.ack()
# consumer = EventConsumer('order_saga_compensator', callback=my_callback)  # Uses settings.BROKER_URL by default
# consumer.start()

# def handle_rpc(body, message):
#     if body.get('action') == 'get_user':
#         return {"user_id": body['user_id'], "name": "Alice"}
# rpc_consumer = RpcConsumer('rpc_queue', callback=handle_rpc)
# rpc_consumer.start()

# consumer = TopicConsumer('user_events', routing_key='user.*', callback=my_callback)
# consumer.start()
