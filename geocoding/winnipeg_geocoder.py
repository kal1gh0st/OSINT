import geopy
import itertools

from geopy.distance import vincenty

helper = "winnipeg manitoba"

locations = {}
locations["333 portage ave"]             = []
locations["329 hargrave st"]             = []
locations["main street and pioneer ave"] = []

# create a new Google geocoder 
geocoder = geopy.GoogleV3()

# iterate over the locations
for location in locations:
    
    # perform the geocoding
    locations[location] = geocoder.geocode("%s %s" % (location,helper))
    

# measure distance between each point
for pairs in itertools.combinations(locations.keys(),r=2):
    
    location_1 = locations[pairs[0]].point
    location_2 = locations[pairs[1]].point
    
    
    distance = vincenty(location_1,location_2).meters
    
    print "%s => %s (%fm)" % (pairs[0],pairs[1],distance)
    
    
    
    
    