import MetadataParser

md = MetadataParser.MetadataParser()

md.addVideo("/Users/michaelwu/Documents/CSCI576/NewYorkCity/NYOne")
md.addVideo("/Users/michaelwu/Documents/CSCI576/NewYorkCity/NYTwo")
md.addLink(0,[0,0,100,100,0,600,0,0])
md.addLink(0,[150,150,250,250,0,600,0,0])
md.addLink(1,[150,150,250,250,0,600,0,0])

md.createMetadata("/Users/michaelwu/Documents/CSCI576/MultimediaFinalProject","test.json")

test=md.readMetadata("/Users/michaelwu/Documents/CSCI576/MultimediaFinalProject/test.json")

print(test)
