
class InMemStorage:
    tweets = {}

    @classmethod
    def put(cls, data):
        cls.tweets[data['tweet_id']] = data
        return data['tweet_id']

    @classmethod
    def get(cls, key):
        if key in cls.tweets:
            return cls.tweets[key]
        return None

    @classmethod
    def delete(cls, key):
        del(cls.tweets[key])

    @classmethod
    def get_100_most_recent(cls):
        # insertion order is guaranteed in python3.7+
        return list(cls.tweets.values())[-100:]

