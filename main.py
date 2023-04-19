# okay so there's multiple components
# scraper to scrape twitter
# database to store it all
# summarizer that runs off database (need to make it idempotent somehow? i mean just do how we do normally - if you keep clicking, you get same stuff, but otherwise just give latest content)
# etc

from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os
import re
import time
import sqlite3
from db import TweetDatabase
import datetime


class TwitterScraper:
    def __init__(self, p):
        self.custom_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
        self.browser = p.chromium.launch(headless=True)
        self.context = self.browser.new_context(user_agent=self.custom_user_agent)

    def login(self):
        print('logging in...')
        page = self.context.new_page()

        page.goto('https://twitter.com/home')
        page.wait_for_timeout(3000)

        # TODO should be moved outside the function probably
        load_dotenv()
        twitter_username = os.environ['username']
        twitter_password = os.environ['password']

        if not twitter_username:
            raise ValueError("twitter_username not found")

        if page.url == 'https://twitter.com/home':
            print("Didn't get redirected. Already logged-in.")
            account_switcher = page.query_selector('div[data-testid="SideNav_AccountSwitcher_Button"]')
            if account_switcher and ('@' + twitter_username) in account_switcher.text_content():
                print("In the desired account")
                return
            else:
                print("Different account. TODO: Switch or Add account")
                page.goto('https://twitter.com/i/flow/login')
                page.wait_for_timeout(3000)
        else:
            page.goto('https://twitter.com/i/flow/login')
            page.wait_for_timeout(3000)

        if not twitter_password:
            raise ValueError("twitter_password not found")

        # Log in to Twitter
        page.wait_for_selector('input[autocomplete="username"]', state="visible")
        page.type('input[autocomplete="username"]', twitter_username, delay=100)

        page.click('text=Next')

        page.wait_for_selector('input[name="password"]', state="visible")
        page.type('input[name="password"]', twitter_password, delay=100)
        page.click('text=Log in')

        page.wait_for_timeout(3000)
        print('logged in!')

    def extract_tweet_info(self, html_content):
        context = self.browser.new_context()
        try:
            page = context.new_page()
            page.set_content(html_content)

            display_name = page.query_selector("div[data-testid='User-Name'] span").inner_text()
            # TODO hideous. idk why but doing the nested xpath does not work, so i split it into separate variables
            username_div = page.query_selector("div[data-testid='User-Name']")
            username_link = username_div.query_selector('a[role="link"]').get_attribute('href')
            # also ugly, but basically drop the leading slash from link to get username
            username = username_link[1:]
            tweet_text = page.query_selector("div[data-testid='tweetText']").inner_text()
            tweet_time = page.query_selector("a[role='link'] time").get_attribute("datetime")
            try:
                num_likes = int(page.query_selector("div[data-testid='like'] div").inner_text())
            except ValueError:  # html is different when 0 likes, so just set to 0
                num_likes = 0

            tweet_link = page.query_selector("//a[contains(@href, 'status')]").get_attribute('href')
            tweet_id = re.search(r'status/(\d+)', tweet_link).group(1)

            # TODO maybe drop this idk
            # Clean up extracted values
            username = re.sub(r'\s+', ' ', username).strip()
            tweet_text = re.sub(r'\s+', ' ', tweet_text).strip()

            # parse tweet_time into datetime
            time_tweeted = datetime.datetime.strptime(tweet_time, '%Y-%m-%dT%H:%M:%S.%fZ')

            return {
                'display_name': display_name,
                'username': username,
                'tweet_text': tweet_text,
                'time_tweeted': time_tweeted,
                'num_likes': num_likes,
                'tweet_id': tweet_id
            }

        except Exception as e:
            print(html_content)
            print(e)
            return None
        finally:
            context.close()

    # get timeline div via aria-labelledby="accessible-list-1"
    # get all tweets from the timeline... with <article> tag
    # scroll it

    def get_tweets(self, tweet_count=100):
        print(f'getting {tweet_count} tweets...')
        page = self.context.new_page()

        page.goto(f'https://twitter.com')
        time.sleep(5)

        tweets = set()
        while len(tweets) < tweet_count:
            new_tweets = page.query_selector_all('//section[@aria-labelledby="accessible-list-1"]//article')
            print('new tweets', len(new_tweets))
            for tweet in new_tweets:
                # TODO o(n) list check not great, but at least capped size (could do set or even just check near end of list)
                inner_html = tweet.inner_html()
                if inner_html not in tweets and len(tweets) < tweet_count:
                    tweets.add(inner_html)

            if len(tweets) < tweet_count:
                page.evaluate(f"window.scrollBy(0, 100)")
                time.sleep(0.1)
                print(f'scrolling... (have {len(tweets)} so far)')

        return tweets


tweet_db = TweetDatabase('sqlite:///tweets.db')

with sync_playwright() as p:
    scraper = TwitterScraper(p)
    scraper.login()
    tweets = scraper.get_tweets(100)
    for tweet in tweets:
        info = scraper.extract_tweet_info(tweet)
        if info is not None:
            tweet_id = tweet_db.insert_tweet(info)
            print('inserted tweet', tweet_id)
        else:
            print('skipping tweet')
