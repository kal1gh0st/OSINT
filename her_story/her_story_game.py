# type "help" into any menu to get help
# search <keyword> will bring up results
# play <videoid> will play the video and remove it from your played list
# back will return you to the main menu
# quit will end the game

# Only for OSX right now, feel free to adapt for Windows

import cmd
import os

shared_asset_path = r"/Users/Justin/Desktop/sharedassets1.assets"
video_directory   = r"/Users/justin/Desktop/herstoryvideos"
played_list       = "played.txt"

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
    
    keywords = {}
    
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
            keywords[video_id] = text
            
        else:
            break
    
    return keywords   


#
# The sub menu of the game to view videos
#
class video_interface(cmd.Cmd):
        
    def __init__(self,search_results):
        cmd.Cmd.__init__(self)
        
        self.search_results = search_results
        
        self.build_prompt()
    
    def build_prompt(self):
        
        self.prompt = "[Play a video by entering: play <VIDEOID> ]\r\n\r\n"
        
        # dirty sort the dictionary
        result_keys = self.search_results.keys()
        
        result_keys.sort()
        
        for video in result_keys:
            
            self.prompt += "[%s] %s\r\n" % (video,self.search_results[video])
        
        self.prompt += ">>> "
        
        return
    
    def do_play(self,video_id):
        
        # remove the video from the list
        del self.search_results[video_id]

        # save the file to our list
        fd = open(played_list,"ab")
        fd.write("%s\r\n" % video_id)
        fd.close()
        
        os.system("open %s/D%s.m4v" % (video_directory,video_id))
        
        # now build prompt with latest video filtered out
        self.build_prompt()
        
        pass
    
    def do_back(self,args):
        return True
    
   
    

#
# The main menu of the game
#
class main_game(cmd.Cmd):
    
    prompt = "(Main Menu)"
    
    def __init__(self,videos):
        cmd.Cmd.__init__(self)
        
        self.videos    = videos
        self.first_run = True
        
    def do_quit(self, args):
        return True

    def do_search(self, search_keywords):
        
        if search_keywords != "":
            
            # grab the already played videos to filter out
            if os.path.exists(played_list) and self.first_run:
                fd = open(played_list,"rb")
                played = fd.read().splitlines()
                fd.close()
                
                for video in played:
                    try:
                        del self.videos[video]
                    except:
                        pass
                
                self.first_run = False
                    
            # farmboy algorithm to find keywords in video files
            keywords = search_keywords.split(" ")
            
            results  = {}
            
            for video in self.videos:
                
                for keyword in keywords:
                    
                    if keyword in self.videos[video]:
                        
                        if not results.has_key(video):
                            results[video] = self.videos[video]
            
            video_menu = video_interface(results)
            video_menu.cmdloop()
            
        pass

# get the list of keywords
videos = get_videos()

main_menu = main_game(videos)
main_menu.cmdloop()
