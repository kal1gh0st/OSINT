import requests
import requests_oauthlib
import os
import urllib2
import base64
import time
import Imagga
import json
from PIL import Image
from pprint import pprint

# initialize the API client
api_client = Imagga.swagger.ApiClient(api_server="https://api.imagga.com/v1")

# authentication setting using user name and password
api_client.username = 'IMAGGA_USER'
api_client.password = 'IMAGGA_PWD'


custom_tags = set(["gun","revolver","weapon","pistol","firearm","machine gun","rifle"])

client_key    = "KEY"
client_secret = "SECRET"
token         = "TOKEN"
token_secret  = "TOKEN_SECRET"

oauth = requests_oauthlib.OAuth1(client_key,client_secret,token,token_secret)

#
# Download Tweets from a user profile
#
def download_tweets(screen_name,max_id=None):
    
    api_url  = "https://api.twitter.com/1.1/statuses/user_timeline.json?"
    api_url += "screen_name=%s&" % screen_name
    api_url += "count=200"
    
    if max_id is not None:
        api_url += "&max_id=%d" % max_id

    # send request to Twitter
    response = requests.get(api_url,auth=oauth)
    
    if response.status_code == 200:
        
        tweets = json.loads(response.content)
        
        return tweets
    
    else:
        
        print "[*] Twitter API FAILED! %d" % response.status_code
    

    return None

#
# Takes a username and begins downloading all Tweets
#
def download_all_tweets(username):
    full_tweet_list = []
    max_id          = 0
    
    # grab the first 200 Tweets
    tweet_list   = download_tweets(username)
    
    # grab the oldest Tweet
    if tweet_list is None:
        return
    
    oldest_tweet = tweet_list[-1]
    
    # continue retrieving Tweets
    while max_id != oldest_tweet['id']:
    
        full_tweet_list.extend(tweet_list)

        # set max_id to latest max_id we retrieved
        max_id = oldest_tweet['id']         

        print "[*] Retrieved: %d Tweets (max_id: %d)" % (len(full_tweet_list),max_id)
    
        # sleep to handle rate limiting
        time.sleep(3)
        
        # send next request with max_id set
        tweet_list = download_tweets(username,max_id-1)
    
        # grab the oldest Tweet
        if len(tweet_list):
            oldest_tweet = tweet_list[-1]
        

    # add the last few Tweets
    full_tweet_list.extend(tweet_list)
        
    # return the full Tweet list
    return full_tweet_list 
    

#
# Uploads image file to Imagga for processing.
#
def upload_file(image_path):

    try:
        content_api = Imagga.ContentApi(api_client)
        response = content_api.upload(image_path)    

        return response.to_dict()["uploaded"][0]["id"]

    except:

        return None

#
# Submits an uploaded file to the tagging API.
#
def tag_image(content_id):
    
        tagging_api = Imagga.TaggingApi(api_client)
        
        response = tagging_api.tagging(content=content_id)
        result   = response.to_dict()
        
        tags = []
        
        for i in result['results'][0]['tags']:
    
            tags.append(i['tag'])
    
        tags = set(tags)
    
        matches = tags.intersection(custom_tags)
    
        if len(matches):
            print "[*] Image matches! => ",
            
            for match in matches:
                print match,
            
            return True
    
        return False

#
# Splits image into thirds both vertically and horizontally.
#
def split_image(image_path):
    
    ext = image_path.split(".")[-1]
    
    im = Image.open(image_path)
    width,height = im.size
    
    step_horizontal = width / 3
    step_vertical   = height / 3

    for i in range(3):
        
        start = i*step_horizontal
        end   = start + step_horizontal
        
        box = (0,start,width,end)
        
        new = im.crop(box)
        
        new.save("test.%s" % ext)

        content_id = upload_file("test.%s" % ext)
        
    
        if content_id is not None:
            
            result = tag_image(content_id)
            
            if result == True:
                
                return result

    for i in range(3):
    
        start = i*step_vertical
        end   = start + step_vertical
    
        box = (start,0,end,height)
    
        new = im.crop(box)
    
        new.save("test.%s" % ext)
    
        content_id = upload_file("test.%s" % ext)
    
    
        if content_id is not None:
    
            result = tag_image(content_id)
    
            if result == True:
    
                return result
    return False
               
#
# Wrapper function that kicks off the entire detection process.
#
def detect_guns(image_path):    

    print "[*] Trying image %s" % image_path
    
    # test the full image first
    content_id = upload_file(image_path)
    
    if content_id != None:
        result = tag_image(content_id)
    
        if result is False:
        
            result = split_image(image_path)
            return result
        
        else:
            
            print "[*] Image matches!"
            return True
            
# set exact path here
# detect_guns("/Users/justin/Desktop/testimage.jpg")

full_tweet_list = download_all_tweets("sikdrive_corn")

print "[*] Retrieved %d Tweets. Processing now..." % len(full_tweet_list)

if not os.path.exists("gunphotos"):
    os.mkdir("gunphotos")

photo_count = 0
match_count = 0

for tweet in full_tweet_list:
        
    if tweet.has_key("extended_entities"):
        if tweet['extended_entities'] is not None:
            if tweet['extended_entities'].has_key("media"):
                
                for media in tweet['extended_entities']['media']:
                    
                    print "[*] Downloading photo %s" % media['media_url']

                    photo_count += 1
                    
                    response = requests.get(media['media_url'])

                    file_name = media['media_url'].split("/")[-1]
                    
                    # write out the file
                    fd = open("gunphotos/%s" % file_name,"wb")
                    fd.write(response.content)
                    fd.close()
                    
                    # now test for guns!
                    result = detect_guns("gunphotos/%s" % file_name)
                    
                    if result != True:
                        os.remove("gunphotos/%s" % file_name)
                    else:
                        match_count += 1

print "[*] Finished! Checked %d photos and detected %d with weapons." % (photo_count,match_count)