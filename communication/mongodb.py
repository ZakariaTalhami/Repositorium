import mongoengine as db


class MongoDBHandler:

    def __init__(self, db_name, username, password, host="localhost", port=27017):
        """
        Parameters
        ----------
        db_name : str
            The name of the database to be used
        username : str
            The username for given database
        password : str
            The password for the given database
        host : str, optional
            The host location of the database (The default is localhost)
        port : str, optional
            The port number of the database (The defalt is 27017)
        """
        self.__db = db_name
        self.__username = username
        self.__password = password
        self.__host = host
        self.__port = port
        self.__connection = None
        
    def connect(self):
        """
        Connect to the database

        Returns
        -------
            The Connection object to the database
        """
        self.__connection = db.connect(
            db=self.__db,
            username=self.__username,
            password=self.__password,
            host=self.__host,
            port=self.__port
        )
        return self.__connection
