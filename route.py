#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 12:42:51 2020

@author: marcop
"""
import json
from track import getAllTracks
from shapely.geometry import MultiLineString
from shapely import ops

class Route():
    def __init__(self, rid, rtracks, rgeomls):
        self.rid = rid
        self.rtracks = rtracks #list of track objects
        self.rgeomls = rgeomls # merged geometry
        
        
def getAllRoutes():
    at = getAllTracks()
    rlist = []
    
    
    cfile = "./config/config.json"
    
    # open input file
    with open(cfile) as cf:
            cdataset = json.load(cf)
    for route in cdataset['routes']:
        rtracks = []
        tgeomlist = []
        
        rname = route['properties']['name']
        print('Proces route: {}'.format(rname))
        
        for track in route['tracks']:
            
            #tnames.append(track)
        
            for x in range(len(at)):
                if track == at[x].tid:
                    rtracks.append(at[x])
                    tgeomlist.append(at[x].tgeomls)
                    print('Added track: {}'.format(at[x].tid))
                    break
        
        #rgeom = mergeRouteGeom(tgeomlist)
        multi_line = MultiLineString(tgeomlist)
        merged_line = ops.linemerge(multi_line)
        
        # create route obj
        
        r = Route(rname, rtracks, merged_line)
        rlist.append(r)
        
    return rlist





