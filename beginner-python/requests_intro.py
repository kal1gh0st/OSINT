import requests

good_url = "http://www.automatingosint.com"
bad_url  = "http://www.automatingosint.com/this/is/a/bad/one"

headers  = {}
headers['User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36"

response = requests.get(good_url,headers=headers)

# grab the good URL
if response.status_code == 200:
    
    print response.content

else:
    
    print "Failed to retrieve %s (%d)" % (good_url,response.status_code)
    
    
response = requests.get(bad_url,headers=headers)
    
# grab the bad URL
if response.status_code == 200:
    
    print response.content

else:
    
    print "Failed to retrieve %s (%d)" % (bad_url,response.status_code)


