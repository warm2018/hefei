 
#!/usr/bin/python
#-*- coding: UTF-8 -*-

# this fie is used to calculate the output value  suach as Delay,quene length
import re   
from matplotlib import pyplot as plt

Sum_waittime = 0
Sum_waitcount = 0
Sum_stoptime = 0
Sum_timeloss = 0
temp = 0

Sum_CO = 0
Sum_CO2 = 0
Sum_fuel = 0

Number_delay= 0
Number_emission = 0

def stat_result():
    with open ("tripinfo22.xml","r") as routes:
        for line in routes:
            if line != ' ' and len(line) > 100:
                temp = temp + 1
                if temp > 100:
                    infor = line.split(' ')
                    if infor[4] == "<tripinfo":
                        depart = float(infor[6].split('"')[1])
                        if depart > 600 :
                            begin = True
                        else:
                            begin = False
                        if begin :    
                            Wait_time = float(infor[17].split('"')[1])
                            Wait_count = float(infor[18].split('"')[1])
                            Stop_time =  float(infor[19].split('"')[1])
                            Time_loss =  float(infor[20].split('"')[1])
                            Sum_waittime = Sum_waittime + Wait_time
                            Sum_waitcount = Sum_waitcount + Wait_count
                            Sum_stoptime = Sum_stoptime + Stop_time
                            Sum_timeloss = Sum_timeloss + Time_loss
                            Number_delay = Number_delay + 1

                    if infor[8] == "<emissions" and begin:
                        CO = float(infor[9].split('"')[1])
                        CO2 = float(infor[10].split('"')[1])
                        fuel = float(infor[14].split('"')[1])
                        Sum_CO = Sum_CO + CO
                        Sum_CO2 = Sum_CO2 + CO2
                        Sum_fuel = Sum_fuel + fuel
                        Number_emission = Number_emission + 1


    Avar_waittime = float(Sum_waittime / Number_delay)
    Avar_waitcount = float(Sum_waitcount / Number_delay)
    Avar_stoptime = float(Sum_stoptime / Number_delay)
    Avar_timeloss = float(Sum_timeloss / Number_delay)

    Avar_CO = float(Sum_CO / Number_emission)
    Avar_CO2 = float(Sum_CO2 / Number_emission)
    Avar_fuel = float(Sum_fuel / Number_emission)


    print("The total number of car is %d \n" % (Number_delay))
    print("**************************trip statistic******************************")
    print("AVARAGE-waitTIME %.2f s\n AVARAGE_waitCOUNT: %0.3f time \n trip_delay: %.2f s\n" % (Avar_waittime,Avar_waitcount,Avar_timeloss))

    print("The total number of car is %d \n" % (Number_emission))
    print("**************************emissions statistic******************************")
    print("AVARAGE-CO %.2f g\n AVARAGE_CO2:%0.2f g \n fuel:%.2f g\n" % (Avar_CO,Avar_CO2,Avar_fuel))



def stat_result2(xml_file):
    Sum_waittime = 0
    Sum_waitcount = 0
    Sum_stoptime = 0
    Sum_timeloss = 0
    temp = 0

    Sum_CO = 0
    Sum_CO2 = 0
    Sum_fuel = 0
    timeloss_total = [ [] for i in range(int(3800/150) + 1)]
    Number_delay= 0
    Number_emission = 0
    with open (xml_file,"r") as routes:
        last_int  = -1; count = 0;
        currrent_int = -1
        for line in routes:
            if line != ' ' and len(line) > 100:
                temp = temp + 1
                if temp > 100:
                    infor = line.split(' ')
                    if infor[4] == "<tripinfo":
                        arrival = float(infor[11].split('"')[1])
                        Time_loss =  float(infor[20].split('"')[1])
                        currrent_int = int(arrival / 150) 
                        timeloss_total[currrent_int].append(Time_loss)

    average = []
    for i in range(len(timeloss_total)):
        value = sum(timeloss_total[i]) / len(timeloss_total[i])
        average.append(value)

    total_average = sum(average) / len(average)

    return average,total_average

    

def stat_result2(xml_file):
    Sum_waittime = 0
    Sum_waitcount = 0
    Sum_stoptime = 0
    Sum_timeloss = 0
    temp = 0

    Sum_CO = 0
    Sum_CO2 = 0
    Sum_fuel = 0
    timeloss_total = [ [] for i in range(int(3800/150) + 1)]
    Number_delay= 0
    Number_emission = 0
    with open (xml_file,"r") as routes:
        last_int  = -1; count = 0;
        currrent_int = -1
        for line in routes:
            if line != ' ' and len(line) > 100:
                temp = temp + 1
                if temp > 100:
                    infor = line.split(' ')
                    if infor[4] == "<tripinfo":
                        arrival = float(infor[11].split('"')[1])
                        Time_loss =  float(infor[20].split('"')[1])
                        currrent_int = int(arrival / 150) 
                        timeloss_total[currrent_int].append(Time_loss)

    average = []
    for i in range(len(timeloss_total)):
        value = sum(timeloss_total[i]) / len(timeloss_total[i])
        average.append(value)

    total_average = sum(average) / len(average)

    return average,total_average




if __name__ == '__main__':
    averageB,total_averageB  = stat_result2("tripinfo88.xml")

    average1,total_average1  = stat_result2("tripinfo77.xml")


    #average3 = stat_result2("tripinfo22.xml")
    #average33 =  stat_result2("tripinfo33.xml")
    #print(average1,averageB)

    ln1,= plt.plot(range(len(average1)),average1,c='r')

    ln2, = plt.plot(range(len(averageB)),averageB,c='g')

    #ln3, = plt.plot(range(len(average3)),average3,c='blue')

    #ln4, = plt.plot(range(len(average33)),average33,c='yellow')
    plt.legend(handles=[ln2, ln1], labels=['Benchmark Delay:%s'%total_averageB, 'Case150 Delay:%s'%total_average1],
    loc='upper left')
    
    plt.show() 


