import pika

class MessageQueue:
    """
    RabbitMQ adapter
    """

    def __init__(self, host, username, password):
        """

        Parameters
        ----------
        host : str
            The location of the RabbitMQ host
        username : str
            Admin username for the host
        password : str
            Admin password for the host
        """
        self.credentials = pika.PlainCredentials(username, password)
        self.connection_params = pika.ConnectionParameters(host, credentials=self.credentials)
        self.connection, self.channel = self.make_connection()

    def make_connection(self):
        """
        Make a connection and channel to RabbitMQ using pika

        Returns
        -------
        pika.BasicConnection
            A Connection to RabbitMQ using pika
        pika.Channel
            A Channel for pika
        """
        connection = None
        channel = None
        try:
            connection = pika.BlockingConnection(self.connection_params)
            channel = connection.channel()
        except:
            print("Failed to make connection")
        return connection, channel

    def reconnect(self):
        """
        Reestablish connection to RabbitMQ if closed or lost
        """
        if not self.connection or self.connection.is_closed:
            self.connection, self.channel = self.make_connection()

    def make_queue(self, name):
        """
        Declare a Queue in RabbitMQ

        Parameters
        ----------
        name : str
            The name of the queue to be declared
        """
        # can be done as a wrapper
        if self.connection.is_closed:
            self.reconnect()
        self.channel.queue_declare(queue=name)

    def consume_queue(self, queue, callback):
        """
        Consume Message from a queue in RabbitMQ

        Parameters
        ----------
        queue : str
            The queue name to be consumed
        callback : function
            The function to execute when receiving a message
        """
        if self.connection.is_closed:
            self.reconnect()
        self.make_queue(queue)
        self.channel.basic_consume(queue, callback)
        self.channel.start_consuming()
