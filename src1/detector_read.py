import math
import pandas as pd
import xlsxwriter
import re   
from matplotlib import pyplot as plt
##workbook = xlsxwriter.Workbook('speed_2.xlsx')
##worksheet1 = workbook.add_worksheet(name='flow')

def loop_read():
	with open ("../cfg3/LoopOutput.xml","r") as routes:
		speed_aggrate = []
		speed_results = []
		last_row = 0
		for line in routes:
			infor = line.split(' ')
			if len(infor) >= 5 and infor[4] == '<interval':
				## and infor[7] == ID
				## select the specific DIRECTOR in every direction
				print(infor)
				begin = float(infor[5].split('"')[1])
				speed = float(infor[11].split('"')[1])
				row = int(begin / 300)
				if row != last_row:
					if len(speed_aggrate) != 0:
						average_speed = sum(speed_aggrate) / len(speed_aggrate)
						speed_results.append(average_speed)
						speed_aggrate = []
				elif speed > -0.1:
					speed_aggrate.append(speed*3.6)
				last_row = row
	print(speed_results)
	return speed_results		
	

def vehicle_count(xml_file):
	#"../cfg2/LoopOutput.xml"
	workbook = xlsxwriter.Workbook('../result/number2.xlsx') 
	worksheet = workbook.add_worksheet('test1')
	with open (xml_file,"r") as routes:
		col = 0; last_row = 1
		vehicle_total = [ [] for i in range(int(3800/150) + 1)]
		for line in routes:
			infor = line.split(' ')
			if len(infor) >= 5 and infor[4] == '<interval':
				## and infor[7] == ID
				## select the specific DIRECTOR in every direction
				detectorID = infor[7].split('"')[1]
				begin = float(infor[5].split('"')[1])
				vehicle_number = float(infor[8].split('"')[1])
				row = int(begin / 150)
				col += 1 
				vehicle_total[row].append(vehicle_number)
				if row != last_row:
					col = 0
				last_row =row
				worksheet.write(row,col,vehicle_number)
	workbook.close()

	average = []
	print(vehicle_total)
	for i in range(len(vehicle_total)):
		value = sum(vehicle_total[i])
		average.append(value)

	total_average = sum(average) / len(average)
	print(sum(average))

	return average,total_average

if __name__ == '__main__':
    average0,total_average0  = vehicle_count("../cfg1B/LoopOutput.xml")

    average1,total_average1  = vehicle_count("../cfg8_S12W22N12E13/LoopOutput.xml")

    average2,total_average2  = vehicle_count("../cfg9_S12W22N12E22/LoopOutput.xml")
    #average3 = vehicle_count("tripinfo22.xml")
    #average33 =  vehicle_count("tripinfo33.xml")

    #print(average1,averageB)
    ln0,= plt.plot(range(len(average0)),average0,c='blue')

    ln1,= plt.plot(range(len(average1)),average1,c='r')

    ln2, = plt.plot(range(len(average2)),average2,c='g')

    #ln3, = plt.plot(range(len(average3)),average3,c='blue')

    #ln4, = plt.plot(range(len(average33)),average33,c='yellow')
    plt.legend(handles=[ln0,ln1,ln2], labels=['Benchmark Capacity','Case120-1 Capacity:','Case120-2 Capacity'],
    loc='center left')
    
    plt.show() 



