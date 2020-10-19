#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 15:40:42 2020

@author: marcop
"""

import json
from shapely.geometry import Point
import math
from numbers import Number


# Cellulsr Base Station (The Tower)
class Enb():
    def __init__(self, enbid, enbgeom, enb_tx_power, enb_height, enb_gain, enb_noise_figure, clist):
        self.enbid = enbid
        self.enbgeom = enbgeom
        self.enb_tx_power = enb_tx_power
        self.enb_height = enb_height
        self.enb_gain = enb_gain
        self.enb_noise_figure = enb_noise_figure
        self.clist = clist
        
        

class Cell():
    def __init__(self, cid, mcc, mnc, dmax, az1, az2):
        self.cid = cid
        self.mcc = mcc
        self.mnc = mnc
        self.dmax = dmax
        self.az1 = az1
        self.az2 = az2
        
 
    
# returns list of enb objects       
def getAllEnbs():
    enblist = []
    
    confile = "./config/config.json"
    
    # open config file
    with open(confile) as conf:
            cdataset = json.load(conf)
    enbfile = cdataset['enbposition']['enbfile']
    cellsfile = cdataset['cellsposition']['cellsfile']
    
    print('Parse CBS in file: {}'.format(enbfile))
    print('Parse Cells in file: {}'.format(cellsfile))
    # open input files
    with open(enbfile) as enbf:
        enbds = json.load(enbf)
    with open(cellsfile) as cf:
        cellsds = json.load(cf)
    for feature in enbds['features']:
        clist = []
        
        #fenbid = feature['properties']['enbid']
        fenbid = getFilledHex(feature['properties']['enbid'], 5)
        fenbgeom = Point(feature['geometry']['coordinates'])
        
        
        for enb in cellsds['towers']:
            if fenbid == getFilledHex(enb['enbid'], 5):
                #print(fbtsid, bts['btsid'])
                fenb_tx_power = enb['enb_tx_power']
                fenb_height = enb['enb_height']
                fenb_gain = enb['enb_gain']
                fenb_noise_figure = enb['enb_noise_figure']
                
                for cell in enb['cells']:
                    
                    ccellid = getFilledHex(cell['cellid'], 2)
                    cmcc = getFilledHex(cell['mcc'], 3)
                    cmnc = getFilledHex(cell['mnc'], 2)
                    #ccellid = (hex(cell['cellid']))
                    # cmcc = cell['mcc']
                    # cmnc = cell['mnc']
                    cdmax = cell['dmax']
                    caz1 = cell['azimuth1']
                    caz2 = cell['azimuth2']
                
                    c = Cell(ccellid, cmcc, cmnc, cdmax, caz1, caz2)
                    clist.append(c)
        enb1 = Enb(fenbid, fenbgeom, fenb_tx_power, fenb_height, fenb_gain, fenb_noise_figure, clist)
        enblist.append(enb1)
        
    return enblist
    

# def getRSSIFromDistance(rssimax, distance, dmax):
    
#     # max RSSI: at -90 dBm signal lost!!!
#     rssi = 0
#     k = 0
    
#     # k = abs(rssimax) / log10(dmax)
#     # rssi = log10(distance * k)
    
    
#     if (isinstance(distance, Number)):
#         k = rssimax/math.log10(abs(dmax))
#         rssi = math.log10(distance)*k
#     else:
#         rssi = -1
        
#     return rssi
   

def getFilledHex(hexstring, zeroes):   
    return  '0x{}'.format(hexstring[2:].zfill(zeroes))

def getECI(enbnex, cidhex):
    enblz = format(enbnex[2:].zfill(5))
    cidlz = format(cidhex[2:].zfill(2))
    eci = '0x{}{}'.format(enblz,cidlz)
    return eci

def getPLMN(mcchex, mnchex):
    mcclz = format(mcchex[2:].zfill(3))
    mnclz = format(mnchex[2:].zfill(2))
    plmnid = '0x{}{}'.format(mcclz, mnclz)
    return plmnid

def getECGI(plmnidhex, ecihex):
    
    return  '{}{}'.format(plmnidhex, ecihex[2:])
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    










        
    
    
    