import argparse
import requests
import json

from pytineye import TinEyeAPIRequest

tineye = TinEyeAPIRequest('http://api.tineye.com/rest/','PUBLICKEY','PRIVATEKEY')

youtube_key = "YOUTUBEKEY"

ap = argparse.ArgumentParser()
ap.add_argument("-v","--videoID",    required=True,help="The videoID of the YouTube video. For example: https://www.youtube.com/watch?v=VIDEOID")
args = vars(ap.parse_args())

video_id    = args['videoID']

#
# Retrieve the video details based on videoID
#
def youtube_video_details(video_id):

    api_url  = "https://www.googleapis.com/youtube/v3/videos?part=snippet%2CrecordingDetails&"
    api_url += "id=%s&" % video_id
    api_url += "key=%s" % youtube_key
    
    response = requests.get(api_url)
    
    if response.status_code == 200:
        
        results = json.loads(response.content)
        
        return results

    return None


print "[*] Retrieving video ID: %s" % video_id
video_data = youtube_video_details(video_id)

thumbnails = video_data['items'][0]['snippet']['thumbnails']

print "[*] Thumbnails retrieved. Now submitting to TinEye."

url_list = []

# add the thumbnails from the API to the list
for thumbnail in thumbnails:
    
    url_list.append(thumbnails[thumbnail]['url'])
    

# build the manual URLS
for count in range(4):
    
    url = "http://img.youtube.com/vi/%s/%d.jpg" % (video_id,count)
    
    url_list.append(url)
    

results = []

# now walk over the list of URLs and search TinEye
for url in url_list:
    
    print "[*] Searching TinEye for: %s" % url
    
    try:
        result = tineye.search_url(url)
    except:
        pass
    
    if result.total_results:
        results.extend(result.matches)
    
result_urls = []
dates       = {}

for match in results:
    
    for link in match.backlinks:
        
        if link.url not in result_urls:
            
            result_urls.append(link.url)
            dates[link.crawl_date] = link.url

print            
print "[*] Discovered %d unique URLs with image matches." % len(result_urls)

for url in result_urls:
    
    print url


oldest_date = sorted(dates.keys())

print
print "[*] Oldest match was crawled on %s at %s" % (str(oldest_date[0]),dates[oldest_date[0]])