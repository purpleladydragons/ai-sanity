from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from db import Tweet
import os
import openai
from dotenv import load_dotenv

def chatWithGPT(prompt, model='gpt-3.5-turbo'):
    completion = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')


def filter_tweets():
    engine = create_engine("sqlite:///tweets.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Query the 100 most recent records from the 'tweets' table
    recent_tweets = (
        session.query(Tweet.username, Tweet.content, Tweet.tweet_id)
            .order_by(desc(Tweet.created_at))
            .limit(100)
            .all()
    )

    # TODO modify this so... that we make intermdediate calls to gpt with query of ~20 tweets, and then flush and do again
    i = 0
    prepend_query = 'Please filter out any tweets that are not about AI.\n'
    query = ''
    query_size = 0
    MAX_QUERY_SIZE = 2000  # slightly less than gpt3.5 limit as dumb way of avoiding overflow
    resps = []
    while i < len(recent_tweets):
        tweet = recent_tweets[i]
        username, content, tweet_id = tweet
        tweet_tokens = content.split()
        if query_size + len(tweet_tokens) < MAX_QUERY_SIZE:
            query += f'Tweet {i} (@{username}/{tweet_id}): ' + ' '.join(tweet_tokens) + '\n'
            query_size += len(tweet_tokens)
        else:
            resp = chatWithGPT(prepend_query + query)
            resps.append(resp)
            query = ''
            query_size = 0
        i += 1

    if len(query) > 0:
        resp = chatWithGPT(prepend_query + query)
        resps.append(resp)

    # Close the session
    session.close()

    return '\n'.join(resps)

def summarize_tweets(tweets):
    prompt = "Please summarize the following list of AI tweets. " \
             "Please try to achieve a perfect blend of depth and breadth. " \
             "Please highlight any specific technologies or techniques that are mentioned. " \
             "For example, a good summary of a specific topic within AI might look like: " \
             "Users X and Y are talking about BabyAGI, which is an agentic version of GPT." \
             "Do it step by step. First, identify the major talking points. " \
             "Then, associate appropriate tweets with each talking point. " \
             "For each summary, make sure to include the username and tweet id for the relevant tweets."
    print('tokens', len((prompt + ' ' + tweets).split()))
    resp = chatWithGPT(prompt + '\n' + tweets, model='gpt-4')
    print(resp)

tweets = filter_tweets()
print(len(tweets.split('\n')), 'filtered tweets')
summarize_tweets(tweets)
