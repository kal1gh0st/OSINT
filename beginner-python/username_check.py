import requests

username = "jms_dot_py"

site_list = [
"https://twitter.com/",
"https://instagram.com/",
"https://ask.fm/",
"http://pastebin.com/u/"
]

for site in site_list:
    
    username_url = "%s%s" % (site,username)
    
    response = requests.get(username_url,allow_redirects=False)
    
    if response.status_code == 200:
        
        print "[*] Hit! %s" % username_url
        
    elif response.status_code == 301:
        
        print response.headers['Location']
        