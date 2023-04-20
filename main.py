from scraper import TwitterScraper
from query import filter_tweets, summarize_tweets
from emailer import send_email
from dotenv import load_dotenv
import os

email_recipient = os.getenv('email_recipient')

TwitterScraper().scrape()

tweets = filter_tweets()
print(len(tweets.split('\n')), 'filtered tweets')
summary = summarize_tweets(tweets)
send_email(summary, email_recipient)
print(summary)
