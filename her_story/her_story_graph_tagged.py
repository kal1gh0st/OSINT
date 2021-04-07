import networkx as nx
from topia.termextract import tag

shared_asset_path = r"/Users/Justin/Desktop/sharedassets1.assets"

# initialize the tagger
tagger = tag.Tagger()
tagger.initialize()


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
videos = get_videos()

for video_id in videos:
    
    # tag text using topia
    tagged_list = tagger(videos[video_id])
    
    for result in tagged_list:
        
        # results are in the form of [keyword,type,keyword]
        found_result = False
        
        # nouns or plural nouns
        if result[1] == "NN" or result[1] == "NNS":
            
            graph.add_node(result[0],node_type="Noun")
            found_result = True
            
        # or is it a proper noun 
        elif result[1] == "NNP" or result[1] == "NNPS":
            
            graph.add_node(result[0],node_type="Proper Noun")
            found_result = True
            
        if found_result:
            graph.add_node(video_id,node_type="Video")
            graph.add_edge(video_id,result[0])
            
            
# write out the graph
print "[*] Generated graph with %d nodes and %d edges" % (graph.number_of_nodes(),graph.number_of_edges())
nx.write_gexf(graph,"her_story_clean.gexf")
    
    