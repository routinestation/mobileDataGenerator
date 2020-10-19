#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 13:55:19 2020

@author: marcop
"""

import json
from shapely.geometry import LineString, Point

class Track():
    def __init__(self, tid, tcat, tls, ths, tgeomls): 
        self.tid = tid
        self.tcat = tcat
        self.tls = tls
        self.ths = ths
        self.tgeomls = tgeomls
        
     
# returns list of track objects
def getAllTracks():
    files = []
    tlist = [] # list of track objects
    
    
    cfile = "./config/config.json"
    
    # open config file
    with open(cfile) as cf:
            cdataset = json.load(cf)
    for file in cdataset['tracksposition']['tfiles']:
        files.append(file)
    
    for file in files:
        print('Parse Tracks in file: {}'.format(file))
        # open input file
        with open(file) as f:
            dataset = json.load(f)
        for feature in dataset['features']:
        
            fname = feature['properties']['name']
            fcat = feature['properties']['category']
            fls = feature['properties']['lspeed']
            fhs = feature['properties']['hspeed']
            
            
            fgeom = LineString(feature['geometry']['coordinates'])
            print('Processed feature: {}'.format(fname))
            
            t = Track(fname, fcat, fls, fhs, fgeom)
            tlist.append(t)
        
    return tlist


def getPointsFromTrack(speedkph, intervalsec, tgeomls):
    
    pointlist = []
    
    point = Point
    
    speedms = speedkph*5/18
    
    dist = int(speedms*intervalsec)
    tlength = tgeomls.length
    
    # create points every dist meters along the line
    for i, distance in enumerate(range(0, int(tlength), dist)):
         point = tgeomls.interpolate(distance) 
         pointlist.append(point)
    
    return pointlist
    
    

    
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    