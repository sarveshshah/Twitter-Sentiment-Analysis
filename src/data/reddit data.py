# import statements
import json
import praw
import pandas as pd

def get_data(subreddit, search_term):
    """Function extracts data from reddit API

    Arguments
    ---------
    subreddit : str
        The subreddit the comments need to be extracted from  
    search_term : str
        The search term to search for
    limit: int
        Maximum comments to be extracted

    Returns
    -------
        DataFrame -- Returns a DataFrame   
    
    Raises
    ------
    """

    # Get API keys
    with open (r"reference files\api_keys\reddit_credentials.json") as f:
        credentials = json.load(f)

    client_id = credentials['client_id'],
    client_secret = credentials['client_secret'],
    user_agent = credentials['user_agent'],
    username = credentials['username'] ,
    password = credentials['password']

    # Create a reddit object
    r = praw.Reddit(client_id = client_id ,
                    client_secret = client_secret,
                    user_agent = user_agent,
                    username = username,
                    password = password)
    
    subreddit = r.subreddit(subreddit)
    response = subreddit.search(search_term)

    topics_dict = { "title":[], 
                    "score":[], 
                    "id":[], 
                    "url":[],  
                    "comms_num": [], 
                    "created": [], 
                    "body":[],                
                    "upvote_ratio":[],
                    "comments":[]
                }

    for submission in response:
        topics_dict["title"].append(submission.title)
        topics_dict["score"].append(submission.score)
        topics_dict["id"].append(submission.id)
        topics_dict["url"].append(submission.url)
        topics_dict["comms_num"].append(submission.num_comments)
        topics_dict["created"].append(submission.created)
        topics_dict["body"].append(submission.selftext)
        topics_dict["upvote_ratio"].append(submission.upvote_ratio)
        topics_dict["comments"].append(submission.comments)

    df = pd.DataFrame(topics_dict)

    display(df.head())


get_data('a','b',1)