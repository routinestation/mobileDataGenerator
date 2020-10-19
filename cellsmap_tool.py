#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 17:04:36 2020

@author: marcop
"""

"""
This tool generates the network configuration layers for QGIS
"""

import os
import math
from configparser import ConfigParser
import json
import fiona
from shapely.geometry import Point
from fiona.crs import from_epsg
from collections import OrderedDict



def loadENBs():
    # Load the configuration file
    config = ConfigParser()
    config.read('./config/mapconfig.ini')

    dataset = []
    enbsfile = []

    if config.has_option('enbsutm', 'file'):
        enbsfile = config['enbsutm'].get('file')
        enbsfile = enbsfile.strip()
        if(len(enbsfile) == 0):
            print ("ENBs file not declared")
        else :
            print('***** File ENBs: %s *****' % enbsfile)
            # open input file
            with open(enbsfile) as f:
                dataset = json.load(f)
    else:
        print ("ENBs conversion aborted")
    return dataset, enbsfile


def createHexagon(xc, yc, r):

    # a = 150 # apotema of polygon

    # r = a * 2 / math.sqrt(3)


    pointslist = []

    # generate cells (hexagons)
    for i in range(30, 420, 60):

        xp = xc + r * math.sin(math.radians(i))
        yp = yc + r * math.cos(math.radians(i))
        #print('i = {} x = {}, y = {}'.format(i, xp, yp))
        pointslist.append((xp,yp))

    return pointslist



def generateCells():

    r = 100


    ds, enbsfile = loadENBs()

    # Output settings
    output_driver = "GeoJSON"
    output_crs = from_epsg(32632)
    output_cells_schema = {
            'geometry': 'Polygon',
            'properties': OrderedDict([
                ('cellid', 'str')
                ])
            }



    # generate cells3; cells of 120 degrees
    sector3 = 1
    for s3 in range(90, 360, 120):
        # open output cells3 file
        fn3 = os.path.splitext(enbsfile)[0]+'_3CELLS_{}'.format(s3)
        fe3 = os.path.splitext(enbsfile)[1]
        fileout3 = fn3+fe3
        print("***** Output file: %s *****" % fileout3)
        c3file = fiona.open(
            fileout3,
            'w',
            driver=output_driver,
            crs=output_crs,
            schema=output_cells_schema)

        # Parse the features
        for feature in ds['features']:
            #fenbid = feature['properties']['enbid']
            fgeomenb = Point(feature['geometry']['coordinates'])
            xc= fgeomenb.x
            yc = fgeomenb.y
            polygon = []
            #print('Sector {}'.format(s3))

            xp = xc + r * math.sin(math.radians(s3))
            yp = yc + r * math.cos(math.radians(s3))

            polygon = createHexagon( xp, yp, r)


            # save the resulting record
            recordc3 =  {
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [polygon]
                    },
                'properties': OrderedDict([
                    ("cellid", 'C{}'.format(sector3))
                    ])
                }
            c3file.write(recordc3)
        sector3 += 1
        c3file.close()





def initialize():

   generateCells()

#start here
initialize()
