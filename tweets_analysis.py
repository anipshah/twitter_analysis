from tweepy import Cursor
from tweepy import API
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import matplotlib.pyplot as plt
import twitter_credentials
import numpy as np
import pandas as pd


class TwitterClient:

    def __init__(self, twitter_user=None):
        """
        this is the initialize method.
        :param twitter_user:
        """
        # initialize twitter client's username
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_client_api(self):
        """
        this function get client api.
        :return: twitter client
        """
        return self.twitter_client

    def get_timeline_tweet(self, number_tweets):
        """
        this function retrieve number of tweets in a list
        :param number_tweets: pass number of tweets
        :return: list of tweets on timeline
        """
        timeline_tweets_list = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(number_tweets):
            timeline_tweets_list.append(tweet)
        return timeline_tweets_list

    def get_tweets(self, number_of_tweets):
        """
        this function gives us user's timeline tweets
        :param num_tweets: pass number of tweets
        :return: user timeline as a list
        """
        user_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(number_of_tweets):
            user_timeline_tweets.append(tweet)
        return user_timeline_tweets

    def get_friend_list(self, number_of_friends):
        """
        this function gives us list of friends
        :param number_of_friends: number of friends
        :return: list of friends
        """
        friends_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(number_of_friends):
            friends_list.append(friend)
        return friends_list

    def get_followers(self, number):
        """
        this function give us last followers list of you
        :param number:
        :return:
        """
        followers_list = []
        for followers in Cursor(self.twitter_client.followers, id=self.twitter_user).items(number):
            followers_list.append(followers)
        return followers_list

    def user_details(self, user):
        """
        This method give details of user
        :param user: user name
        :return:
        """
        print("User Name: " + user.name)
        print("User Description: " + user.description)
        print("User Location: " + user.location)
        print("User Followers: " + str(user.followers_count))
        print("User Friends: " + str(user.friends_count))
        print("User Profile URL: " + str(user.profile_image_url))


class TwitterAuthenticator:
    """
    this class is for authentication
    """
    def authenticate_twitter_app(self):
        """
        this takes authentication of user from twitter_credentials file
        :return: pass auth
        """
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth


class TwitterStreamer:
    """
    Class for live tweets
    """
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)
        stream.filter(track=hash_tag_list)


class TwitterListener(StreamListener):
    """
    this class inheritance from StreamListener. it's listener which can print tweets
    """

    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename,'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data %s" % str(e))
        return True

    def on_error(self, status):
        if status == 420:
            # Returning False on_data method in case rate limit occurs
            return False
        print(status)


class TweetAnalyzer:
    """
    this class for analysis tweets
    """
    def tweet_to_data_frame(self, tweets):

        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])
        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        return df


if __name__ == "__main__":

    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()
    api = twitter_client.get_client_api()

    # this will update status on your twitter timeline
    #api.update_status("Testing from Tweepy")
    # this will add description on your profile
    #api.update_profile(description="I like Python")

    # insert username
    user_name = input("Enter User Name:")
    user = api.get_user(user_name)
    # scan last 100 tweets
    tweets = api.user_timeline(screen_name=user_name, count=100)
    # it's print first 10 tweets
     for tweet in range(10):
       print(tweets[tweet].text)
    
    # create data frame to analysis tweets
    df = tweet_analyzer.tweet_to_data_frame(tweets)
    twitter_client.user_details(user)

    # print max numbers of likes on tweet
    max_likes = np.max(df['likes'])
    print(f"Max number of likes {max_likes}")

    # print id of tweet
    print(id(tweets[10]))


    # this is plot of retweet and likes for analysis
    # likes plot
    time_likes = pd.Series(data=df['likes'].values, index=df['date'])
    time_likes.plot(figsize=(50, 30), label="likes", legend=True)

    # retweet plot
    time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
    time_retweets.plot(figsize=(50, 30), label="retweets", legend=True)
    plt.title(f'{user_name}\'s tweets')
    plt.show()

    