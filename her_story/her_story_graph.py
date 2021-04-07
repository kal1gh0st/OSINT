import networkx as nx

shared_asset_path = r"/Users/Justin/Desktop/sharedassets1.assets"


#
# Build the keyword to video mapping
#
def get_videos():
    fd = open(shared_asset_path)
    
    # we see in the hexdump that our records start at 0x11D15F8+4
    fd.seek(0x11D15F8+4)
    
    # read in the remainder of the file
    file_contents = fd.read()
    
    # close the file
    fd.close()
    
    # now let's split up based on 0x0D 0x0A
    text_records = file_contents.split("\x0D\x0A")
    
    count = 0
    
    videos = {}
    
    # loop over each record and extract the video ID and the text
    for record in text_records:
        
        # split by comma
        fields = record.split(",")
        
        # Field 3 is the text (remember 0 based index)
        text     = fields[2]
        
        # Field 5 is the video ID
        video_id = fields[4]
        
        # Dirty check to see if we hit the end of the list
        if video_id.isdigit():
        
            # Video filenames are in D{VIDEOID}.m4v format
            videos[video_id] = text
            
        else:
            break
    
    return videos


graph          = nx.Graph()
minimum_length = 5

# add whatever filters you want here to experiment
word_filters   = ["is","a","the"]

videos = get_videos()

for video_id in videos:
    
    # remove periods and question marks, convert to lowercase and split on spaces
    word_list = videos[video_id].replace(".","").replace("?","").lower().split(" ")
    
    for word in word_list:
        
        # if the word is not filtered and is long enough
        if word not in word_filters and len(word) >= minimum_length:
            
            # connect this keyword to the video ID
            v_node = graph.add_node(video_id,video=True)
            w_node = graph.add_node(word,keyword=True)
            
            graph.add_edge(video_id,word)

# write out the graph
print "[*] Generated graph with %d nodes and %d edges" % (graph.number_of_nodes(),graph.number_of_edges())
nx.write_gexf(graph,"her_story.gexf")
    
    
