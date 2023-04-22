import os
import openai
from dotenv import load_dotenv
from storage import InMemStorage
from util import path
from typing import List, Dict


def prompt_gpt(prompt, model='gpt-3.5-turbo'):
    completion = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content


load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')


def chunk_tweets(tweets: List[Dict[str, str]]) -> List[List[str]]:
    """
    The full list of tweets may sometimes be too long to include in a single query to GPT.
    This method chunks the tweets into smaller lists. We use a rough estimate of max token length
    based on number of words. Once this limit is exceeded, a new query is started.

    :param tweets: list of tweet objects
    :return: list of queries, which are themselves a list of tweet strings, e.g [["tweet1", "tweet2"], ["tweet3"]]
    """

    max_query_size = 2000  # slightly less than gpt3.5 limit as dumb way of avoiding overflow
    queries = [[]]

    query_len = 0
    s = 0
    for e, tweet in enumerate(tweets):
        tweet_id = tweet['tweet_id']
        username = tweet['username']
        content = tweet['tweet_text']

        tweet_text = f'Tweet {e-s} (@{username}/{tweet_id}): {content}'
        l = len(tweet_text.split())
        if query_len + l < max_query_size:
            query_len += l
            queries[-1].append(tweet_text)
        else:
            queries.append([tweet_text])
            query_len = l
            s = e

    return queries


def filter_tweets():
    recent_tweets = InMemStorage.get_100_most_recent()

    with open(path('prompts/filter'), 'r') as f:
        prepend_query = f.read()

    resps = []
    list_of_tweet_chunks = chunk_tweets(recent_tweets)
    for tweet_chunk in list_of_tweet_chunks:
        query = prepend_query + '\n' + '\n'.join(tweet_chunk)
        print('QUERY:', query)
        resp = prompt_gpt(prepend_query + query)
        resps.append(resp)

    return '\n'.join(resps)


def summarize_tweets(tweets):
    with open(path('prompts/summarize'), 'r') as f:
        prompt = f.read()

    print('tokens', len((prompt + ' ' + tweets).split()))
    resp = prompt_gpt(prompt + '\n' + tweets, model='gpt-4')
    return resp
