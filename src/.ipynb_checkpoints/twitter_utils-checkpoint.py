import tweepy
import pandas as pd
import numpy as np
import json
import datetime as dt
from afinn import Afinn

def authenticate():
    """
    Authenticate Twitter
    """
    
    try:
        with open(r'..//reference files//api_keys//twitter_credentials.json') as f:
            data = json.load(f)
    except Exception as e:
        print("Something went wrong",e)
        
    try:
        auth = tweepy.AppAuthHandler(data['api_key'], data['api_secret_key'])
        api = tweepy.API(auth)
        print('Authenticated')
        return api

    except:
        print("Please check your api keys")
        return None

def get_tweets_replied_to(api,user_names):
    """
    Returns a list of dictionaries
    """
    
    tweets = []

    for user in user_names:
        
        try:
            user = api.get_user(user)
            print("User {} found. Extracting Tweets".format(user.screen_name))
            
            replies=[]
            
            for tweet in tweepy.Cursor(api.search,q='to:'+user_name, result_type='recent', tweet_mode='extended', timeout=999999).items():
                if hasattr(tweet, 'in_reply_to_status_id_str'):
                    replies.append(tweet)

            for i in range(len(replies)):
                temp = replies[i]._json
                tweet = {
                    'id' : temp['id'],
                    'full_text' : temp['full_text'],
                    'user_id' : temp['user']['id'],
                    'screen_name ': temp['user']['screen_name'],
                    'location' : temp['user']['location'],
                    'tweet_created_at' : temp['created_at'],
                    'user_created_at' : temp['user']['created_at'],
                    'user_follower_count' : temp['user']['followers_count'],
                    'user_friend_count' : temp['user']['friends_count'],
                    'hashtags' : temp['entities']['hashtags'],
                    'user_mentions' : temp['entities']['user_mentions'],
                    'retweet_count' : temp['retweet_count'] ,
                    'favorite_count' : temp['favorite_count']
                }
            tweets.append(tweet)
            
        except:
            print("Invalid User: {}".format(user))
        
    tweets.to_csv('../data/raw/tweets_replied_to_{}.csv'.format(dt.datetime.now().strftime('%Y_%m_%d_%H_%m')))
    return tweets


def get_tweets_from_user_timeline(api, user_names):
    """
    Function scans all the tweets for a user. Saves tweets.csv in data folder
    """
     
    for user in user_names:

        try:
            user = api.get_user(user)
            print("User {} found. Extracting Tweets".format(user.screen_name))

            replies=[]

            for tweet in tweepy.Cursor(api.user_timeline, screen_name='SEPTA_Social', tweet_mode='extended', timeout=999999).items():
                replies.append(tweet)
                tweets = []

            for i in range(len(replies)):
                temp = replies[i]._json
                tweet = {
                    'id' : temp['id'],
                    'full_text' : temp['full_text'],
                    'user_id' : temp['user']['id'],
                    'screen_name ': temp['user']['screen_name'],
                    'tweet_created_at' : temp['created_at'],
                    'user_created_at' : temp['user']['created_at'],
                    'user_follower_count' : temp['user']['followers_count'],
                    'user_friend_count' : temp['user']['friends_count'],
                    'hashtags' : temp['entities']['hashtags'],
                    'user_mentions' : temp['entities']['user_mentions'],
                    'retweet_count' : temp['retweet_count'] ,
                    'favorite_count' : temp['favorite_count']
                }
                tweets.append(tweet)

        except:
            print("Invalid User: {}".format(user))
        
    tweets.to_csv('../data/raw/tweets_from_user_timeline_{}.csv'.format(dt.datetime.now().strftime('%Y_%m_%d_%H_%m')))
    
    return pd.DataFrame(tweets)


def get_names(names):
    """
        Lambda function for getting username mentions
    """
    l_of_names = []
    for name in names:
        if name['screen_name'] not in l_of_names:
            l_of_names.append(name['screen_name'])
            return name['screen_name']
        
        
def process_tweets(tweet_list):
    """
        Returns a DataFrame with additional features and clean data
    """

    for col in ['tweet_created_at','user_created_at']:
        tweet_list[col] =pd.to_datetime(tweet_list[col])

    tweet_list['hashtags'] = tweet_list.loc[tweet_list.hashtags.apply(lambda x: len(x))>0, 'hashtags'].apply(lambda x: x[0]['text'])
    tweet_list['hashtags'].fillna('', inplace=True)

    tweet_list['user_names'] = tweet_list['user_mentions'].apply(lambda x: get_names(x))
    tweet_list['full_text'] = tweet_list['full_text'].str.replace("(?:[^a-zA-Z0-9 ]|(?<=['\"])s)","", regex=True)
    
    tweet_list['sentiment_score'] = tweet_list['full_text'].apply(lambda x: af.score(x))

    tweet_list['sentiment'] = np.where(tweet_list['sentiment_score']>0,'positive','negative')
    tweet_list['sentiment'] = np.where(tweet_list['sentiment_score']==0,'neutral',tweet_list['sentiment'])
    
    tweet_list['year'] = tweet_list['tweet_created_at'].dt.year
    tweet_list['month'] = tweet_list['tweet_created_at'].dt.month
    tweet_list['day'] = tweet_list['tweet_created_at'].dt.day
    tweet_list['hour'] = tweet_list['tweet_created_at'].dt.hour

    tweet_list['hour'] = tweet_list['hour'].astype(int)
    tweet_list['year'] = tweet_list['year'].astype(int)
    tweet_list['month'] = tweet_list['month'].astype(int)
    tweet_list['day'] = tweet_list['day'].astype(int)

    tweet_list['hour_of_day'] = ''
    tweet_list['hour_of_day'] = np.where(tweet_list['hour']<12,'morning',tweet_list['hour_of_day'])
    tweet_list['hour_of_day'] = np.where((tweet_list['hour']>=12)&(tweet_list['hour']<=16),'afternoon',tweet_list['hour_of_day'])
    tweet_list['hour_of_day'] = np.where((tweet_list['hour']>=17)&(tweet_list['hour']<=20),'evening',tweet_list['hour_of_day'])
    tweet_list['hour_of_day'] = np.where(tweet_list['hour']>20,'night',tweet_list['hour_of_day'])
    
    tweet_list['hour_of_day'] = pd.Categorical(tweet_list['hour_of_day'], ordered = True, categories = ['morning','afternoon','evening','night'])
    
    return tweet_list