'''*****************************************************************************
File: MetadataParser.py
Written By: Michael Wu
Class: CSCI 576
Project: Hypermedia Player

Purpose: To create a metadata file or read a metadata file.
This metadata file will be json file so the json library can be used

Metadata
    video sources vid1: path to video/audio
    link sources vid1:  [start frame #, end frame #, vid_dest, vid_dest start frame#]

*****************************************************************************'''
import numpy as np
import os
class Metadata:
    def __init__(self):
        self.videoSources = {}
        self.links = {}
        self.index = 0
    def addVideo(self,path):
        #directory to a path containing the video and audio sources
        abs_path = os.path.abspath(path)
        if os.path.isdir(abs_path):
            self.videoSources[self.index] = abs_path
            if self.index not in self.links:
                self.links[self.index] = []
            self.index += 1
        else:
            print("MetadataParser: addVideo() input is invalid path.")
    def deleteVideo(self,idx):
        #the idx is valid so remove
        if idx in self.videoSources:
            self.videoSources.pop(idx)
            #check all the links and see if the vid_dest is pointing there
            #remove those links
    def addLink(self,idx,linkContent):
        #given the idx of the video and the link content
        #if idx not in self.links:
        #    self.links[idx] = []
        if idx in self.videoSources and idx in self.links:
            self.links[idx].append(linkContent)
    def createMetadata(self, path):
        #create the metadata file
