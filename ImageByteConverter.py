'''*****************************************************************************
File: ImageByteConverter.py
Written By: Michael Wu
Class: CSCI 576
Project: Hypermedia Player

Purpose: QImage reads in a byte format in 888 RGB format. The byte stream for
each pixel will be a byte for red, blue, and green. While the given images
seperate the red, green, and blue bytes. numpy is used and then returns the
correct formatted byte stream.

Frame Format (frame.rgb): Same as Assignment 2 where the resolution is 352x288 with
 each .rgb file containing 352*288 red bytes, followed by 352*288 green bytes,
 followed by 352*288 blue bytes. The frames are given in sequential order and
 there are 30 frames per second of video (9000 frames in total for each video).

*****************************************************************************'''
import numpy as np
import os
class ImageByteConverter:
    def convert(self, path):
        #path is the input of the image
        if os.path.isfile(path):
            byte_stream = np.fromfile(path,dtype = np.uint8)
            rgb_arrays=np.split(byte_stream , 3)
            #rgb_arrays[0] is red channel
            #rgb_arrays[1] is blue channel
            #rgb_arrays[2] is green channel
            #size is N pixels
            #combine into one np array nx3
            #then stream line into a single dimension
            nx3_array = np.stack((rgb_arrays[0],rgb_arrays[1],rgb_arrays[2]),axis = -1)
            flattened_array = nx3_array.ravel()
            return bytearray(flattened_array)
        else:
            print("ERROR: ImageByteConverter class unable to change the byte file.")
