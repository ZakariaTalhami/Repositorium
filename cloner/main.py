import os
from logging import Logger
import json
from git import Repo
from git.exc import GitCommandError
from communication.rabbitmq import MessageQueue

# construct logger
import logging
import logging.config
import yaml

with open('logConfig.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


REPO_BASE_LOCATION = os.getenv("REPO_BASE_LOCATION", './')
QUEUE_NAME = os.getenv("QUEUE_NAME")
MESSAGE_BROKER_HOST = os.getenv("MESSAGE_BROKER_HOST")
MESSAGE_BROKER_USER = os.getenv("MESSAGE_BROKER_USER")
MESSAGE_BROKER_PASS = os.getenv("MESSAGE_BROKER_PASS")


class RepoCloner:

    def __init__(self, queue_host, queue_username, queue_password, repo_base_location):
        """
        Parameters
        ----------
        queue_host : str
            The message queue host
        queue_username : str
            The message queue admin username
        queue_password : str
            The message queue admin password
        repo_base_location : str
            The base location for cloning Repositories
        """
        self.__queue_host = queue_host
        self.__queue_username = queue_username
        self.__queue_password = queue_password
        self.__repo_base_location = repo_base_location
        self.__message_broker = MessageQueue(
            host=self.__queue_host,
            username=self.__queue_username,
            password=self.__queue_password
        )

    def clone(self, remote_url, path):
        """
        Parameters
        ----------
        remote_url : str
            The Remote repository URL to be cloned
        path : str
            The directory path to clone the repository
        Returns
        -------
        git.Repo
            Cloned repository instance
        """
        location = os.path.join(self.__repo_base_location, path)
        logger.info("Cloning...")
        try:
            repo = Repo.clone_from(remote_url, location)
        except GitCommandError as e:
            logger.error(f"Failed to clone {remote_url}")
            logger.error(e)
            return None
        logger.info("Clone Complete")
        return repo

    def process_message(self, channel, method, properties, body):
        """
        Process the message from the queue, extract the Repository information and clone

        Parameters
        ----------
        channel
        method
        properties
        body
        """
        try:
            message = json.loads(body)
            logger.info(message)
            try:
                url = message['url']
                name = message['name']
                self.clone(url, name)
            except KeyError as e:
                logger.error("Message must specify {}".format(e))
        except json.JSONDecodeError:
            logger.error("Unable to decode message")
            logger.error(body)

    def consume_messages(self, queue_name):
        """
        Start consuming messages from the message queue for cloning

        Message Body Example:
        body = {
            "url": "https://github.com/<username>/<repository-name>.git",
            "name": "<repository-path>"
        }

        Parameters
        ----------
        queue_name : str
            The name of the queue to receive messages from
        """
        self.__message_broker.consume_queue(
            queue=queue_name,
            callback=self.process_message
        )


logger.info("Bringing cloner up...")

# Initiate RepoCloner
cloner = RepoCloner(
    queue_host=MESSAGE_BROKER_HOST,
    queue_username=MESSAGE_BROKER_USER,
    queue_password=MESSAGE_BROKER_PASS,
    repo_base_location=REPO_BASE_LOCATION
)

# Start consuming message queue
cloner.consume_messages(QUEUE_NAME)

logger.info("Cloner going down!")
