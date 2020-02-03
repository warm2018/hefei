
import threading
import random
import os
import sys
import csv
import xlrd 
import optparse
import subprocess

from detector_read import loop_read
from sumolib import checkBinary
import traci

if 'SUMO_HOME' in os.environ:
	tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
	sys.path.append(tools)
else:   
	sys.exit("please declare environment variable 'SUMO_HOME'")



def set_light1(step):
	cycle_a =  120
	start_a = [24,59,89,133,23,60,91,0] #60
	duration_a = [30,25,55,35,30,25,36,19]

	start_a = [134,85,20,135,110,105,80,60] #60
	duration_a = [20,20,35,90,20,20,20,20]

	start_a = [80,135,10,105,80,135,20,110] #60
	duration_a = [25,20,65,25,20,30,55,20]

	start_a = [75,135,10,100,75,135,20,110] #60
	duration_a = [30,20,60,30,20,30,50,20]

	start_a = [75,10,35,100,75,10,35,105] #60
	duration_a = [25,20,35,25,20,20,35,20]

	start_a = [21,117,65,41,147,119,85,0] #60
	duration_a = [44,31,52,44,44,31,34,21]

	start_a = [25,105,55,5,35,100,55,5] #60
	duration_a = [30,20,50,30,20,25,45,20]

	start_a =    [85,122,0,48,85,122,0,48] #60
	duration_a = [37,25,48,37,37,25,48,37]

	start_a =    [70,20,40,90,70,20,50,95] #60
	duration_a = [25,20,30,50,20,30,20,45]
	#start_a =    [15,85,45,105,15,75,45,105] #60
	#duration_a = [30,20,40,30,30,30,30,30]

	#start_a = [20,150,87,66,28,142,103,57] #60
	#duration_a = [33,23,58,33,33,23,34,25]	

	#start_a =    [40,0,60,20,40,100,60,20] #60
	#duration_a = [20,20,60,20,20,40,40,20]



	#start_a =    [85,10,40,105,85,65,10,105] #1111
	#duration_a = [20,30,45,25,20,20,55,25]

	start_a =    [25,100,60,0,25,95,60,0] #11222
	duration_a = [35,20,40,25,35,25,35,25]

	start_a =    [50,50,70,10,30,70,90,30] #11222
	duration_a = [20,20,80,20,20,20,40,20]


	step_a = int(step) % cycle_a
	Binary=[0,0,0,0,0,0,0,0];signal_temp = 0;
	for i in range(8):
		if(start_a[i] <= step_a and start_a[i]+duration_a[i] > step_a):## 其实 bstep_temp 就是step 的代替，如何让现在的step成为
			Binary[i]=1
		else:
			Binary[i]=0	
		if start_a[i]+duration_a[i] > cycle_a:
			start = 0
			end = start_a[i]+duration_a[i] - cycle_a
			if start <= step_a and end > step_a:
				Binary[i]=1
	for i in range(8):
		signal_temp = signal_temp+(2**(7-i))*Binary[i]    
	traci.trafficlight.setPhase("a",signal_temp)	

	

def set_light2(step):
	cycle_a = 147
	start_a =    [85,122,0,48,85,122,0,48] #60
	duration_a = [37,25,48,37,37,25,48,37]

	#start_a =    [85,122,0,48,85,122,0,48] #60
	#duration_a = [37,25,48,37,37,25,48,37]
	#start_a = [20,150,87,66,28,142,103,57] #60
	#duration_a = [33,23,58,33,33,23,34,25]	
	step_a = int(step) % cycle_a
	Binary=[0,0,0,0,0,0,0,0];signal_temp = 0;
	for i in range(8):
		if(start_a[i] <= step_a and start_a[i]+duration_a[i] > step_a):## 其实 bstep_temp 就是step 的代替，如何让现在的step成为
			Binary[i]=1
		else:
			Binary[i]=0	
		if start_a[i]+duration_a[i] > cycle_a:
			start = 0
			end = start_a[i]+duration_a[i] - cycle_a
			if start <= step_a and end > step_a:
				Binary[i]=1
	for i in range(8):
		signal_temp = signal_temp+(2**(7-i))*Binary[i]    
	traci.trafficlight.setPhase("a",signal_temp)	


def set_light3(step):
	cycle_a =  150

	start_a = [35,7,99,68,43,114,0,60] #60
	duration_a = [20,31,53,41,20,31,30,34]

	step_a = int(step) % cycle_a
	Binary=[0,0,0,0,0,0,0,0];signal_temp = 0;
	for i in range(8):
		if(start_a[i] <= step_a and start_a[i]+duration_a[i] > step_a):## 其实 bstep_temp 就是step 的代替，如何让现在的step成为
			Binary[i]=1
		else:
			Binary[i]=0
	for i in range(8):
		signal_temp = signal_temp+(2**(7-i))*Binary[i]    
	traci.trafficlight.setPhase("a",signal_temp)	


def get_options():
	optParser = optparse.OptionParser()
	optParser.add_option("--nogui", action="store_true",
	 default=False, help="run the commandline version of sumo")
	options, args = optParser.parse_args()
	return options
	# this is the main entry point of this script



def run_0():# benchmark, the real traffic light control
	options = get_options()
	# this script has been called from the command line. It will start sumo as a
	# server, then connect and run
	
	if options.nogui:
		sumoBinary = checkBinary('sumo')
	else:
		sumoBinary = checkBinary('sumo-gui')
	traci.start([sumoBinary, '-c', '../cfg1/intersection.sumocfg',
									'--step-length','0.1',
									"--tripinfo-output", "../result/tripinfo0.xml",
									"--device.emissions.probability", "1.0",])

	step = 0
	while step < 3800:
		intstep = int(step*10)
		traci.simulationStep()
		if intstep % 10 == 0:
			pass
		step += 0.1

	traci.close()


def run_1():
	options = get_options()
	# this script has been called from the command line. It will start sumo as a
	# server, then connect and run
	
	if options.nogui:
		sumoBinary = checkBinary('sumo')
	else:
		sumoBinary = checkBinary('sumo-gui')
	traci.start([sumoBinary, '-c', '../cfg5/intersection.sumocfg',
									'--step-length','0.1',
									"--tripinfo-output", "../result/tripinfo11.xml",
									"--device.emissions.probability", "1.0",])
	step = 0
	while step < 3800:
		intstep = int(step*10)
		traci.simulationStep()
		if intstep % 10 == 0:
			set_light1(step)
		step += 0.1

	traci.close()


def run_2():
	options = get_options()
	# this script has been called from the command line. It will start sumo as a
	# server, then connect and run
	
	if options.nogui:
		sumoBinary = checkBinary('sumo')
	else:
		sumoBinary = checkBinary('sumo-gui')
	traci.start([sumoBinary, '-c', '../cfg3/intersection.sumocfg',
									'--step-length','0.1',
									 "--tripinfo-output", "../result/tripinfo33.xml",
									 "--device.emissions.probability", "1.0",])

	step = 0
	while step < 3800:
		intstep = int(step*10)
		traci.simulationStep()
		if intstep % 10 == 0:
			set_light1(step)
		step += 0.1

	traci.close()


def run_bench():
	options = get_options()
	# this script has been called from the command line. It will start sumo as a
	# server, then connect and run
	
	if options.nogui:
		sumoBinary = checkBinary('sumo')
	else:
		sumoBinary = checkBinary('sumo-gui')
	traci.start([sumoBinary, '-c', '../cfg1B/intersection.sumocfg',
									'--step-length','0.1',
									 "--tripinfo-output", "../result/tripinfo88.xml",
									 "--device.emissions.probability", "1.0",])

	step = 0
	while step < 3800:
		intstep = int(step*10)
		traci.simulationStep()
		if intstep % 10 == 0:
			set_light1(step)
		step += 0.1

	traci.close()




def run_7():
	options = get_options()
	# this script has been called from the command line. It will start sumo as a
	# server, then connect and run
	
	if options.nogui:
		sumoBinary = checkBinary('sumo')
	else:
		sumoBinary = checkBinary('sumo-gui')
	traci.start([sumoBinary, '-c', '../cfg7/intersection.sumocfg',
									'--step-length','0.1',
									 "--tripinfo-output", "../result/tripinfo7.xml",
									 "--device.emissions.probability", "1.0",])

	step = 0
	while step < 3800:
		intstep = int(step*10)
		traci.simulationStep()
		if intstep % 10 == 0:
			set_light1(step)
		step += 0.1

	traci.close()

def run_7B():
	options = get_options()
	# this script has been called from the command line. It will start sumo as a
	# server, then connect and run
	
	if options.nogui:
		sumoBinary = checkBinary('sumo')
	else:
		sumoBinary = checkBinary('sumo-gui')
	traci.start([sumoBinary, '-c', '../cfg1B/intersection.sumocfg',
									'--step-length','0.1',
									 "--tripinfo-output", "../result/tripinfo77.xml",
									 "--device.emissions.probability", "1.0",])

	step = 0
	while step < 3800:
		intstep = int(step*10)
		traci.simulationStep()
		if intstep % 10 == 0:
			set_light2(step)
		step += 0.1

	traci.close()

def run_8():
	options = get_options()
	# this script has been called from the command line. It will start sumo as a
	# server, then connect and run
	
	if options.nogui:
		sumoBinary = checkBinary('sumo')
	else:
		sumoBinary = checkBinary('sumo-gui')
	traci.start([sumoBinary, '-c', '../cfg8_S12W22N12E13/intersection.sumocfg',
									'--step-length','0.1',
									 "--tripinfo-output", "../result/tripinfo88.xml",
									 "--device.emissions.probability", "1.0",])

	step = 0
	while step < 3800:
		intstep = int(step*10)
		traci.simulationStep()
		if intstep % 10 == 0:
			set_light1(step)
		step += 0.1

	traci.close()



def run_9():
	options = get_options()
	# this script has been called from the command line. It will start sumo as a
	# server, then connect and run
	
	if options.nogui:
		sumoBinary = checkBinary('sumo')
	else:
		sumoBinary = checkBinary('sumo-gui')
	traci.start([sumoBinary, '-c', '../cfg9_S12W22N12E22/intersection.sumocfg',
									'--step-length','0.1',
									 "--tripinfo-output", "../result/tripinfo103.xml",
									 "--device.emissions.probability", "1.0",])

	step = 0
	while step < 3800:
		intstep = int(step*10)
		traci.simulationStep()
		if intstep % 10 == 0:
			set_light1(step)
		step += 0.1

	traci.close()

def run_8B():
	options = get_options()
	# this script has been called from the command line. It will start sumo as a
	# server, then connect and run
	
	if options.nogui:
		sumoBinary = checkBinary('sumo')
	else:
		sumoBinary = checkBinary('sumo-gui')
	traci.start([sumoBinary, '-c', '../cfg11B/intersection.sumocfg',
									'--step-length','0.1',
									 "--tripinfo-output", "../result/tripinfo11BB.xml",
									 "--device.emissions.probability", "1.0",])

	step = 0
	while step < 3800:
		intstep = int(step*10)
		traci.simulationStep()
		if intstep % 10 == 0:
			set_light1(step)
		step += 0.1

	traci.close()


def run_10():
	options = get_options()
	# this script has been called from the command line. It will start sumo as a
	# server, then connect and run
	
	if options.nogui:
		sumoBinary = checkBinary('sumo')
	else:
		sumoBinary = checkBinary('sumo-gui')
	traci.start([sumoBinary, '-c', '../cfg9_S12W22N12E22/intersection.sumocfg',
									'--step-length','0.1',
									 "--tripinfo-output", "../result/tripinfo10.xml",
									 "--device.emissions.probability", "1.0",])

	step = 0
	while step < 3800:
		intstep = int(step*10)
		traci.simulationStep()
		if intstep % 10 == 0:
			set_light1(step)
		step += 0.1

	traci.close()

def run_11():
	options = get_options()
	# this script has been called from the command line. It will start sumo as a
	# server, then connect and run
	
	if options.nogui:
		sumoBinary = checkBinary('sumo')
	else:
		sumoBinary = checkBinary('sumo-gui')
	traci.start([sumoBinary, '-c', '../cfg1B/intersection.sumocfg',
									'--step-length','0.1',
									 "--tripinfo-output", "../result/tripinfo10B.xml",
									 "--device.emissions.probability", "1.0",])

	step = 0
	while step < 3800:
		intstep = int(step*10)
		traci.simulationStep()
		if intstep % 10 == 0:
			set_light2(step)
		step += 0.1

	traci.close()





if __name__ == '__main__':
	run_9()
