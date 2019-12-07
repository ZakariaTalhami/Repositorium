import time
import os
import pika
import json
from git import Repo


REPO_BASE_LOCATION = os.getenv("REPO_BASE_LOCATION", './')
QUEUE_NAME = "cloner_belt"
MESSAGE_BROKER_HOST = "rabbitmq"
MESSAGE_BROKER_USER = "user"
MESSAGE_BROKER_PASS = "password"


class MessageQueue:
    def __init__(self, host, username, password):
        self.credentials = pika.PlainCredentials(username, password)
        self.connection_params = pika.ConnectionParameters(host, credentials=self.credentials)
        self.connection, self.channel = self.make_connection()

    def make_connection(self):
        connection = None
        channel = None
        try:
            connection = pika.BlockingConnection(self.connection_params)
            channel = connection.channel()
        except:
            print("Failed to make connection")
        return connection, channel

    def reconnect(self):
        if not self.connection or self.connection.is_closed:
            self.connection, self.channel = self.make_connection()

    def make_queue(self, name):
        # can be done as a wrapper
        if self.connection.is_closed:
            self.reconnect()
        self.channel.queue_declare(queue=name)

    def consume_queue(self, queue, callback):
        if self.connection.is_closed:
            self.reconnect()
        self.make_queue(queue)
        self.channel.basic_consume(queue, callback)
        self.channel.start_consuming()
# start_consuming


def clone(url, path):
    """
    :param url: The url of the remote repo
    :param path: The file path to clone into
    :return:
        Repo Object
    """
    location = os.path.join(REPO_BASE_LOCATION, path)
    print("Cloning...")
    repo = Repo.clone_from(url, location)
    print("Clone Complete")
    return repo


print("Bringing cloner up...")

message_broker = MessageQueue(
    host=MESSAGE_BROKER_HOST,
    username=MESSAGE_BROKER_USER,
    password=MESSAGE_BROKER_PASS
)

# Turn this into a class
def cloner(channel, method, properties, body):
    try:
        message = json.loads(body)
        print(message)
        try:
            url = message['url']
            name = message['name']
            print(url)
            print(name)
            clone(url, name)
        except KeyError as e:
            print("Message must specify {}".format(e))
    except json.JSONDecodeError:
        print(body)
        print("Unable to decode message")


message_broker.consume_queue(
    queue=QUEUE_NAME,
    callback=cloner
)


# clone("https://github.com/ZakariaTalhami/PCBuild-django.git", "PCBuild-django")
x = {
"url": "https://github.com/ZakariaTalhami/PCBuild-django.git",
"name": "PCBuild-django"
}
print("Cloner going down!")
# while True:
#     time.sleep(10)

