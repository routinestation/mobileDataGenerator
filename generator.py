#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 13:21:50 2020

@author: marcop
"""

from route import getAllRoutes
from track import getPointsFromTrack
from ue import getRandomMSIN
from enb import getAllEnbs, getFilledHex, getECI, getPLMN
from signalstrength import getSINR, getRSSIFromDistance, getRSRPFromRSSI, getRSRPFromDistance
import json
from random import randint
from operator import itemgetter
import time
import csv
import math
import os
import logging



def loadConfiguration():

    cfile = "./config/config.json"
    # open config file
    with open(cfile) as cf:
        ds = json.load(cf)

    conf_dict = {}

    conf_dict['hn_mcc'] = getFilledHex(ds['configuration']['home_network_mcc'], 3) # country code
    conf_dict['hn_mnc'] = getFilledHex(ds['configuration']['home_network_mnc'], 2) # network code
    conf_dict['max_rssi'] = ds['configuration']['rssi_max'] # in -dBm
    conf_dict['migration_rssi'] = ds['configuration']['rssi_migration'] # in -dBm
    conf_dict['sample_interval'] = ds['configuration']['sample_interval'] # in seconds
    conf_dict['min_routes_interval'] = ds['configuration']['route_interval'][0] # in seconds
    conf_dict['max_routes_interval'] = ds['configuration']['route_interval'][1] # in seconds
    conf_dict['min_msin'] = ds['configuration']['msin_range'][0]
    conf_dict['max_msin'] = ds['configuration']['msin_range'][1]
    conf_dict['total_ues'] = ds['configuration']['total_ues']
    conf_dict['min_routes_for_ue'] = ds['configuration']['routes_for_ue'][0]
    conf_dict['max_routes_for_ue'] = ds['configuration']['routes_for_ue'][1]

    conf_dict['ue_height'] = ds['configuration']['ue_height'] # in meters
    conf_dict['network_frequency'] = ds['configuration']['network_frequency'] # in GHz
    conf_dict['ue_gain'] = ds['configuration']['ue_gain'] # in -dB
    conf_dict['thermal_noise'] = ds['configuration']['thermal_noise'] # in -dB
    conf_dict['ue_noise_figure'] = ds['configuration']['ue_noise_figure'] # in -dB
    conf_dict['cable_loss'] = ds['configuration']['cable_loss'] # in -dBm
    conf_dict['migration_signal'] = ds['configuration']['migration_signal'] # in -dBm
    conf_dict['min_signal'] = ds['configuration']['min_signal'] # in -dBm

    return conf_dict




def generate(conf):
    logger = logging.getLogger('Generator_Log')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('generator.log')
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)



    testmode = False

    home_plmnid = getPLMN(conf['hn_mcc'], conf['hn_mnc'])
    # print(conf['hn_mcc'])
    # print(conf['hn_mnc'])
    # print(home_plmnid)

    ar = getAllRoutes()
    aenb = getAllEnbs()

    list_gen_msins = getRandomMSIN(conf['min_msin'], conf['max_msin'], conf['total_ues'])

    # testbed active
    if testmode:
        list_gen_msins = getRandomMSIN(1, 2, 1)

    millisec = int(round(time.time() * 1000))
    #filename_sinr = 'results/out_SINR_'+str(millisec)+'.csv'
    #filename_rssi_e = 'results/out_RSSI_E_'+str(millisec)+'.csv'
    filename_rssi = 'results/out_RSSI_'+str(millisec)+'.csv'
    #filename_rsrp = 'results/out_RSRP_'+str(millisec)+'.csv'


    # out_sinr = open(filename_sinr, "w")
    # out_rssi_e = open(filename_rssi_e, "w")
    out_rssi = open(filename_rssi, "w")
    #out_rsrp = open(filename_rsrp, "w")
    # record_sinr = csv.writer(out_sinr, delimiter=';')
    # record_rssi_e = csv.writer(out_rssi_e, delimiter=';')
    record_rssi = csv.writer(out_rssi, delimiter=';')
    #record_rsrp = csv.writer(out_rsrp, delimiter=';')
    # record_sinr.writerow([
    #                     'timeindex',
    #                     'IMSI',
    #                     'route_id',
    #                     'speed (Km/h)',
    #                     'East (m)',
    #                     'North (m)',
    #                     'Master_PLMN',
    #                     'Master_ECI',
    #                     'Master_SINR',
    #                     'Candidate_PLMN',
    #                     'Candidate_ECI',
    #                     'Candidate_SINR',
    #                     ])

    # record_rssi_e.writerow([
    #                     'timeindex',
    #                     'IMSI',
    #                     'route_id',
    #                     'speed (Km/h)',
    #                     'East (m)',
    #                     'North (m)',
    #                     'Master_PLMN',
    #                     'Master_ECI',
    #                     'Master_RSSI_E',
    #                     'Candidate_PLMN',
    #                     'Candidate_ECI',
    #                     'Candidate_RSSI_E',
    #                     ])

    record_rssi.writerow([
                        'timeindex',
                        'IMSI',
                        'route_id',
                        'speed (Km/h)',
                        'East (m)',
                        'North (m)',
                        'Master_PLMN',
                        'Master_ECI',
                        'Master_RSSI',
                        'Candidate_PLMN',
                        'Candidate_ECI',
                        'Candidate_RSSI',
                        'migrate'
                        ])

    #record_rsrp.writerow([
    #                    'timeindex',
    #                    'IMSI',
    #                    'route_id',
    #                    'speed (Km/h)',
    #                    'East (m)',
    #                    'North (m)',
    #                    'Master_PLMN',
    #                    'Master_ECI',
    #                    'Master_RSRP',
    #                    'Candidate_PLMN',
    #                    'Candidate_ECI',
    #                    'Candidate_RSRP',
    #                    ])



    # start  with the generated ues
    for msin in list_gen_msins:

        # calculate IMSI = MCC + MNC + MSIN
        # imsi = int(str(int(home_plmnid, 16))+'{:09d}'.format(msin))
        imsi = 'ue'+(str(int(home_plmnid, 16))+'{:09d}'.format(msin))


        routetimeindex = randint(0, 600)

        # get the # of possible routes
        n_routes = len(ar)
        # set the # of routes to generate for current ue
        n_gen_routes = randint(conf['min_routes_for_ue'], conf['max_routes_for_ue'])

        # testbed active
        if testmode:
            n_gen_routes = randint(1, 1)


        # generate the routes for current ue
        for r in range(n_gen_routes):

            # get a random route
            curr_route = ar[randint(0, n_routes-1)]

            # testbed active
            if testmode:
                curr_route = ar[1]


            #get tracks of route
            for t in curr_route.rtracks:
                tls = t.tls # track low speed
                ths = t.ths # track high speed
                # generate random speed in Km/h from range
                tspeed = randint(tls, ths)

                # testbed active
                if testmode:
                    tspeed = 60


                # get the points at interval of SAMPLE_INTERVAL
                # based on current speed
                plist = getPointsFromTrack(tspeed, conf['sample_interval'], t.tgeomls)

                # check all generated points
                for p in plist:
                    # increase time index of 1 sample
                    routetimeindex += conf['sample_interval']

                    # store covered cells of enb
                    enb_sinr_touples = []
                    enb_rssi_touples = []
                    enb_rssi_e_touples = []
                    enb_rsrp_touples = []

                    for enb in aenb:
                        #logger.debug('********** eNB parse **********')

                        txpwr = enb.enb_tx_power
                        height = enb.enb_height
                        gain = enb.enb_gain
                        #noise = enb.enb_noise_figure

                        x1 = enb.enbgeom.x
                        y1 = enb.enbgeom.y
                        x2 = p.x
                        y2 = p.y
                        # calculate azimuth from enb to point
                        bearing = (math.degrees(math.atan2(x2-x1, y2-y1)) + 360) % 360
                        # check distance from current point to current enb
                        dist = p.distance(enb.enbgeom)

                       # logger.debug('eNB id: {}, Bearing: {}, Distance: {}'.format(enb.enbid, bearing, dist))

                        # use the max distance (dmax) to skip too far away cells
                        clist = enb.clist
                        clist.sort(key = lambda x:  x.dmax, reverse = True)
                        # skip current eNB if max(dmax) < dist: p not covered by any cell of current eNB
                        if dist > clist[0].dmax:
                           continue

                        # get cells of current eNB
                        for c in enb.clist:
                            az1 = c.az1
                            az2 = c.az2
                            bearingcheck = False

                            if az2 < az1:
                                 if ((bearing >= 0 and bearing < az2) or (bearing >= az1 and bearing < 360)):
                                     bearingcheck = True
                            else:
                                if (bearing >= az1 and bearing < az2):
                                    bearingcheck = True


                            if bearingcheck:

                                # check if it is home network
                                cell_plmnid = getPLMN(c.mcc, c.mnc)
                                # if c.mcc == conf['hn_mcc'] and conf['hn_mnc'] == c.mnc:
                                if cell_plmnid == home_plmnid:
                                    netprio = 1000
                                else:
                                    netprio = 1

                                # calculate the ECI of the cell
                                eci = getECI(enb.enbid, c.cid)

                                # get SINR
                                sinr = getSINR(dist,
                                                   bearing,
                                                   az1,
                                                   az2,
                                                   txpwr,
                                                   conf['network_frequency'],
                                                   height,
                                                   conf['ue_height'],
                                                   conf['ue_noise_figure'],
                                                   conf['ue_gain'],
                                                   gain,
                                                   conf['cable_loss'],
                                                   conf['thermal_noise']
                                                   )

                                # logger.debug('cid: {}, az1: {}, az2: {}, SINR: {}'.format(c.cid, az1, az2, sinr))

                                # if (sinr >= conf['min_signal']):
                                #     enb_sinr_touples.append((cell_plmnid, eci, netprio, sinr))

                                # get empitical RSSI
                                rssi = getRSSIFromDistance(conf['max_rssi'], dist, c.dmax)
                                if rssi > conf['max_rssi']:
                                    enb_rssi_touples.append((cell_plmnid, eci, netprio, rssi))

                                #rsrp = getRSRPFromRSSI(rssi_e)
                                rsrp = getRSRPFromDistance(-100, dist, c.dmax)
                                if rsrp >= -101:
                                    enb_rsrp_touples.append((cell_plmnid, eci, netprio, rsrp))
                                    logger.debug('cid: {}, az1: {}, az2: {}, RSRP: {}'.format(c.cid, az1, az2, rsrp))

                                # # get RSSI from SINR
                                # rssi = sinr + conf['thermal_noise']
                                # if rssi >= conf['max_rssi']:
                                #     enb_rssi_touples.append((cell_plmnid, eci, netprio, rssi))




                    # add 2 dummy cells in case of no coverage
                    # enb_sinr_touples.append((-1,-1,-1, 0))
                    # enb_sinr_touples.append((-1,-1,-1, 0))

                    # enb_rssi_e_touples.append((-1,-1,-1,-100))
                    # enb_rssi_e_touples.append((-1,-1,-1, -100))

                    enb_rssi_touples.append(('-1','-1',-1, -100))
                    enb_rssi_touples.append(('-1','-1',-1, -100))

                    enb_rsrp_touples.append(('-1','-1',-1, -110))
                    enb_rsrp_touples.append(('-1','-1',-1, -110))

                    # sort the best signal based on home network priority
                    # bestcells_sinr = sorted(enb_sinr_touples, reverse = True, key=itemgetter(2,3))
                    # bestcells_rssi_e = sorted(enb_rssi_e_touples, reverse = True, key=itemgetter(2,3))
                    bestcells_rssi = sorted(enb_rssi_touples, reverse = True, key=itemgetter(2,3))
                    bestcells_rsrp = sorted(enb_rsrp_touples, reverse = True, key=itemgetter(2,3))
                    # logger.debug('*********************************************************')
                    # logger.debug('bestcell1 {} {}'.format(bestcells_rsrp[0][1], bestcells_rsrp[0][3]))
                    # logger.debug('bestcell2 {} {}'.format(bestcells_rsrp[1][1], bestcells_rsrp[1][3]))
                    # logger.debug('bestcell3 {} {}'.format(bestcells_rsrp[2][1], bestcells_rsrp[2][3]))


                    # skip cells with rsrp < -95
                    mm = True
                    while mm:
                        if bestcells_rsrp[0][3] < -95 and bestcells_rsrp[0][0] != '-1':
                            bestcells_rsrp.pop(0)
                        else:
                            mm = False

                    # skip cells with rssi < -85
                    m2 = True
                    while m2:
                        if bestcells_rssi[0][3] < conf['migration_rssi'] and bestcells_rssi[0][0] != '-1':
                            bestcells_rssi.pop(0)
                        else:
                            m2 = False


                    # set master cell
                    cell1 = bestcells_rsrp[0]
                    cell1_rssi = bestcells_rssi[0]
                    #cell2 = bestcells_rsrp[1]


                    # remove master cell and sort candidate cells
                    bestcells_rsrp.pop(0)
                    bestcells_rsrp2 = sorted(bestcells_rsrp, reverse = True, key=itemgetter(2,3))

                    bestcells_rssi.pop(0)
                    bestcells_rssi2 = sorted(bestcells_rssi, reverse = True, key=itemgetter(2,3))

                    # mm = True
                    # while mm:
                    #     if bestcells_rsrp2[0][3] < -95 and bestcells_rsrp2[0][0] != -1:
                    #         bestcells_rsrp2.pop(0)
                    #     else:
                    #         mm = False

                    # set candidate cell
                    cell2 = bestcells_rsrp2[0]
                    cell2_rssi = bestcells_rssi2[0]


                    # this sets treshold for master cell (cell1) when roaming takes place
                    if(cell1[2] == 1000 and cell2[2] < 1000 and cell1[3] < -94):
                        cell1 = cell2
                        cell2 = bestcells_rsrp2[1]
                        # cell2 = bestcells_rsrp[1]
                        # logger.debug('*****************Cell Dropped******************')
                        # logger.debug('bestcell1 {} {}'.format(bestcells_rsrp[0][1], bestcells_rsrp[0][3]))
                        # logger.debug('bestcell2 {} {}'.format(bestcells_rsrp[1][1], bestcells_rsrp[1][3]))

                    if(cell1_rssi[2] == 1000 and cell2_rssi[2] < 1000 and cell1_rssi[3] < conf['migration_rssi']):
                        cell1_rssi = cell2_rssi
                        cell2_rssi = bestcells_rssi2[1]




                    # record_sinr.writerow([
                    #     routetimeindex,
                    #     imsi,
                    #     curr_route.rid,
                    #     tspeed,
                    #     '{:.4f}'.format(p.x),
                    #     '{:.4f}'.format(p.y),
                    #     bestcells_sinr[0][0],
                    #     bestcells_sinr[0][1],
                    #     #bestcells[0][2],
                    #     '{:.4f}'.format(bestcells_sinr[0][3]),
                    #     bestcells_sinr[1][0],
                    #     bestcells_sinr[1][1],
                    #     #bestcells[1][2],
                    #     '{:.4f}'.format(bestcells_sinr[1][3]),
                    #     ])

                    migrate = []
                    if(curr_route.rid == 'Road Back'):
                        migrate = 0
                    else:
                        migrate = 1


                    record_rssi.writerow([
                        routetimeindex,
                        imsi,
                        curr_route.rid,
                        tspeed,
                        '{:.4f}'.format(p.x),
                        '{:.4f}'.format(p.y),
                        cell1_rssi[0].strip('0x'),
                        cell1_rssi[1].strip('0x'),
                        #bestcells[0][2],
                        '{:.4f}'.format(cell1_rssi[3]),
                        cell2_rssi[0].strip('0x'),
                        cell2_rssi[1].strip('0x'),
                        #bestcells[1][2],
                        '{:.4f}'.format(cell2_rssi[3]),
                        migrate,
                        ])

                    # record_rssi_e.writerow([
                    #     routetimeindex,
                    #     imsi,
                    #     curr_route.rid,
                    #     tspeed,
                    #     '{:.4f}'.format(p.x),
                    #     '{:.4f}'.format(p.y),
                    #     bestcells_rssi[0][0],
                    #     bestcells_rssi[0][1],
                    #     #bestcells[0][2],
                    #     '{:.4f}'.format(bestcells_rssi[0][3]),
                    #     bestcells_rssi[1][0],
                    #     bestcells_rssi[1][1],
                    #     #bestcells[1][2],
                    #     '{:.4f}'.format(bestcells_rssi[1][3]),
                    #     ])

                    #record_rsrp.writerow([
                    #    routetimeindex,
                    #    imsi,
                    #    curr_route.rid,
                    #    tspeed,
                    #    '{:.4f}'.format(p.x),
                    #    '{:.4f}'.format(p.y),
                    #    cell1[0].strip('0x'),
                    #    cell1[1].strip('0x'),
                    #    #bestcells[0][2],
                    #    '{:.4f}'.format(cell1[3]),
                    #    cell2[0].strip('0x'),
                    #    cell2[1].strip('0x'),
                    #    #bestcells[1][2],
                    #    '{:.4f}'.format(cell2[3]),
                    #    ])

            # set random interval before new route
            routetimeindex += randint(conf['min_routes_interval'], conf['max_routes_interval'])

    # out_sinr.close()
    # out_rssi_e.close()
    out_rssi.close()
    #out_rsrp.close()













def main():
    if os.path.exists("generator.log"):
        os.remove("generator.log")
    start_time = time.time()

    generate(loadConfiguration())
    print("--- {} seconds ---".format(time.time() - start_time))


if __name__ == '__main__':
    main()
