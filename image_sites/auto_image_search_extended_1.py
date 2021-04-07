import requests
import json
import os

search_name      = "BellingcatRaqqah"
southwest_corner = "35.92865398664048,38.96073818206787"
northeast_corner = "35.97895687940326,39.06510829925537"

# we use the coordinates
lat_min,long_min = southwest_corner.split(",")
lat_max,long_max = northeast_corner.split(",")

#
# Function responsible for sending requests to Panoramio API
#
def send_panoramio_request(start,end):

    api_url  = "http://www.panoramio.com/map/get_panoramas.php?set=full&"
    api_url += "from=%d&to=%d&" % (start,end)
    api_url += "minx=%s&miny=%s&maxx=%s&maxy=%s&" % (long_min,lat_min,long_max,lat_max)
    api_url += "size=medium&mapfilter=false"
    
    response = requests.get(api_url)
    
    if response.status_code == 200:
        
        # convert to a dictionary
        search_results = json.loads(response.content)
        
        return search_results

    # there was a problem
    return None


#
# Use the Panaramio API to get all pictures
#
def get_all_panoramio_pictures():

    photo_list   = []
    search_start = 0
    
    # send the intial request
    search_results = send_panoramio_request(search_start,search_start+50)

    # if there was an error return nothing
    if search_results is None:
        print "[*] Error retrieving photos."
        return

    # add the current results to our list
    photo_list.extend(search_results['photos'])

    print "[*] Retrieved %d photos..." % (len(photo_list))
    
    # while there are more photos to retrieve
    while search_results['has_more'] is True:
        
        # we increase the search count by 50
        search_start += 50
        
        search_results = send_panoramio_request(search_start,search_start+50)
        
        if search_results is not None:
            photo_list.extend(search_results['photos'])
            
            print "[*] Retrieved %d photos..." % (len(photo_list))
            

    # return all of our photos     
    return photo_list      
    
    
#
# Write out the list of photos
#
def write_photo_list(photo_list):

    if not os.path.exists("%s" % search_name):
        os.mkdir("%s" % search_name)
    
    fd = open("%s/%s.html" % (search_name,search_name),"wb")
    fd.write("<html><head></head><body>")
    
    # walk through the list of photos and add them to our log file
    for photo in photo_list:
        fd.write("<a target='_blank' href='https://maps.google.com/?q=%f,%f'><img src='%s' border='0'></a><br/>\r\n" %
                             (photo['latitude'],photo['longitude'],photo['photo_file_url']))        
    
    # close the html file
    fd.write("</body></html>")
    fd.close()
    
    return

# grab the full list of photos from panoramio
photo_list = get_all_panoramio_pictures()

write_photo_list(photo_list)