import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
import requests

CONSUMER_KEY ="GmgAEFzNzf2FahFOGMhhDxVIW"
CONSUMER_SECRET ="zmKtI4YmfOBBjlvHWrbhIHjVfCOByW7zCxpOrVTpfF9mxQUuZq"

# The access tokens can be found on your applications's Details
# page located at https://dev.twitter.com/apps (located
# under "Your access token")
ACCESS_KEY = "913598144-GmQZoKIs7cIPX2vSBXZKWHJ0DlxdaEEpKjti1lMg"
ACCESS_SECRET = "ECSCwAtH0YGblQESlCbQpl4yJhXvXVDVjBtPefTjofHTT"

t_auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
t_auth.secure = True
t_auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(t_auth)

auth = OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)

class TweetListener(StreamListener):
    # A listener handles tweets are the received from the stream.
    #This is a basic listener that just prints received tweets to standard output

    def on_data(self, data):
        print data
        return True

    def on_error(self, status):
        print status

def updateWithNewUsers():
    result = conn.execute("SELECT T.USER_ID FROM TWEETS T WHERE NOT EXISTS (SELECT 1 FROM USERS U WHERE U.USER_ID = T.USER_ID);")
    for row in result:
        # print row['user_id']
        user = api.lookup_users(row)
        screen_name = str(user.screen_name)
        location = str(user.location.encode('utf-8'))
        description = str(user.description.encode('utf-8'))
        description = description.translate(None, ':\'')
        followers = int(user.followers_count)
        statuses = int(user.statuses_count)
        # print (user_id, screen_name, location, description, followers, statuses)
        new_user = conn.execute("INSERT INTO USERS VALUES(%d, '%s', '%s', '%s', %d, %d)" %(user_id, screen_name, location, description, followers, statuses))

def updateNumVotes():
    result0 = conn.execute("SELECT COUNT(*) FROM TWEETS T WHERE T.CANDIDATE_ID = 0;")
    result1 = conn.execute("SELECT COUNT(*) FROM TWEETS T WHERE T.CANDIDATE_ID = 1;")
    result2 = conn.execute("SELECT COUNT(*) FROM TWEETS T WHERE T.CANDIDATE_ID = 2;")
    result3 = conn.execute("SELECT COUNT(*) FROM TWEETS T WHERE T.CANDIDATE_ID = 3;")
    result4 = conn.execute("SELECT COUNT(*) FROM TWEETS T WHERE T.CANDIDATE_ID = 4;")
    result5 = conn.execute("SELECT COUNT(*) FROM TWEETS T WHERE T.CANDIDATE_ID = 5;")
    # print result0

def updateVote(score, agg, vote):
    if score == 'NEU' or 'NONE':
        if agg == 'DISAGREEMENT':
            vote -= 1
        else:
            vote += 1
    else:
        if agg == 'AGREEMENT':
            if score == 'P' or score == 'P+':
                vote += 1
            else:
                vote -= 1
        else:
            if score == 'N' or score == 'N+':
                vote += 1
            else:
                vote -= 1
    return vote;

def calcWeightedVote(score, agg, vote, weight):
    if score == 'NEU' or 'NONE':
        if agg == 'DISAGREEMENT':
            vote -= 1
        else: #AGREEMENT
            vote += 1
    else:
        if agg == 'AGREEMENT':
            if score == 'P':
                vote += 1
            elif score == 'P+':
                vote += 1 + weight
            elif score == 'N':
                vote -= 1
            elif score == 'N+':
                vote += 1 + weight
        else: #DISAGREEMENT
            if score == 'N':
                vote +=  1
            elif score == 'N+':
                vote += 1 + weight
            elif score == 'P':
                vote -= 1
            elif score == 'P+':
                vote -= 1 + weight
    return vote

def getCandidateID(votes):
    val = -1
    count = 0
    topScore = 0
    candidate_num = 0
    for v in votes:
        if v != 0:
            if topScore == 0 or abs(topScore) < abs(v):
                topScore = v
                candidate_num = count
        count += 1
    if topScore > 0:
        return candidate_num, True
    elif topScore < 0:
        return candidate_num, False
    return -1, False

def determineScore(scores):
    val = -1
    count = 0
    topScore = 0
    candidate_num = 0
    for v in scores:
        if v != 0:
            if topScore == 0 or abs(topScore) < abs(v):
                topScore = v
                candidate_num = count
        count += 1
    if topScore > 0:
        return topScore, candidate_num, True
    elif topScore < 0:
        return topScore, candidate_num, False
    return 0, -1, False


def updateVotesTable():
    result = conn.execute("SELECT DISTINCT T.USER_ID FROM TWEETS T WHERE NOT EXISTS (SELECT 1 FROM VOTES V WHERE T.USER_ID = V.VOTE_ID);")
    for row in result:
        user_id = int(row['user_id'])
        tweets = conn.execute("SELECT * FROM TWEETS T, USERS U WHERE T.USER_ID = %d;" %(user_id))
        tweet_count = 1
        votes = [0,0,0,0,0,0] #list of vote tally for each candidate
        for t in tweets:
            tweet_id = int(t['tweet_id'])
            candidate_id = int(t['candidate_id'])
            nlp_results = conn.execute("SELECT * FROM NLP_RESULTS N WHERE N.NLP_ID = %d;" %(tweet_id))
            vote = 0
            for nlp in nlp_results:
                nlp_id = int(nlp['nlp_id'])
                score = str(nlp['score'])
                agg = str(nlp['agreement'])
                if nlp_id == tweet_id:
                    vote = updateVote(score, agg, vote)
                    votes[candidate_id] += vote
                # confidence = int(nlp['confidence'])
            tweet_count += 1
        print 'tweet_count: ', tweet_count
        print votes
        notEmpty = False
        for v in votes:
            if v != 0:
                notEmpty = True
        if notEmpty:
            cand, pos = getCandidateID(votes)
            if pos:
                new_vote = conn.execute("INSERT INTO VOTES VALUES (%d, %d)" %(user_id, cand))

def updateWeightedVotesTable(weight):
    result = conn.execute("SELECT DISTINCT T.USER_ID FROM TWEETS T;")
    for row in result:
        user_id = int(row['user_id'])
        tweets = conn.execute("SELECT * FROM TWEETS WHERE USER_ID = %d;" %(user_id))
        tweet_count = 1
        scores = [0, 0, 0, 0, 0, 0] #list of scores for each candidate
        for t in tweets:
            tweet_id = int(t['tweet_id'])
            candidate_id = int(t['candidate_id'])
            nlp_results = conn.execute("SELECT * FROM NLP_RESULTS WHERE NLP_ID = %d" %(tweet_id))
            vote = 0
            nlp_count = 0
            for nlp in nlp_results:
                nlp_id = int(nlp['nlp_id'])
                score = str(nlp['score'])
                agg = str(nlp['agreement'])
                if nlp_id == tweet_id and nlp_count == 0:
                    vote = calcWeightedVote(score, agg, vote, weight)
                    scores[candidate_id] += vote
                    nlp_count += 1
            tweet_count += 1
        notEmpty = False
        for s in scores:
            if s != 0:
                notEmpty = True
        if notEmpty:
            score, cand, pos = determineScore(scores)
            side = 'PRO'
            if not pos:
                side = 'CON'
            new_vote = conn.execute("INSERT INTO WEIGHTED_VOTES VALUES (%d, %d, %d, '%s');" %(user_id, cand, score, side))

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
engine = create_engine("postgresql://ddominguez:u8paz3500k@aa1n9lvw4037g4u.cgtfuf6sekto.us-west-2.rds.amazonaws.com:5432/twitterpoll_db")
conn = engine.connect()
twitterStream = Stream(auth,TweetListener())
count = 0
while(count < 1):
    try:
        # updateWithNewUsers()
        # updateNumVotes()
        # updateVotesTable()
        updateWeightedVotesTable(1) #using a weight of one
    except tweepy.TweepError as e:
        print(e)
    count += 1
conn.close()
