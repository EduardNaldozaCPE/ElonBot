import csv
import os
import keyHandling
import tweepy

def getUser(guildID):
    print("getUser method called")
    return keyHandling.getUser(guildID)

def getKeywords(guildID):
    keywords = keyHandling.getKeywords(guildID)
    if keywords != 404:
        print("getKeywords method called")
        return keywords
    else:
        return 404

#setUser method [REQUIRED]
def setUser(api, userString, guildID):
    keyHandling.createKeywordFile(guildID)
    keyHandling.updateUser(guildID, userString)
    user = api.get_user(userString)
    print(user.location)
    print(user.description)
    return user

#addKeyword function
def addKeyword(keyword, guildID):
    keywords = keyHandling.getKeywords(guildID)
    if keywords == 404:
        return keywords
    else:
        keywords.append(keyword)
        keyHandling.updatekeywords(guildID,keywordList=keywords)
        print(keywords)

#delKeyword function
def delKeyword(keyword, guildID):
    keywords = keyHandling.getKeywords(guildID)
    try:
        keywords.remove(keyword)
        keyHandling.updatekeywords(guildID,keywordList=keywords)
        print(keywords)
    except:
        print("no such keyword")
        
#clearKeaywords function
def clearKeys(guildID):
    keywords = keyHandling.getKeywords(guildID)
    if keywords != 404:
        keywords.clear()
        keyHandling.updatekeywords(guildID,keywordList=keywords)
        return 0
    else:
        return 404

#getRelevantTweets function
def getRelevantTweets(api, userInstance, guildID):
    recentTweets_id = []
    lastUserTweet_dic = {}
    relevantTweetIDs = []
    
    if os.path.exists(guildID+"_lastIDs.csv"):
        print(guildID+"_lastIDs.csv exists")
    else:
        open(guildID+'_lastIDs.csv', 'x', encoding='utf-8')

    #import most recent tweet id of user
    try:
        with open(guildID+"_lastIDs.csv", 'r', encoding='utf-8') as lastIDs:
            reader = csv.reader(lastIDs)
            lastUserTweet_dic = {rows[0]:rows[1] for rows in reader}
    except:
        print('error csv')
    print(lastUserTweet_dic)

    userHandle = getUser(guildID)
    keywords = getKeywords(guildID)

    #If the user does not exist in the csv file, create a new dictionary key
    if userHandle not in lastUserTweet_dic:
        lastUserTweet_dic[userHandle] = '0'

    #Using tweepy Cursor, get the max 10 most recent tweets' IDs including last most recent tweet
    #IDs stored in recentTweets_id
    for status in tweepy.Cursor(api.user_timeline, id=userInstance.id).items(10):
        if int(status.id) >= int(lastUserTweet_dic[userHandle]):
            recentTweets_id.append([status.id])

    #for each ID, check to see if the tweet contains the keyword/s. if it does, add into list of relevant tweets 
    for id in recentTweets_id:
        status = api.get_status(id[0], tweet_mode="extended")
        try:                    # Retweet
            for word in keywords:
                if word in status.retweeted_status.full_text:
                    relevantTweetIDs.append(id[0])
                    #print("[RETWEET] ", status.retweeted_status.full_text)
        except AttributeError:  # Not a Retweet
            for word in keywords:
                if word in status.full_text:
                    relevantTweetIDs.append(id[0])
                    #print(status.full_text)

    #export recent tweet of user to csv file
    if userHandle in lastUserTweet_dic:    #update an existing user's most recent tweet id
        lastUserTweet_dic[userHandle] = recentTweets_id[0][0]
        with open(guildID+"_lastIDs.csv", 'w', encoding='utf-8', newline='') as lastIDs:
            writer = csv.writer(lastIDs)
            for key in lastUserTweet_dic.keys():
                lastIDs.write("%s,%s\n"%(key,lastUserTweet_dic[key]))
    else:                                 #append new user's most recent tweet id
        with open(guildID+"_lastIDs.csv", 'a', encoding='utf-8', newline='') as lastIDs:
            writer = csv.writer(lastIDs)
            writer.writerows([[userHandle,recentTweets_id[0][0]]])

    #remove duplicate tweet IDs
    finalTweetIDS = []
    for i in relevantTweetIDs:
        if i not in finalTweetIDS:
            finalTweetIDS.append(i)
    return finalTweetIDS