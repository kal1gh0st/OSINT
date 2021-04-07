import os
import requests
import smtplib
import time

from email.mime.text import MIMEText

alert_email_account  = "YOUREMAIL@GMAIL.COM"
alert_email_password = "YOURPASSWORD" 
searx_url            = "http://localhost:8888/?"
max_sleep_time       = 120

# read in our list of keywords
with open("keywords.txt","r") as fd:
    file_contents = fd.read()
    keywords      = file_contents.splitlines()

if not os.path.exists("keywords"):
    os.mkdir("keywords")

#
# Send email to you!
#
def send_alert(alert_email):
    
    email_body = "The following are keyword hits that were just found:\r\n\r\n"
    
    # walk through the searx results
    if alert_email.has_key("searx"):
        
        for keyword in alert_email['searx']:
            
            email_body += "\r\nKeyword: %s\r\n\r\n" % keyword
            
            for keyword_hit in alert_email['searx'][keyword]:
                
                email_body += "%s\r\n" % keyword_hit
                
    # walk through pastebin results
    if alert_email.has_key("pastebin"):
        
        for paste_id in alert_email['pastebin']:
            
            email_body += "\r\nPastebin Link: https://pastebin.com/%s\r\n" % paste_id
            email_body += "Keywords:%s\r\n" % ",".join(alert_email['pastebin'][paste_id][0])
            email_body += "Paste Body:\r\n%s\r\n\r\n" % alert_email['pastebin'][paste_id][1]
            
           
    # build the email message
    msg = MIMEText(email_body)
    msg['Subject'] = "AutomatingOSINT.com Keyword Alert"
    msg['From']    = alert_email_account
    msg['To']      = alert_email_account
    
    server = smtplib.SMTP("smtp.gmail.com",587)
    
    server.ehlo()
    server.starttls()
    server.login(alert_email_account,alert_email_password)
    server.sendmail(alert_email_account,alert_email_account,msg.as_string())
    server.quit()
    
    print "[!] Alert email sent!"
    
    return

#
# Check if the URL is new.
#
def check_urls(keyword,urls):
    
    new_urls = []
    
    if os.path.exists("keywords/%s.txt" % keyword):
        
        with open("keywords/%s.txt" % keyword,"r") as fd:
            
            stored_urls = fd.read().splitlines()
        
        for url in urls:
            
            if url not in stored_urls:
                
                print "[*] New URL for %s discovered: %s" % (keyword,url)
                
                new_urls.append(url)
                
    else:
        
        new_urls = urls
        
    # now store the new urls back in the file
    with open("keywords/%s.txt" % keyword,"ab") as fd:
        
        for url in new_urls:
            fd.write("%s\r\n" % url)
            
    
    return new_urls


#
# Poll Searx instance for keyword.
#
def check_searx(keyword):
    
    hits = []
    
    # build parameter dictionary
    params               = {}
    params['q']          = keyword
    params['categories'] = 'general'
    params['time_range'] = 'day' #day,week,month or year will work
    params['format']     = 'json'
    
    print "[*] Querying Searx for: %s" % keyword
    
    # send the request off to searx
    try:
        response = requests.get(searx_url,params=params)
        
        results  = response.json()
        
    except: 
        return hits
    
    # if we have results we want to check them against our stored URLs
    if len(results['results']):
        
        urls = []
        
        for result in results['results']:
            
            if result['url'] not in urls:
            
                urls.append(result['url'])
            
        hits = check_urls(keyword,urls)
    
    return hits

#
# Check Pastebin for keyword list.
#
def check_pastebin(keywords):
    
    new_ids    = []
    paste_hits = {}
    
    # poll the Pastebin API
    try:
        response = requests.get("http://pastebin.com/api_scraping.php?limit=500")
    except:
        return paste_hits
    
    # parse the JSON
    result   = response.json()
    
    # load up our list of stored paste ID's and only check the new ones
    if os.path.exists("pastebin_ids.txt"):
        with open("pastebin_ids.txt","rb") as fd:
            pastebin_ids = fd.read().splitlines()
    else:
        pastebin_ids = []
        
    for paste in result:
    
        if paste['key'] not in pastebin_ids:
            
            new_ids.append(paste['key'])
    
            # this is a new paste so send a secondary request to retrieve
            # it and then check it for our keywords 
            paste_response       = requests.get(paste['scrape_url'])
            paste_body_lower     = paste_response.content.lower()
            
            keyword_hits = []
            
            for keyword in keywords:
                
                if keyword.lower() in paste_body_lower:
                    keyword_hits.append(keyword)
                
            if len(keyword_hits):      
                paste_hits[paste['key']] = (keyword_hits,paste_response.content)
            
                print "[*] Hit on Pastebin for %s: %s" % (str(keyword_hits),paste['full_url'])

    # store the newly checked IDs 
    with open("pastebin_ids.txt","ab") as fd:
        
        for pastebin_id in new_ids:
            
            fd.write("%s\r\n" % pastebin_id)
    
    print "[*] Successfully processed %d Pastebin posts." % len(new_ids)
    
    return paste_hits


def check_keywords(keywords):
    
    alert_email          = {}
    
    time_start = time.time()
    
    # use the list of keywords and check each against searx
    for keyword in keywords:
        
        # query searx for the keyword
        result = check_searx(keyword)
        
        if len(result):
            
            if not alert_email.has_key("searx"):
                alert_email['searx'] = {}            
            
            alert_email['searx'][keyword] = result
        
    # now we check Pastebin for new pastes
    result = check_pastebin(keywords)
    
    if len(result.keys()):
        
        # we have results so include it in the alert email
        alert_email['pastebin'] = result
    
        
    time_end   = time.time()
    total_time = time_end - time_start
    
    # if we complete the above inside of the max_sleep_time setting
    # we sleep. This is for Pastebin rate limiting
    if total_time < max_sleep_time:
        
        sleep_time = max_sleep_time - total_time
        
        print "[*] Sleeping for %d s" % sleep_time
        
        time.sleep(sleep_time)
    
    return alert_email


# execute your search once first to populate results
check_keywords(keywords)

# now perform the main loop
while True:
    
    alert_email = check_keywords(keywords)
    
    if len(alert_email.keys()):
        
        # if we have alerts send them out
        send_alert(alert_email)
        
    
    
    
        
