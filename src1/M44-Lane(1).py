#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 08:42:03 2019
 
@author: zhaozhang
"""
#这个模型存在的问题是：各方向分配的比例不同了
#Model4-max capacity, lane setting is known in prior
 
from gurobipy import *
import xlrd
import xlwt
import numpy as np
 
try:
 
    # Create a new model
    m = Model("M4")
    P=0.95 ## maximum degree of saturation
    Q=1600# lane capacity
    clearance=0 # clearance time in seconds
    mingreen = 20
    maxgreen = 90
    cmin = 100  #cycle in seconds
    cmax = 150
    Demand = [0,1085,0,1822,0,1085,0,1137]   
    M=100000      
    K=[4,4,5,5,4,4,5,5]
    s={1,3,5,7}
    conflict=[(1,4,3,8),(1,4,5,2),(1,4,7,2),(1,4,3,6),
                              (1,6,7,4),(1,6,3,8),(1,6,7,2),(1,6,5,8),
                              (3,8,1,6),(3,8,1,4),(3,8,7,2),(3,8,5,2),
                              (3,6,7,4),(3,6,5,2),(3,6,5,8),(3,6,1,4),
                              (5,2,1,4),(5,2,3,8),(5,2,3,6),(5,2,7,4),
                              (5,8,1,6),(5,8,3,6),(5,8,7,2),(5,8,7,4),
                              (7,2,1,6),(7,2,1,4),(7,2,3,8),(7,2,5,8),
                              (7,4,1,6),(7,4,3,6),(7,4,5,8),(7,4,5,2)]      
    movement,ratio,gdirect,arm,nlane=multidict({(1,4):[0.26,1,1,1],(1,6):[0.74,2,1,3],(1,8):[0.0,3,1,1],
                                                (3,2):[0.00,3,2,1],(3,6):[0.22,1,2,1],(3,8):[0.78,2,2,3],
                                                (5,4):[0.00,3,3,1],(5,2):[0.74,2,3,3],(5,8):[0.26,1,3,1],
                                                (7,4):[0.73,2,4,3],(7,6):[0.00,3,4,1],(7,2):[0.27,1,4,1]})
# n=1,3,5,7,create i1 in E
    def yy(n):
        y=[2,4,6,8]
        for m in [2,4,6,8]:
            if m-n==1:
                y.remove(m)
        return y
    left=[(1,4),(3,6),(5,8),(7,2)]
    through=[(1,6),(3,8),(5,2),(7,4)]
    right=[(1,8),(3,2),(5,4),(7,6)]
 
    # Create variables
    sta={}
    phi={}
    omg={}
    q={}   
    klane={} # number of lanes for movment
    y={} # lane setting parameters
    y1={}
    y2={}
    y11={}
    y22={}
    y111 = {}
    y222 = {}
    miu = m.addVar(lb=0,vtype=GRB.CONTINUOUS)
    c = m.addVar(lb=1/cmax,ub=1/cmin,vtype=GRB.CONTINUOUS)
    for i,i1 in movement:
        sta[i,i1] = m.addVar(lb=0,ub=1,vtype=GRB.CONTINUOUS, name='sta%s_%s_'%(i,i1))
        phi[i,i1] = m.addVar(lb=0,vtype=GRB.CONTINUOUS, name='phi%s_%s'%(i,i1))     
        q[i,i1] = m.addVar(lb=0,vtype=GRB.CONTINUOUS, name='q%s_%s'%(i,i1))      
        klane[i,i1] = m.addVar(lb=1,vtype=GRB.INTEGER, name='k%s_%s'%(i,i1))  
        y[i,i1] = m.addVar(vtype=GRB.INTEGER, name='y%s_%s'%(i,i1))
         
    for i,i1,i2,i3 in conflict:
            omg[i,i1,i2,i3]= m.addVar(vtype=GRB.BINARY, name='omg%s_%s_%s_%s'%(i,i1,i2,i3))    
#below is the constraints
# 1. order of movement ,       omg[i,i1,i2,i3]=0表示M[i,i1]在M[i2,i3]的前面    
    for i,i1,i2,i3 in conflict:
        m.addConstr(omg[i,i1,i2,i3]+omg[i2,i3,i,i1]==1)
        m.addConstr(sta[i2,i3]+M*omg[i,i1,i2,i3]>=sta[i,i1]+phi[i,i1]+clearance*c)
        m.addConstr(sta[i2,i3]+phi[i2,i3]-1+clearance*c<=sta[i,i1]+M*omg[i,i1,i2,i3])
         
# 2. green timings'
    for i,i1 in movement:
        m.addConstr(phi[i,i1]<=maxgreen*c)
        m.addConstr(phi[i,i1]>=mingreen*c)               
# 3. cycle length
    m.addConstr(c<=1/cmin)
    m.addConstr(c>=1/cmax)
# 4. capacity constrain        
    for i,i1 in movement:

        y11[i,i1] = m.addVar(vtype=GRB.INTEGER,name='y11%s_%s'%(i,i1))
        y22[i,i1] = m.addVar(vtype=GRB.INTEGER,name='y22%s_%s'%(i,i1))
        y111[i,i1] = m.addVar(vtype=GRB.INTEGER,name='y111%s_%s'%(i,i1))
        y222[i,i1] = m.addVar(vtype=GRB.INTEGER,name='y222%s_%s'%(i,i1))

        m.addConstr(miu*Demand[i]*ratio[i,i1]<=q[i,i1]+y[i,i1]*M)
        m.addConstr(miu*Demand[i]*ratio[i,i1]>=q[i,i1]-y[i,i1]*M)
        '''
        m.addConstr(miu*Demand[i]*ratio[i,i1]<=q[i,i1]*2+(1-y[i,i1])*M)
        m.addConstr(miu*Demand[i]*ratio[i,i1]>=q[i,i1]*2-(1-y[i,i1])*M)  
        m.addConstr(miu*Demand[i]*ratio[i,i1]<=q[i,i1]*3+(2-y[i,i1])*M)
        m.addConstr(miu*Demand[i]*ratio[i,i1]>=q[i,i1]*3-(2-y[i,i1])*M)
        '''
        m.addConstr(y11[i,i1] == 1-y[i,i1])
        m.addConstr(y22[i,i1] == 2-y[i,i1])

        m.addConstr(y111[i,i1] == abs_(y11[i,i1]))
        m.addConstr(y222[i,i1] == abs_(y22[i,i1]))        

        m.addConstr(miu*Demand[i]*ratio[i,i1]<=q[i,i1]*2+y111[i,i1]*M)
        m.addConstr(miu*Demand[i]*ratio[i,i1]>=q[i,i1]*2-y111[i,i1]*M)  
        m.addConstr(miu*Demand[i]*ratio[i,i1]<=q[i,i1]*3+y222[i,i1]*M)
        m.addConstr(miu*Demand[i]*ratio[i,i1]>=q[i,i1]*3-y222[i,i1]*M)        
           
        m.addConstr(klane[i,i1]==1+y[i,i1])                         
    for i in s:
        m.addConstr(quicksum(klane[i,i1] for i1 in yy(i))==K[i])                
# 5. maximum degree of saturation
    for i,i1 in movement:
        m.addConstr(q[i,i1]<=P*phi[i,i1]*Q)         
                    
    m.update()    
     
    m.setObjective(miu, GRB.MAXIMIZE)
    m.optimize()   
     
    book=xlwt.Workbook()
    resultSheet=book.add_sheet('phasesetting')
    resultSheet.write(0,0,'phase')
    for i,i1 in movement:
        resultSheet.write(3*(arm[i,i1]-1)+gdirect[i,i1],0,gdirect[i,i1])    
## write phi and sta into excel
    resultSheet.write(0,1,'sta')
    resultSheet.write(0,2,'phi')
    resultSheet.write(0,3,'nlane')
    resultSheet.write(0,4,'flow')
    resultSheet.write(0,5,'arm flow')
    resultSheet.write(0,6,'cycle')    
    resultSheet.write(0,7,'green start')    
    resultSheet.write(0,8,'green duration')    
    resultSheet.write(0,9,'degree of saturation')    
     
    for i,i1 in movement:
        resultSheet.write((arm[i,i1]-1)*3+gdirect[i,i1],1,int(sta[i,i1].x * 1/c.x))
        resultSheet.write((arm[i,i1]-1)*3+gdirect[i,i1],2,int(phi[i,i1].x * 1/c.x))     
        resultSheet.write((arm[i,i1]-1)*3+gdirect[i,i1],3,klane[i,i1].x)  
        resultSheet.write((arm[i,i1]-1)*3+gdirect[i,i1],4,q[i,i1].x)  
        resultSheet.write((arm[i,i1]-1)*3+gdirect[i,i1],5,q[i,i1].x*klane[i,i1].x)  
        resultSheet.write((arm[i,i1]-1)*3+gdirect[i,i1],6,int(1/c.x)) 
        resultSheet.write((arm[i,i1]-1)*3+gdirect[i,i1],7,int(1/c.x*sta[i,i1].x)) 
        resultSheet.write((arm[i,i1]-1)*3+gdirect[i,i1],8,int(1/c.x*phi[i,i1].x))  
        resultSheet.write((arm[i,i1]-1)*3+gdirect[i,i1],9,int(q[i,i1].x/(Q*phi[i,i1].x)))  
        print(y[i,i1].x)   
    book.save('M44.xls')
except GurobiError:
    print('Encountered a Gurobi error')