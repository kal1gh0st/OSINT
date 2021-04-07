fd = open("/Users/Justin/Desktop/sharedassets1.assets")

# we see in the hexdump that our records start at 0x11D15F8+4
fd.seek(0x11D15F8+4)

# read in the remainder of the file
file_contents = fd.read()

# close the file
fd.close()

# now let's split up based on 0x0D 0x0A
text_records = file_contents.split("\x0D\x0A")

count = 0

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
        print "D%s.m4v => %s" % (video_id,text)
    
        count += 1
        
    else:
        break

print "[*] Done. Discovered %d videos." % count