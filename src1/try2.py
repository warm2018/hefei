from datetime import datetime
import collections
import threading
import random
import os
import sys
import csv
import xlrd 
import optparse
import subprocess

from detector_read import loop_read

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


workbook = xlrd.open_workbook(r'speed_NEW2.xlsx')
sheet_names = workbook.sheet_names()
speed_sheet = workbook.sheet_by_name('Sheet1')

real_speed = speed_sheet.col_values(0)[0:12]


def generate_route(route_settings):
	with open('../cfg1/intersection.rou.xml', 'w') as routes:
	   print("""<routes>""", file=routes)
	   print("""<vType id="car" length="4.8" minGap="%s" maxSpeed="20" carFollowModel="%s" sigma="%s" tau="%s"  accel="%s" decel="%s" />""" %(route_settings[0], route_settings[1], route_settings[2], route_settings[3], route_settings[4], route_settings[5]), file=routes)
	   print("""  
	<flow id="S_L" begin="0" end= "3600" probability="0.079" type="car">
		<route edges="a1i a4o"/> 
	</flow>
	<flow id="S_S" begin="0" end= "3600" probability="0.223" type="car">
		<route edges="a1i a3o"/> 
	</flow>
	<flow id="S_R" begin="0" end= "3600" probability="0.1" type="car">
		<route edges="a1i a2o"/> 
	</flow>

	<flow id="E_L" begin="0" end= "3600" probability="0.109" type="car">
		<route edges="a2i a1o"/> 
	</flow>
	<flow id="E_S" begin="0" end= "3600" probability="0.397" type="car">
		<route edges="a2i a4o"/> 
	</flow>
	<flow id="E_R" begin="0" end= "3600" probability="0.1" type="car">
		<route edges="a2i a3o"/> 
	</flow>S

	<flow id="N_L" begin="0" end= "3600" probability="0.079" type="car">
		<route edges="a3i a2o"/> 
	</flow>
	<flow id="N_S" begin="0" end= "3600" probability="0.233" type="car">
		<route edges="a3i a1o"/> 
	</flow>
	<flow id="N_R" begin="0" end= "3600" probability="0.1" type="car">
		<route edges="a3i a4o"/> 
	</flow>

	<flow id="W_L" begin="0" end= "3600" probability="0.055" type="car">
		<route edges="a4i a3o"/> 
	</flow>
	<flow id="W_S" begin="0" end= "3600" probability="0.261" type="car">
		<route edges="a4i a2o"/> 
	</flow>
	<flow id="W_R" begin="0" end= "3600" probability="0.1" type="car">
		<route edges="a4i a1o"/> 
	</flow>""", file=routes)
	   print("""</routes>""", file=routes)

def get_options():
	optParser = optparse.OptionParser()
	optParser.add_option("--nogui", action="store_true",
	 default=True, help="run the commandline version of sumo")
	options, args = optParser.parse_args()
	return options
	# this is the main entry point of this script
	   
def fitness(route_settings):
	generate_route(route_settings)

	options = get_options()
	# this script has been called from the command line. It will start sumo as a
	# server, then connect and run
	
	if options.nogui:
		sumoBinary = checkBinary('sumo')
	else:
		sumoBinary = checkBinary('sumo-gui')
	traci.start([sumoBinary, '-c', '../cfg1/intersection.sumocfg'])

	step = 0
	while step < 3800:
		traci.simulationStep()
		step += 1
	traci.close()
	Speed_results = loop_read()

	MSE = 0
	for sim,real in zip(Speed_results,real_speed):
		MSE += (sim - real)**2
	return MSE / len(Speed_results)

if __name__ == '__main__':
	errors = []
	minGap = list(range(2, 7))
	carFollowModel = ['Krauss','IDM']
	sigma = [0.2, 0.4, 0.6, 0.8, 1.0]
	tau = [0.8, 0.9, 1.0, 1.1, 1.2]
	accel = [2, 2.3, 2.6, 2.9, 3.2]
	decel = [2.5, 3, 3.5, 4, 4.5]
	for i in minGap:
		for j in carFollowModel:
			for k in sigma:
				for l in tau:
					for m in accel:
						for n in decel:
							errors.append([fitness([i, j, k, l, m, n]), i,j,k,l,m,n])
							print(errors)

	errors.reverse()
	print(errors)
		
	plot_y_data = []
	for i in range(len(errors)):
		plot_y_data.append(errors[i][0])

	plot_x_data = list(range(len(errors)))
	plt.plot(plot_x_data, plot_y_data)
	plt.savefig('errors6.png')
	print(errors[0])







