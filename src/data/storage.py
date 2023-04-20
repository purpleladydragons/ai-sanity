import sqlite3
import boto3
from abc import ABC, abstractmethod
from .sql import Tweet, TweetDatabase


def create_storage(mode='inmem', table_name=None, sqlite_db_path=None):
    if mode == 'inmem':
        return InMemStorage()
    elif mode == 'dynamo':
        return DynamoDBStorage(table_name)
    elif mode == 'sql':
        return SQLiteStorage(sqlite_db_path)
    else:
        raise Exception(f'Invalid storage mode {mode}')


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


# persist the storage outside of instance to avoid needing to DI the same instance everywhere
tweets = {}
class InMemStorage(Storage):
    def __init__(self):
        self.tweets = tweets

    def put(self, data):
        self.tweets[data['tweet_id']] = data
        return data['tweet_id']

    def get(self, key):
        if key in self.tweets:
            return self.tweets[key]
        return None

    def delete(self, key):
        del(self.tweets[key])

    def get_100_most_recent(self):
        return list(self.tweets.values())[-100:]


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
