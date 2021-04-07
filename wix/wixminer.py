import requests
import json
import os
import argparse
import sys

ap = argparse.ArgumentParser()
ap.add_argument("-d","--domain",    required=False,help="The domain to target ie. cnn.com")
args = vars(ap.parse_args())

domain = args['domain']

if not os.path.exists(domain):
    os.mkdir(domain)

# send off first request
response = requests.get("http://%s" % domain)

print "[*] Trying domain: %s" % domain

public_model = response.content.find("publicModel")

if public_model == -1:
    print "[!] Could not locate Javascript code. Is this a Wix domain?"
    sys.exit(0)
    
end_model    = response.content[public_model:].find(";")

json_blob    = response.content[public_model:public_model+end_model]
json_blob    = json_blob.split("=",1)[1]

model        = json.loads(json_blob)

# now iterate over the URL list
for url in model["pageList"]["pages"]:
    
    # grab the first JSON url
    json_response = requests.get(url["urls"][0])
    
    page     = json.loads(json_response.content)
    
    # grab the SEO friendly version of the page
    #http://yoursite.com/?_escaped_fragment=page_name/page_id
    print "[*] Retrieving page: %s" % page['pageUriSEO']
    seo_url  = "http://%s/?_escaped_fragment_=%s/%s" % (domain,page['pageUriSEO'],url['pageId'])
    
    response = requests.get(seo_url)
    
    # store the HTML page
    with open("%s/%s.html" % (domain,page['pageUriSEO']),"wb") as fd:
        fd.write(response.content)
    
    # store the raw JSON
    with open("%s/%s.json" % (domain,page['pageUriSEO']),"wb") as fd:
        fd.write(json_response.content)
        
    
    