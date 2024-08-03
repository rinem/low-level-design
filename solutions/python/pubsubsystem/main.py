# concrete_subscriber.py
class ConcreteSubscriber:
    def __init__(self, name):
        self.name = name

    def on_message(self, message):
        print(f"Subscriber {self.name} received message: {message.get_content()}")

# message.py
class Message:
    def __init__(self, content):
        self.content = content

    def get_content(self):
        return self.content

# pub_sub_system.py
from concurrent.futures import ThreadPoolExecutor
from topic import Topic

class PubSubSystem:
    def __init__(self):
        self.topics = {}
        self.executor_service = ThreadPoolExecutor(max_workers=10)

    def create_topic(self, topic_name):
        self.topics.setdefault(topic_name, Topic(topic_name))

    def subscribe(self, topic_name, subscriber):
        topic = self.topics.get(topic_name)
        if topic:
            topic.add_subscriber(subscriber)

    def unsubscribe(self, topic_name, subscriber):
        topic = self.topics.get(topic_name)
        if topic:
            topic.remove_subscriber(subscriber)

    def publish(self, topic_name, message):
        topic = self.topics.get(topic_name)
        if topic:
            self.executor_service.submit(topic.publish, message)

    def shutdown(self):
        self.executor_service.shutdown()

    def get_topics(self):
        return self.topics

# pub_sub_system_demo.py
from concrete_subscriber import ConcreteSubscriber
from message import Message
from publisher import Publisher
from pub_sub_system import PubSubSystem

class PubSubSystemDemo:
    @staticmethod
    def run():
        pub_sub_system = PubSubSystem()

        # Create topics
        pub_sub_system.create_topic("Topic1")
        pub_sub_system.create_topic("Topic2")

        # Create subscribers
        subscriber1 = ConcreteSubscriber("Subscriber1")
        subscriber2 = ConcreteSubscriber("Subscriber2")
        subscriber3 = ConcreteSubscriber("Subscriber3")

        # Subscribe to topics
        pub_sub_system.subscribe("Topic1", subscriber1)
        pub_sub_system.subscribe("Topic1", subscriber2)
        pub_sub_system.subscribe("Topic2", subscriber2)
        pub_sub_system.subscribe("Topic2", subscriber3)

        # Create publishers
        publisher1 = Publisher(pub_sub_system.get_topics().get("Topic1"))
        publisher2 = Publisher(pub_sub_system.get_topics().get("Topic2"))

        # Publish messages
        publisher1.publish(Message("Message1 for Topic1"))
        publisher1.publish(Message("Message2 for Topic1"))
        publisher2.publish(Message("Message1 for Topic2"))

        # Unsubscribe from a topic
        pub_sub_system.unsubscribe("Topic1", subscriber2)

        # Publish more messages
        publisher1.publish(Message("Message3 for Topic1"))
        publisher2.publish(Message("Message2 for Topic2"))

        # Shutdown the system
        pub_sub_system.shutdown()

if __name__ == "__main__":
    PubSubSystemDemo.run()

# publisher.py
class Publisher:
    def __init__(self, topic):
        self.topic = topic

    def publish(self, message):
        self.topic.publish(message)

# subscriber.py
class Subscriber:
    def on_message(self, message):
        pass

# topic.py
class Topic:
    def __init__(self, name):
        self.name = name
        self.subscribers = set()

    def get_name(self):
        return self.name

    def add_subscriber(self, subscriber):
        self.subscribers.add(subscriber)

    def remove_subscriber(self, subscriber):
        self.subscribers.discard(subscriber)

    def publish(self, message):
        for subscriber in self.subscribers:
            subscriber.on_message(message)

