from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from wdg_kombu_sdk.publisher import EventPublisher

# Example: Integrate with a Django model (replace 'YourModel' with your model)
# from your_app.models import YourModel

# @receiver(post_save, sender=YourModel)
# def publish_model_saved(sender, instance, created, **kwargs):
#     event_type = 'model.created' if created else 'model.updated'
#     payload = {'id': instance.id, 'data': str(instance)}
#     publisher = EventPublisher()
#     publisher.publish_event(event_type, payload)

# To use:
# 1. Uncomment and adjust the import for your model.
# 2. Uncomment the receiver and function, and adjust event_type/payload as needed.
# 3. Add 'wdg_kombu_sdk.signals' to your app's ready() or import it in your app config to activate.

def start_load_balanced_consumers(consumer_class, queue_name, callback, num_consumers=2, **kwargs):
    """
    Helper to start multiple consumer instances for load balancing.
    Usage:
        from wdg_kombu_sdk.consumer import EventConsumer
        start_load_balanced_consumers(EventConsumer, 'shared_queue', my_callback, num_consumers=3)
    """
    import threading
    def run_consumer():
        consumer = consumer_class(queue_name, callback=callback, **kwargs)
        consumer.start()
    threads = []
    for _ in range(num_consumers):
        t = threading.Thread(target=run_consumer)
        t.daemon = True
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

# Example usage:
# def my_callback(body, message):
#     print(body)
#     message.ack()
# start_load_balanced_consumers(EventConsumer, 'shared_queue', my_callback, num_consumers=3)

# Example: Using custom serializers (e.g., yaml, msgpack)
#
# On the publisher side:
# publisher.publish_event('user.created', {"id": 1}, serializer='yaml')
#
# On the consumer side:
# consumer = EventConsumer('queue', accept=['yaml'], callback=my_callback)
# consumer.start()
#
# To register a custom serializer globally:
# from kombu.serialization import register
# import yaml
#
# def yaml_dumps(obj):
#     return yaml.dump(obj).encode()
#
# def yaml_loads(s):
#     return yaml.safe_load(s.decode())
#
# register('yaml', yaml_dumps, yaml_loads, content_type='application/x-yaml', content_encoding='utf-8')
#
# Now you can use serializer='yaml' in publish_event and accept=['yaml'] in consumers.

def register_custom_serializer(name, dumps, loads, content_type, content_encoding='utf-8'):
    """
    Helper to register a custom serializer for Kombu.
    Example usage:
        import yaml
        def yaml_dumps(obj):
            return yaml.dump(obj).encode()
        def yaml_loads(s):
            return yaml.safe_load(s.decode())
        register_custom_serializer('yaml', yaml_dumps, yaml_loads, content_type='application/x-yaml')
    Then use serializer='yaml' in publisher and accept=['yaml'] in consumer.
    """
    from kombu.serialization import register
    register(name, dumps, loads, content_type=content_type, content_encoding=content_encoding)
