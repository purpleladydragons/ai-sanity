import os
import openai
from dotenv import load_dotenv
from storage import InMemStorage
from util import path


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
    recent_tweets = InMemStorage.get_100_most_recent()

    # TODO very ugly... basically trying to work around gpt's token limit
    i = 0
    with open(path('prompts/filter'), 'r') as f:
        prepend_query = f.read()

    query = ''
    query_size = 0
    MAX_QUERY_SIZE = 2000  # slightly less than gpt3.5 limit as dumb way of avoiding overflow
    resps = []
    while i < len(recent_tweets):
        tweet = recent_tweets[i]
        username = tweet['username']
        content = tweet['tweet_text']
        tweet_id = tweet['tweet_id']
        tweet_tokens = content.split()
        if query_size + len(tweet_tokens) < MAX_QUERY_SIZE:
            query += f'Tweet {i} (@{username}/{tweet_id}): ' + ' '.join(tweet_tokens) + '\n'
            query_size += len(tweet_tokens)
        else:
            resp = chatWithGPT(prepend_query + query)
            resps.append(resp)
            print(query)
            query = ''
            query_size = 0
        i += 1

    if len(query) > 0:
        resp = chatWithGPT(prepend_query + query)
        print(query)
        resps.append(resp)

    return '\n'.join(resps)


def summarize_tweets(tweets):
    with open(path('prompts/summarize'), 'r') as f:
        prompt = f.read()

    print('tokens', len((prompt + ' ' + tweets).split()))
    resp = chatWithGPT(prompt + '\n' + tweets, model='gpt-4')
    return resp
