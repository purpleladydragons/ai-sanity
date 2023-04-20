import datetime

import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, exists, desc, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


# Define the SQLAlchemy model for the "tweets" table
class Tweet(Base):
    __tablename__ = 'tweets'
    id = Column(Integer, primary_key=True)
    tweet_id = Column(String, nullable=False)
    username = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    content = Column(String, nullable=False)
    num_likes = Column(Integer, nullable=False)
    tweet_time = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=sa.text('now'))


class TweetDatabase:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def insert_tweet(self, tweet_dict):
        session = self.Session()

        if session.query(exists().where(Tweet.tweet_id == tweet_dict['tweet_id'])).scalar():
            print('dupe')
            return None

        # TODO if we update the dict keys to be same, can we use **tweet_dict?
        # Create a new tweet record from the dictionary
        new_tweet = Tweet(
            tweet_id=tweet_dict['tweet_id'],
            username=tweet_dict['username'],
            display_name=tweet_dict['display_name'],
            content=tweet_dict['tweet_text'],
            num_likes=tweet_dict['num_likes'],
            tweet_time=tweet_dict['time_tweeted'],
            # TODO i know this is very bad, but for whatever godforsaken reason, CURRENT_TIMESTAMP is not working on the sqlite side
            created_at=datetime.datetime.now()
        )
        # Add the new tweet to the session
        session.add(new_tweet)
        # Commit the transaction to insert the record into the database
        session.commit()

        id = new_tweet.id

        # Close the session
        session.close()
        return id

    def get_100_most_recent(self):
        session = self.Session()
        recent_tweets = (
            session.query(Tweet.username, Tweet.content, Tweet.tweet_id)
                .order_by(desc(Tweet.created_at))
                .limit(100)
                .all()
        )
        session.close()
        return recent_tweets
