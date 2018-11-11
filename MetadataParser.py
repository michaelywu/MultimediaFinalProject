'''*****************************************************************************
File: MetadataParser.py
Written By: Michael Wu
Class: CSCI 576
Project: Hypermedia Player

Purpose: To create a metadata file or read a metadata file.
This metadata file will be json file so the json library can be used

Metadata
    'videos' - contain the directory path to videos
            key = some index N
            return = corresponding path
    'links' -
            key = some index N
            return = 2D list
                [x1,y1,xLength,yLength,start frame #, end frame #, vid_dest, vid_dest start frame#]

*****************************************************************************'''
import numpy as np
import json
import os
class MetadataParser:
    def __init__(self):
        self.metadata = {}
        self.metadata['videos'] = {}
        self.metadata['links'] = {}
        self.index = 0
    def addVideo(self,path):
        #directory to a path containing the video and audio sources
        abs_path = os.path.abspath(path)
        if os.path.isdir(abs_path):
            self.metadata['videos'][self.index] = abs_path
            if self.index not in self.metadata['links']:
                self.metadata['links'][self.index] = []
            self.index += 1
        else:
            print("MetadataParser: addVideo() input is invalid path.")
    def deleteVideo(self,idx):
        #the idx is valid so remove
        if idx in self.metadata['videos']:
            self.metadata['videos'].pop(idx)
            #check all the links and see if the vid_dest is pointing there
            #remove those links
    def addLink(self,idx,linkContent):
        #given the idx of the video and the link content
        #if idx not in self.links:
        #    self.links[idx] = []
        if idx in self.metadata['videos'] and idx in self.metadata['links']:
            self.metadata['links'][idx].append(linkContent)
        else:
            print("MetadataParser: addLink() unable to add the link.")
    def createMetadata(self, path,file):
        #create the metadata file
        if os.path.isdir(path):
            with open("{}/{}".format(path,file), 'w') as outfile:
                json.dump(self.metadata, outfile,indent = 4)
        else:
            print("MetadataParser: createMetadata() invalid file.")

    def readMetadata(self, path):
        if os.path.isfile(path):
            with open(path) as data_file:
                data_loaded = json.load(data_file)
                if 'videos' in data_loaded and 'links' in data_loaded:
                    return data_loaded
        else:
            print("MetadataParser: readMetadata() invalid file.")
        return None
