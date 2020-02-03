
 
import numpy as np
import pandas as pd 
import xlrd
import xlsxwriter
import matplotlib.pyplot as plt
import copy

def combine_excel():
	df1=pd.read_excel('data2_new.xlsx',sheet_name='detector_data')
	df2=pd.read_excel('data2_new.xlsx',sheet_name='signal_data')

	workbook = xlrd.open_workbook(r'data2.xlsx')
	sheet_names = workbook.sheet_names()
	relationship = workbook.sheet_by_name('relationship')

	detector_ID = relationship.col_values(3)[1:]
	signal_phases = relationship.col_values(4)[1:]
	detector_position = relationship.col_values(5)[1:]

	groups1 = df1.groupby("DetectorID")

	detector_infor = {}
	for i,detector in enumerate(detector_ID):
		detector_infor[int(detector)] = [int(signal_phases[i]),detector_position[i]]
	print(detector_infor)
	detector_infor[42] = [-1,-1]
	phase_sery = [detector_infor[ID][0] for ID in df1['DetectorID']]
	position_sery = [detector_infor[ID][1] for ID in df1['DetectorID']]

	df1['Phase'] = phase_sery
	df1['Position'] = position_sery

	'''
	group3 = df1.groupby("Phase")
	for group in group3:
		## group structure: (label,datafrme)
		for detect_ID,detect_data in group:
			print(type(i))
	'''

	df2
	groups2 = df2.groupby("PhaseID")
	for group in groups2:
		pass

	groups2_dict = dict(list(groups2))
	print(groups2_dict)
	Phase_color = []

	## find the 
	for phase,timestamp in zip(df1["Phase"],df1["TimeStamp"]):
		if phase != -1:
			phase_dataframe = groups2_dict[phase]
			for start,duration,state in zip(phase_dataframe["TimeStamp"],phase_dataframe["TimeDuration"],\
				phase_dataframe["Status"]):
				findif = False
				if timestamp > start and timestamp < start + duration:
					Phase_color.append(state)
					findif = True
					break
			if findif:
				continue
			else:
				Phase_color.append("R")
		else:
			Phase_color.append("-1")

	df1['State'] = Phase_color

	df1.to_excel('combine.xlsx')
	

def stat_volume():
	df1 = pd.read_excel('combine.xlsx',sheet_name='Sheet1')

	detector = [[14],[24,23,19],[20],[17,16,18],[6],[32,31,30],[5],[27,26,25]]
	workbook = xlsxwriter.Workbook('flow_new.xlsx')
	worksheet1 = workbook.add_worksheet(name='flow')

	for row in range(1,25):
		start = (row-1) * 1800 
		end = (row)* 1800
		col = 1
		for i,movement in enumerate(detector):
			for detect in movement:
				worksheet1.write(0,col,"%d_%d"%(phase[i],detect))
				select_df1 = df1.loc[(df1["TimeStamp"] > start) & (df1["TimeStamp"]< end) & \
				(df1["DetectorID"] == detect)]
				worksheet1.write(row,col,select_df1.shape[0])
				col += 1
	workbook.close()

def lane_headway(select_peak,detectorID):
	select_df1 = select_peak.loc[(df1["DetectorID"] == detectorID )]
	print(select_df1)
	G_list = []
	G_vehicles = []

	NUMBERCAR = 4
	count = 1
	for i,state in enumerate(select_df1["State"]):
		if state=="G":
			G_vehicles.append(i)
			count = 0
		elif count == 0:
			count = 1
			G_list.append(G_vehicles)
			G_vehicles = []
	G_time = []
	for platoon in G_list:
		platoon_time = []	
		for i,vehicle in enumerate(platoon[:NUMBERCAR]):
			if i != 0:
				pre_vehicle = platoon[i-1]
				time_headway = list(select_df1["TimeStamp"])[vehicle] - list(select_df1["TimeStamp"])[pre_vehicle]
				if time_headway < 4:
					platoon_time.append(time_headway)
		G_time.append(platoon_time)	


	platoon_list = [[] for i in range(NUMBERCAR-1)]
	for platoon in G_time:
		for i,vehicle in enumerate(platoon):
			platoon_list[i].append(vehicle)

	x_coor = copy.deepcopy(platoon_list)
	for i,position_time in enumerate(platoon_list):
		for j,l in enumerate(position_time):
			x_coor[i][j] = i

	for position_x,position_y in zip(x_coor,platoon_list):
		plt.scatter(position_x, position_y,s=8)

	mean_time = []
	for position_x,position_y in zip(x_coor,platoon_list):
		mean = sum(position_y) / len(position_x)
		mean_time.append(mean)

	plt.plot(range(NUMBERCAR-1),mean_time,lw=3)
	plt.xlabel("Position")
	plt.ylabel("Time Headway")	
	plt.show() 

	return mean


if __name__ == '__main__':
	df1 = pd.read_excel('combine.xlsx',sheet_name='Sheet1')
	start = 7*3600
	end = 9*3600
	select_peak = df1.loc[(df1["TimeStamp"] > start) & (df1["TimeStamp"]< end)] 
	mean = lane_headway(select_peak,2)























	











