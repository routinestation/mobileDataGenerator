#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 16:57:33 2020

@author: marcop
"""

import math
import scipy.constants
from numbers import Number

import logging
logger = logging.getLogger('Generator_Log')

# eNBHeight = 25.0
# uEHeight = 2.0
# carrierFrequency = 2.0
# antennaGainUE = 0.0
# antennaGainENB = 18.0
# thermalNoise = -104.5 # for 10MHz bandwidth
# noiseFigureUE = 7.0
# noiseFigureENB = 5
# cableLoss = 2.0


# txPower = 8


def getRSSIFromDistance(rssimax, distance, dmax):
    
    # max RSSI: at -90 dBm signal lost!!!
    rssi = 0
    k = 0
    
    # k = abs(rssimax) / log10(dmax)
    # rssi = log10(distance * k)
    
    
    if (isinstance(distance, Number)):
        k = rssimax/math.log10(abs(dmax))
        rssi = math.log10(distance)*k
    else:
        rssi = -1000
        
    return rssi

def getRSRPFromRSSI(rssi):
    rsrp = 0
    rb = 100 # assume full load on 20 MHz band
    rsrp += rssi - 10 * math.log10(12 * 6)
    rsrp += rssi - 10 * math.log10(12 * 15)
    rsrp += rssi - 10 * math.log10(12 * 25)
    rsrp += rssi - 10 * math.log10(12 * 50)
    rsrp += rssi - 10 * math.log10(12 * 75)
    rsrp += rssi - 10 * math.log10(12 * rb)
    rsrp /= 6
    return rsrp

def getRSSIFromRSRP(rsrp):
    rssi = 0
    rb = 100 # assume full load on 20 MHz band
    rssi += rsrp + 10 * math.log10(12 * 6)
    rssi += rsrp + 10 * math.log10(12 * 15)
    rssi += rsrp + 10 * math.log10(12 * 25)
    rssi += rsrp + 10 * math.log10(12 * 50)
    rssi += rsrp + 10 * math.log10(12 * 75)
    rssi += rsrp + 10 * math.log10(12 * rb)
    rssi /= 6
    return rsrp


def getRSRPFromDistance(rsrpmax, distance, dmax):
    # max RSRP: at -100 dBm signal lost!!!
    rsrp = 0
    k = 0
    
    # k = abs(rsrpmax) / log10(dmax)
    # rsrp = log10(distance * k)
    
    
    if (isinstance(distance, Number)):
        k = rsrpmax/math.log10(abs(dmax))
        rsrp = math.log10(distance)*k
    else:
        rsrp = -120
        
    return rsrp



def linearToDBm(linear):
    return 10 * math.log10(1000 * linear)

def linearToDB(linear):
    return 10 * math.log10(linear)

def dBmToLinear(db):
    return pow(10, (db - 30) / 10)

def dBToLinear(db):
    return pow(10, (db) / 10)



def angleAtt(bearing, az1, az2):
    
    if az2 < az1:
        t = az2
        az2 = az1
        az1 = t
    
    eNBAngle = (az2 + az1) / 2
    angle = abs(eNBAngle - bearing)   
    #print('eNB Angle:  {} az1: {}, az2: {}'.format(eNBAngle,az1,az2 ))

    minAngAtt = 25 # max value in dB
    
    angAtt = 12 * pow(angle / 70.0, 2)
    if(angAtt > minAngAtt):
        angAtt = minAngAtt
        
    #print('Angle att.:  {}'.format(angAtt))
    return angAtt

def getAttenuation(d, enbheight, ueheight, frequency): # defined dor LOS and urban cells d<2000
    if (d < 10):
        d = 10
    
    dbp = 4 * (enbheight -1) * (ueheight - 1) * (frequency * 1000000000 / scipy.constants.speed_of_light)
    
    
    #LOS situation
    if (d < dbp):
        return 22 * math.log10(d) + 28 + 20 * math.log10(frequency)
    else:
        return 40 * math.log10(d) + 7.8 - 18 * math.log10(enbheight - 1) - 18 * math.log10(ueheight - 1) + 2 * math.log10(frequency)


def getSINR(distance, bearing, az1, az2, txpower, frequency, enbheight, ueheight, uenoisefigure, uegain, enbgain, cableloss, thermalnoise):
    recvPwr = txpower
    
    attenuation = getAttenuation(distance, enbheight, ueheight, frequency)
    recvPwr -= attenuation
    recvPwr += uegain # (dBm+dB)=dBm
    recvPwr += enbgain # (dBm+dB)=dBm
    recvPwr -= cableloss # (dBm-dB)=dBm
    
    # ******** angular attenuation disabled !!!
    # ******** recvPwr -= angleAtt(bearing, az1, az2)
    
    recvPwr -= 3 # multi user tx power divided
    #print('recpwr: {}'.format(recvPwr))
    
    # suppose no cell interference
    recvPwr = recvPwr - uenoisefigure - thermalnoise
    
    # rssi_test = recvPwr + thermalnoise
    # rsrp_test = getRSRPFromRSSI(rssi_test)
    # print('RSSI {} RSRP {}'.format(rssi_test, rsrp_test))
    # print('Distance: {}, SINR: {}'.format(distance, recvPwr))
    #rsrq = 12/recvPwr - 12
    #print('RSRQ: {}'.format(rsrq))
    
    return recvPwr

    

# def initialize():
#     # for i in range(10, 310, 10):     
#     #     print('Distance: {}'.format(i))
#         #getSINR(i, 330, 270, 30, 8, 2, 25, 1.5, 7, 0, 18, 2, -104.5)
#     rsrp = 0
#     rssi = -60
#     rsrp += rssi - 10 * math.log10(12 * 6)
#     print('RSRP 6: {}'.format(rssi - 10 * math.log10(12 * 6)))
#     rsrp += rssi - 10 * math.log10(12 * 15)
#     print('RSRP 6: {}'.format(rssi - 10 * math.log10(12 * 15)))
#     rsrp += rssi - 10 * math.log10(12 * 25)
#     print('RSRP 6: {}'.format(rssi - 10 * math.log10(12 * 25)))
#     rsrp += rssi - 10 * math.log10(12 * 50)
#     print('RSRP 6: {}'.format(rssi - 10 * math.log10(12 * 50)))
#     rsrp += rssi - 10 * math.log10(12 * 100)
#     print('RSRP 6: {}'.format(rssi - 10 * math.log10(12 * 100)))
#     rsrp /= 5
#     print('RSRP: {}'.format(rsrp))
    
    
        
        

# initialize()
        

    



