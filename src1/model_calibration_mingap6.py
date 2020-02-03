# -*- coding='utf-8' -*-

from matplotlib import pyplot as plt
from datetime import datetime
import collections
import threading
import random
import os
import sys
import csv
 if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:   
    sys.exit("please declare environment variable 'SUMO_HOME'")
    
from sumolib import checkBinary
sumoBinary = checkBinary('sumo-gui')
sumoCmd = [sumoBinary, '-c', 'inter.sumocfg']

import traci
import traci.constants as tc

direvolume = collections.defaultdict(list)with open('direction_volume_foronehour.csv', 'r', encoding='utf-8', newline='') as f:
    for line in f:
        row = line.strip().split(',')
        dire = row[0]
        direvolume[dire].append(int(row[2]))
random.seed(66)

N = 5000
directions = ['nl', 'ns', 'nr', 'el', 'es', 'er', 'sl', 'ss', 'sr', 'wl', 'ws', 'wr']
volume = [75, 158, 86, 153, 1139, 78, 30, 82, 103, 64, 2250, 153]

q


def generate_route(route_settings):
    veh_gen = [1]*12
    with open('intersection.rou.xml', 'w') as routes:
        print("""<routes>""", file=routes)
        print("""    <vType id="1" length="5" minGap="%s" maxSpeed="16.67" carFollowModel="%s" sigma="%s" tau="%s" lcStrategic="%s"\ lcCooperative="%s"/>""" % \
            (route_settings[0], route_settings[1], route_settings[2], route_settings[3], route_settings[4], route_settings[5]), file=routes)
        print("""    <route id="0" edges="2to6 6to0 0to3"/>
    <route id="1" edges="2to6 6to0 0to4"/>
    <route id="2" edges="2to6 6to0 0to1"/>
    <route id="3" edges="3to7 7to0 0to4"/>
    <route id="4" edges="3to7 7to0 0to1"/>
    <route id="5" edges="3to7 7to0 0to2"/>
    <route id="6" edges="4to8 8to0 0to1"/>
    <route id="7" edges="4to8 8to0 0to2"/>
    <route id="8" edges="4to8 8to0 0to3"/>
    <route id="9" edges="1to5 5to0 0to2"/>
    <route id="10" edges="1to5 5to0 0to3"/>
    <route id="11" edges="1to5 5to0 0to4"/>""", file=routes)

        for i in range(N):
            for j in range(len(volume)):
                if random.uniform(0, 1) < volume[j]/3600:
                    print('    <vehicle id="%s_%i" type="1" route="%i" depart="%i" departspeed="%s"/>' % (directions[j], veh_gen[j], j, i, 16.67), file=routes)
                    veh_gen[j] += 1
        print("""</routes>""", file=routes)

diredetectors = {'nl':['6to0_3'], 'ns':['6to0_1', '6to0_2'], 'nr':['6to0_0'], 'el':['7to0_3', '7to0_4'], 'es':['7to0_1', '7to0_2'], 'er':['7to0_0'], 'sl':['8to0_3', '8to0_4'], 'ss':['8to0_1', '8to0_2'], 'sr':['8to0_0'], 'wl':['5to0_3', '5to0_4'], 'ws':['5to0_1', '5to0_2'], 'wr':['5to0_0']}

N_step = 4105


def fitness(route_settings):
    MSE = 0
    generate_route(route_settings)
    detectorvol = collections.defaultdict(list)
    for dire in directions:
        detectorvol[dire].append(None)
        
    traci.start(['sumo', '-c', 'intersection.sumocfg'])
    step = 0
    tempcount_0 = [0]*12
    tempcount_1 = [0]*12
    tempcount_2 = [0]*12
    tempcount_3 = [0]*12
    tempvehid = {'6to0_3':None, '6to0_1':None, '6to0_2':None, '6to0_0':None, '7to0_3':None, '7to0_4':None, '7to0_2':None, '7to0_1':None, '7to0_0':None, '8to0_0':None, '8to0_1':None, '8to0_2':None, '8to0_3':None, '8to0_4':None, '5to0_0':None, '5to0_1':None, '5to0_2':None, '5to0_3':None, '5to0_4':None}
    while step < N_step:
        traci.simulationStep()
        if step > 500 and step <= 1400:
            for i in range(len(directions)):
                dets = diredetectors[directions[i]]
                for det in dets:
                    if traci.inductionloop.getLastStepVehicleIDs(det) != tempvehid[det]:
                        tempcount_0[i] = tempcount_0[i] + traci.inductionloop.getLastStepVehicleNumber(det)
                        tempvehid[det] = traci.inductionloop.getLastStepVehicleIDs(det)
        if step > 1400 and step <= 2300:
            for i in range(len(directions)):
                dets = diredetectors[directions[i]]
                for det in dets:
                    if traci.inductionloop.getLastStepVehicleIDs(det) != tempvehid[det]:
                        tempcount_1[i] = tempcount_1[i] + traci.inductionloop.getLastStepVehicleNumber(det)
                        tempvehid[det] = traci.inductionloop.getLastStepVehicleIDs(det)
        if step > 2300 and step <= 3200:
            for i in range(len(directions)):
                dets = diredetectors[directions[i]]
                for det in dets:
                    if traci.inductionloop.getLastStepVehicleIDs(det) != tempvehid[det]:
                        tempcount_2[i] = tempcount_2[i] + traci.inductionloop.getLastStepVehicleNumber(det)
                        tempvehid[det] = traci.inductionloop.getLastStepVehicleIDs(det)
        if step > 3200 and step <= 4100:
            for i in range(len(directions)):
                dets = diredetectors[directions[i]]
                for det in dets:
                    if traci.inductionloop.getLastStepVehicleIDs(det) != tempvehid[det]:
                        tempcount_3[i] = tempcount_3[i] + traci.inductionloop.getLastStepVehicleNumber(det)
                        tempvehid[det] = traci.inductionloop.getLastStepVehicleIDs(det)
                    
        step += 1
    traci.close()
    for tpc in [tempcount_0, tempcount_1, tempcount_2, tempcount_3]:
        for i in range(len(directions)):
            detectorvol[directions[i]].append(tpc[i])
    for k in direvolume.keys():
        for j in range(4):
            MSE = MSE + (direvolume[k][j]-detectorvol[k][j+1])**2
    return MSE/48
'''
route_setting_test = [5, 'Krauss', 0.5, 1.2, 0.5, 0.5]
test_mse = fitness(route_setting_test)
print('\n')
print(test_mse)
'''
errors = []
minGap = list(range(2, 7))
carFollowModel = ['Krauss', 'PWagner2009', 'IDM', 'CACC']
sigma = [0.2, 0.4, 0.6, 0.8, 1.0]
tau = [0.8, 0.9, 1.0, 1.1, 1.2]
lcStrategic = [0.2, 0.4, 0.6, 0.8, 1.0]
lcCooperative = [0.2, 0.4, 0.6, 0.8, 1.0]
for j in carFollowModel:
    for k in sigma:
        for l in tau:
            for m in lcStrategic:
                for n in lcCooperative:
                    errors.append([fitness([6, j, k, l, m, n]), 6,j,k,l,m,n])

errors.reverse()
with open('errors_mingap6.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    for i in range(len(errors)):
        writer.writerow(errors[i])
    
plot_y_data = []
for i in range(len(errors)):
    plot_y_data.append(errors[i][0])

plot_x_data = list(range(len(errors)))
plt.plot(plot_x_data, plot_y_data)
plt.savefig('errors6.png')
print(errors[0])




    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    



            


