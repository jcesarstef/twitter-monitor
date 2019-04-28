import requests
from twitter_scraper import get_tweets
import nosqlite
import json
import datetime
import time

# TODO
# Twitter alert
# Search for users to monitor
# Use a trve nosql database ;)

users_list = ['jcesarstef']

pages_to_dump = 10

def dump_user(username):
    dump_username = get_tweets(username, pages=pages_to_dump)
    dump = []
    for i in dump_username:
        dump.append(i)
    return dump

def save_tweet_to_db(tweet):
    conn = nosqlite.Connection('dump.nosqlite')
    dump_nosqlite = conn['dump_nosqlite']
    if len(dump_nosqlite.find({'tweetId':tweet['tweetId']})) < 1:
        dump_nosqlite.insert(tweet)
    conn.close()

def alert_deleted_tweet(deleted):
    print("Deleted Tweet: \n\n"+ str(deleted) + "\n\n")
    conn2 = nosqlite.Connection('deleted_tweets.nosqlite')
    deleted_tweets = conn2['deleted_tweets']
    deleted_tweets.insert(deleted)
    conn2.close()

def test_if_deleted():
    conn = nosqlite.Connection('dump.nosqlite')
    dump_nosqlite = conn['dump_nosqlite']
    for i in dump_nosqlite.find({'deleted':0}):
        status = requests.get("https://twitter.com/" + i['username'] + "/status/" + i['tweetId']).status_code
        if status == 404:
            alert_deleted_tweet(i)
            i['deleted'] = 1
            dump_nosqlite.insert(i)

    conn.close()

def main(username):
    dump_tweets_from_user = dump_user(username)
    for tweet in dump_tweets_from_user:
        status_code = requests.get('https://twitter.com/' + username + '/status/' + tweet['tweetId']).status_code
        if status_code == 200:
            tweet['username'] = username
            tweet['time'] = str(tweet['time'])
            tweet['deleted'] = 0
            save_tweet_to_db(tweet)
        else:
            #TODO
            pass

for user in users_list:
    main(user)
    print(user + " dumped to DB and looking for deleted tweets")
    #time.sleep(60)
    test_if_deleted()
    time.sleep(60)