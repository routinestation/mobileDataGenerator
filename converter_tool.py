#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 17:04:36 2020

@author: marcop
"""

import os
from configparser import ConfigParser
import json
import utm
import fiona
from shapely.geometry import Point, LineString
from fiona.crs import from_epsg
from collections import OrderedDict
                
def convertENB():
    
    
    # Load the configuration file
    config = ConfigParser()
    config.read('converter.ini')
    
    if config.has_option('enbs', 'file'):
        enbsfile = config['enbs'].get('file')
        enbsfile = enbsfile.strip()
        if(len(enbsfile) == 0): 
            print ("ENBs file not declared") 
        else : 
            print('***** File ENBs: %s *****' % enbsfile)
            # Output settings
            output_driver = "GeoJSON"
            output_crs = from_epsg(32632)
 
            # open input file
            with open(enbsfile) as f:
                dataset = json.load(f)
        
            # open output file
            bn = os.path.basename(enbsfile)
            fn = os.path.splitext(enbsfile)[0]+"_UTM"
            fe = os.path.splitext(enbsfile)[1]
            fn = fn+fe
            fileout = os.path.join(bn, '/geojson/', fn )
            print("***** Output file: %s *****" % fileout)
    
            output_enbs_schema = {
                    'geometry': 'Point',
                    'properties': OrderedDict([
                        ('enbid', 'str')
                        ])
                    }
        
            with fiona.open(
                    fileout,
                    'w',
                    driver=output_driver,
                    crs=output_crs,
                    schema=output_enbs_schema) as c:
            
                # Parse the features    
                for feature in dataset['features']:
                    fenbid = feature['properties']['enbid']
                    fgeomenb = Point(feature['geometry']['coordinates'])
                    
                    print(utm.from_latlon(fgeomenb.y,fgeomenb.x))
                    temp = utm.from_latlon(fgeomenb.y,fgeomenb.x)
                
                    
                    # save the resulting record
                    record =  {
                      'geometry': {
                          'type': 'Point',
                          'coordinates': temp[:2]
                          },
                      'properties': OrderedDict([
                          ("enbid", fenbid)
                          ])
                      }
                    c.write(record)

    else:
        print ("ENBs conversion aborted") 
        

def convertTracks():
    
    # Load the configuration file
    config = ConfigParser()
    config.read('converter.ini')
    
    if config.has_section('trackfiles'):
        # res = config['segment'].get('files')
        # files = res.strip('][').split(',')
        for key, value in config['trackfiles'].items():
            #file = config['trackfiles'].get(key)
            file = value.strip()
            if(len(file) == 0): 
                print ("Tracks file %s not declared" % key) 
            else : 
                print('\n***** Tracks file: %s *****' % file)
                
                # Output settings
                output_driver = "GeoJSON"
                output_crs = from_epsg(32632)
             
                # open input file
                with open(file) as f:
                    dataset = json.load(f)
                    
                # open output file
                bn = os.path.basename(file)
                fn = os.path.splitext(file)[0]+"_UTM"
                fe = os.path.splitext(file)[1]
                fn = fn+fe
                fileout = os.path.join(bn, '/geojson/', fn )
                print("***** Output file: %s *****" % fileout)
                        
                output_schema = {
                    'geometry': 'LineString',
                    'properties': OrderedDict([
                        ('name', 'str'),
                        ('category', 'int'),
                        ('lspeed', 'int'),
                        ('hspeed', 'int')
                        ])
                    }
                
                with fiona.open(
                        fileout,
                        'w',
                        driver=output_driver,
                        crs=output_crs,
                        schema=output_schema) as c:
                    
                    for feature in dataset['features']:
                        crdlist = []
                        
                        
                        fname = feature['properties']['name']
                        fcat = feature['properties']['category']
                        fls = feature['properties']['lspeed']
                        fhs = feature['properties']['hspeed']
                        
                        print ("***** Processed Track: %s *****" % fname)
                        
                        fgeom = LineString(feature['geometry']['coordinates'])
                        
                        
                        # convert coordinates from Geographic to UTM
                        for i in range(0, len(fgeom.coords)):
                            
                            print(utm.from_latlon((fgeom.coords[i])[1],(fgeom.coords[i])[0]))
                            temp = utm.from_latlon((fgeom.coords[i])[1],(fgeom.coords[i])[0])
                            crdlist.append(temp[:2])
                            
                        print("# of tuples converted: %d\n" % len(crdlist))
                        
                        # save the resulting record
                        record =  {
                            'geometry': {
                                'type': 'LineString',
                                'coordinates': crdlist
                                },
                            'properties': OrderedDict([
                                ('name', fname),
                                ('category', fcat),
                                ('lspeed', fls),
                                ('hspeed', fhs),
                                ])
                            }
                        c.write(record)
                 
                
    else:
        print ("Tracks conversion aborted") 
    
    
    
    




def initialize():
    
   convertENB()
   convertTracks()    
 
#start here
initialize()
    


