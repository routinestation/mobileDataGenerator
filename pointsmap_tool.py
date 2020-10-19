#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 17:04:36 2020

@author: marcop
"""

"""
This tool generates the points on the roads in QGIS
"""

import os
import math
from configparser import ConfigParser
import json
import fiona
from shapely.geometry import Point
from fiona.crs import from_epsg
from collections import OrderedDict



import pandas as pd




def readCSV(filename):
    col_list = ['timeindex', 'East (m)', 'North (m)']
    df = pd.read_csv(filename, delimiter = ';', usecols = col_list)
    return df


def generatePoints(filename):

    ds = readCSV(filename)
    print(ds)

    # Output settings
    output_driver = "GeoJSON"
    output_crs = from_epsg(32632)
    output_cells_schema = {
            'geometry': 'Point',
            'properties': OrderedDict([
                ('pid', 'int')
                ])
            }

    # open output cells file
    fn1 = os.path.splitext(filename)[0]+"_POINTS"
    fe1 = '.geojson'
    fileout1 = fn1+fe1
    print("***** Output file: %s *****" % fileout1)
    c1file = fiona.open(
                    fileout1,
                    'w',
                    driver=output_driver,
                    crs=output_crs,
                    schema=output_cells_schema)


    for i in range(0, len(ds)):

        if (int(ds['timeindex'][i]) % 5 == 0):


            # save the resulting record
            recordc1 =  {
              'geometry': {
                  'type': 'Point',
                  'coordinates': [ds['East (m)'][i], ds['North (m)'][i]]
                  },
              'properties': OrderedDict([
                  ("pid", int(ds['timeindex'][i]))
                  ])
              }
            c1file.write(recordc1)
    c1file.close()






def initialize():

   generatePoints('./results/demo/mainroad_95.csv')
   generatePoints('./results/demo/highway_95.csv')
   generatePoints('./results/demo/roadback_95.csv')
   generatePoints('./results/demo/train_95.csv')

#start here
initialize()
