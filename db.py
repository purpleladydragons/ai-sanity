from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, exists
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

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
    created_at = Column(TIMESTAMP, nullable=False, server_default='CURRENT_TIMESTAMP')


class TweetDatabase:
    def __init__(self, db_url):
        # Create an SQLite database engine
        self.engine = create_engine(db_url)
        # Create the "tweets" table in the database (if it doesn't exist)
        Base.metadata.create_all(self.engine)
        # Create a session to interact with the database
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
        )
        # Add the new tweet to the session
        session.add(new_tweet)
        # Commit the transaction to insert the record into the database
        session.commit()

        id = new_tweet.id

        # Close the session
        session.close()
        return id
