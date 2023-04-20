import sqlite3
import boto3
from abc import ABC, abstractmethod
from .sql import Tweet, TweetDatabase


def create_storage(use_dynamodb=False, table_name=None, sqlite_db_path=None):
    if use_dynamodb:
        return DynamoDBStorage(table_name)
    else:
        return SQLiteStorage(sqlite_db_path)


class Storage(ABC):
    @abstractmethod
    def put(self, data):
        pass

    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def delete(self, key):
        pass

    @abstractmethod
    def get_100_most_recent(self):
        pass


class SQLiteStorage(Storage):
    def __init__(self, db_path):
        self.db_path = db_path
        self.db = TweetDatabase(self.db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def put(self, data):
        self.db.insert_tweet(data)

    # TODO use sqlalchemy for these
    def get(self, key):
        self.cursor.execute("SELECT * FROM your_table WHERE uuid=?", (key,))
        return self.cursor.fetchone()

    def delete(self, key):
        self.cursor.execute("DELETE FROM your_table WHERE uuid=?", (key,))
        self.conn.commit()

    def get_100_most_recent(self):
        return self.db.get_100_most_recent()


class DynamoDBStorage(Storage):
    def __init__(self, table_name):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)

    def put(self, data):
        self.table.put_item(Item=data)

    def get(self, key):
        response = self.table.get_item(Key={"tweet_id": key})
        return response.get("Item")

    def delete(self, key):
        self.table.delete_item(Key={"tweet_id": key})
