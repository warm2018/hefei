import math
import pandas as pd
import xlsxwriter

#2016-10-11 06:30:00
def calculate(dataframe):
	grouped = dataframe.groupby("VEHICLE_CLASS")
	grouped_dict = dict(list(grouped))
	print(grouped_dict)
	total_number3=0;total_number4=0
	try:
		class_3 = grouped_dict[3]
		class_4 = grouped_dict[4]
		number_list3 = list(class_3["VOLUME"])
		number_list4 = list(class_4["VOLUME"])
		total_number3 = sum(number_list3)
		total_number4 = sum(number_list4)
	except:
		pass
	return total_number3,total_number4


def stat_volume():
	df1=pd.read_excel('../data/weibo.xlsx',sheet_name='weibo')
	workbook = xlsxwriter.Workbook('flow_new.xlsx')
	worksheet1 = workbook.add_worksheet(name='flow')
	
	interval = 10
	row = 0
	for Day in [11,12,13,14,15]:
		for begin in range(30,210,interval):
			start_hour = int(begin / 60)
			start_minute = begin  % 60
			start = "2016-10-%d 0%d:%d:00"%(Day,start_hour + 6,start_minute)

			finish_hour = int((begin + interval)  / 60)
			finish_minute = (begin + interval) % 60
			finish = "2016-10-%d 0%d:%d:00"%(Day,finish_hour + 6,finish_minute)
			row += 1; col = 0
			print(start,finish)
			for detector in [7,8,9]:
				#worksheet1.write(0,col,"%d_%d"%(detector,detect))
				for lane in [0,1,2,3]:
					select_df1 = df1.loc[(df1["DETECT_ID"] == detector) & (df1["LANE"] == lane) & (df1["COLLEC_TIME"] >= start ) \
					& (df1["COLLEC_TIME"] < finish ) & (df1["VOLUME"] != 0)]
					number3,number4 = calculate(select_df1)
					print(number3,number4)
					worksheet1.write(row,col,number3)
					worksheet1.write(row,col+1,number4)
					col += 2
				col += 1
		row += 1		
	workbook.close()


def speed_distri():
	df1=pd.read_excel('../data/weibo.xlsx',sheet_name='weibo')
	workbook = xlsxwriter.Workbook('speed_new.xlsx')
	worksheet1 = workbook.add_worksheet(name='flow')
	
	interval = 5
	row = 0
	for begin in range(30,90,interval):
		start_hour = int(begin / 60)
		start_minute = begin  % 60
		start = "2016-10-%d 0%d:%d:00"%(11,start_hour + 7,start_minute)

		finish_hour = int((begin + interval)  / 60)
		finish_minute = (begin + interval) % 60
		finish = "2016-10-%d 0%d:%d:00"%(11,finish_hour + 7,finish_minute)
		print(start,finish)
		#worksheet1.write(0,col,"%d_%d"%(detector,detect))
		select_df1 = df1.loc[(df1["DETECT_ID"] == 8) & (df1["COLLEC_TIME"] >= start ) \
		& (df1["COLLEC_TIME"] < finish ) & (df1["VOLUME"] != 0)]
		describe_data = select_df1.describe()
		speed = describe_data.at['mean', 'SPEED']
		worksheet1.write(row,1,speed)
		row += 1		
	workbook.close()

def test():
	df1=pd.read_excel('../data/weibo.xlsx',sheet_name='weibo')
	start = "2016-10-11 07:30:00"
	finish = "2016-10-11 08:30:00"
	select_df1 = df1.loc[(df1["DETECT_ID"] == 8)  & (df1["COLLEC_TIME"] >= start ) \
	& (df1["COLLEC_TIME"] < finish ) & (df1["VOLUME"] != 0)]
	select_df2 = select_df1["SPEED"]
	print(select_df2.describe())

if __name__ == '__main__':
	speed_distri()

