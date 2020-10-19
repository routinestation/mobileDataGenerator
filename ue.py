#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 21:59:06 2020

@author: marcop
"""

from random import sample

def getRandomMSIN(msinmin, msinmax, uenumber):
    msins = []
    
    temp = sample(range(msinmin, msinmax), uenumber)
    
    for t in temp:
        
        msins.append(t)
    return msins