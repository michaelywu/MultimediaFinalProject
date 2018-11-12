import MetadataParser

md = MetadataParser.MetadataParser()

md.addVideo("/Users/michaelwu/Documents/CSCI576/NewYorkCity/NYOne")
md.addVideo("/Users/michaelwu/Documents/CSCI576/NewYorkCity/NYTwo")
#[x1,y1,xLength,yLength,start frame #, end frame #, vid_dest, vid_dest start frame#]
md.addLink(0,[0,0,100,100,0,600,1,0])
md.addLink(0,[150,150,100,100,0,600,0,0])
md.addLink(1,[64,64,50,100,0,500,0,0])

md.createMetadata("/Users/michaelwu/Documents/CSCI576/MultimediaFinalProject","test.json")

test=md.readMetadata("/Users/michaelwu/Documents/CSCI576/MultimediaFinalProject/test.json")

#print(test)
