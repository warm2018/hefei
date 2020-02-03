#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 22:20:17 2019

@author: zhaozhang
"""

#Model4-max capacity, lane setting is known in prior

from gurobipy import *
import xlrd
import xlwt
import numpy as np

try:

    # Create a new model
    m = Model("M4")
    P=0.95 ## maximum degree of saturation
    Q=1800 # lane capacity
    clearance=5 # clearance time in seconds
    mingreen = 20
    maxgreen = 90
    cmin = 100  #cycle in seconds
    cmax = 150

    Demand = [0,1085,0,1822,0,1085,0,1137]  
    M=10000000000
    S=[1,3,5,7] 
    E=[2,4,6,8]   
    K=4
    conflict=[(1,4,3,8),(1,4,5,2),(1,4,7,2),(1,4,3,6),
                              (1,6,7,4),(1,6,3,8),(1,6,7,2),(1,6,5,8),
                              (3,8,1,6),(3,8,1,4),(3,8,7,2),(3,8,5,2),
                              (3,6,7,4),(3,6,5,2),(3,6,5,8),(3,6,1,4),
                              (5,2,1,4),(5,2,3,8),(5,2,3,6),(5,2,7,4),
                              (5,8,1,6),(5,8,3,6),(5,8,7,2),(5,8,7,4),
                              (7,2,1,6),(7,2,1,4),(7,2,3,8),(7,2,5,8),
                              (7,4,1,6),(7,4,3,6),(7,4,5,8),(7,4,5,2)]    
 


    movement,ratio,gdirect,arm,nlane=multidict({(1,4):[0.26,1,1,1],(1,6):[0.64,2,1,2],(1,8):[0.1,3,1,1],
                                                (3,2):[0.10,3,2,1],(3,6):[0.22,1,2,1],(3,8):[0.68,2,2,2],
                                                (5,4):[0.10,3,3,1],(5,2):[0.64,2,3,2],(5,8):[0.26,1,3,1],
                                               (7,4):[0.73,2,4,2],(7,6):[0.10,3,4,1],(7,2):[0.17,1,4,1]})

    '''
    Demand = [0,1000,0,1000,0,1000,0,900]  
    M=100000    
    S=[1,3,5,7] 
    E=[2,4,6,8]   
    K=4 
    conflict=[(1,4,3,8),(1,4,5,2),(1,4,7,2),(1,4,3,6),
                              (1,6,7,4),(1,6,3,8),(1,6,7,2),(1,6,5,8),
                              (3,8,1,6),(3,8,1,4),(3,8,7,2),(3,8,5,2),
                              (3,6,7,4),(3,6,5,2),(3,6,5,8),(3,6,1,4),
                              (5,2,1,4),(5,2,3,8),(5,2,3,6),(5,2,7,4),
                              (5,8,1,6),(5,8,3,6),(5,8,7,2),(5,8,7,4),
                              (7,2,1,6),(7,2,1,4),(7,2,3,8),(7,2,5,8),
                              (7,4,1,6),(7,4,3,6),(7,4,5,8),(7,4,5,2)] 
 
    movement,ratio,gdirect,arm,nlane=multidict({(1,4):[0.3,1,1,1],(1,6):[0.3,2,1,2],(1,8):[0.4,3,1,1],
                                                (3,2):[0.4,3,2,1],(3,6):[0.3,1,2,1],(3,8):[0.3,2,2,2],
                                                (5,4):[0.3,3,3,1],(5,2):[0.5,2,3,2],(5,8):[0.2,1,3,1],
                                                (7,4):[0.4,2,4,2],(7,6):[0.3,3,4,1],(7,2):[0.3,1,4,1]})
    '''


    left=[(1,4),(3,6),(5,8),(7,2)]
    through=[(1,6),(3,8),(5,2),(7,4)]
    right=[(1,8),(3,2),(5,4),(7,6)]
# n=2,4,6,8,create i in S
    def xx(n):
        x=[1,3,5,7]
        for m in [1,3,5,7]:
            if n-m==1:
                x.remove(m)
        return x
# n=1,3,5,7,create i1 in E
    def yy(n):
        y=[2,4,6,8]
        for m in [2,4,6,8]:
            if m-n==1:
                y.remove(m)
        return y
    # Create variables
    sta={}
    phi={}
    omg={}
    q={}   
    alpha={}
    klane={}    
    QC={}
    flow={}# lane flow with direction
    DeRT={}
    miu = m.addVar(lb=0,vtype=GRB.CONTINUOUS)
    c = m.addVar(lb=1/cmax,ub=1/cmin,vtype=GRB.CONTINUOUS)
    for i,i1 in movement:
        sta[i,i1] = m.addVar(lb=0,ub=1,vtype=GRB.CONTINUOUS, name='sta%s_%s_'%(i,i1))
        phi[i,i1] = m.addVar(lb=0.1,ub=0.9,vtype=GRB.CONTINUOUS, name='phi%s_%s'%(i,i1))     
        klane[i,i1] = m.addVar(lb=0,vtype=GRB.INTEGER, name='klane%s_%s'%(i,i1))     
        QC[i,i1] = m.addVar(lb=0,vtype=GRB.INTEGER, name='QC%s_%s'%(i,i1))    
        q[i,i1] = m.addVar(lb=0,vtype=GRB.INTEGER, name='q%s_%s'%(i,i1))  
        
    for i,i1 in movement:
        for k in range(1,K+1):
            DeRT[i,i1,k]=m.addVar(vtype=GRB.BINARY,name='DeRT%s_%s_%s'%(i,i1,k))        
            flow[i,i1,k] = m.addVar(lb=0,vtype=GRB.CONTINUOUS, name='flow%s_%s_%s'%(i,i1,k))       
                                 
    for i,i1,i2,i3 in conflict:
            omg[i,i1,i2,i3]= m.addVar(vtype=GRB.BINARY, name='omg%s_%s_%s_%s'%(i,i1,i2,i3))    
#below is the constraints
# 1. order of movement ,       omg[i,i1,i2,i3]=0表示M[i,i1]在M[i2,i3]的前面    
    for i,i1,i2,i3 in conflict:
        m.addConstr(omg[i,i1,i2,i3]+omg[i2,i3,i,i1]==1)
        m.addConstr(sta[i2,i3]+M*omg[i,i1,i2,i3]>=sta[i,i1]+phi[i,i1]+clearance*c)
        m.addConstr(sta[i2,i3]+phi[i2,i3]-1+clearance*c<=sta[i,i1]+M*omg[i,i1,i2,i3])
        
# 2. green timings
    for i,i1 in movement:
        m.addConstr(phi[i,i1]<=maxgreen*c)
# 3. cycle length
    m.addConstr(c<=1/cmin)
    m.addConstr(c>=1/cmax)
# 4. capacity constrain
    for i,i1 in movement:
        m.addConstr(miu*Demand[i]*ratio[i,i1]==quicksum(flow[i,i1,k] for k in range(1,K+1)))

# 5.one movement can distribute on multiple lanes
    for i,i1 in movement:
        m.addConstr(quicksum(DeRT[i,i1,k] for k in range(1,K+1))>=1) 
# 6. no conflict for adjacent lane settings
    for i in S:
        for i1 in yy(i):
            for i2 in yy(i):
                for k in range(1,K):
                    if(gdirect[i,i1]>gdirect[i,i2]):
                        m.addConstr(DeRT[i,i1,k+1]+DeRT[i,i2,k]<=1)                             
# 7.no lane permission, no flow
    for i,i1 in movement:
        m.addConstr(DeRT[i,i1,k]*M>=flow[i,i1,k])
# 8. maximum degree of saturation
    for i,i1 in movement:
        m.addConstr(flow[i,i1,k]<=Q*P*phi[i,i1])
        m.addConstr(flow[i,i1,k]<=500)
# 9. adjacent lane with same direction has the same flow
    for i,i1 in movement:
        for k in range(1,K):
            m.addConstr(flow[i,i1,k]-flow[i,i1,k+1]<=M*(DeRT[i,i1,k]-DeRT[i,i1,k+1]))
            m.addConstr(flow[i,i1,k]-flow[i,i1,k+1]>=-M*(DeRT[i,i1,k]-DeRT[i,i1,k+1]))
# below are not constraints            
# 10. calculate directed flow, not constraint
    for i,i1 in movement:
        m.addConstr(q[i,i1]==quicksum(flow[i,i1,k] for k in range(1,K+1)))
# 11. calculate lane setting, not constraint
    for i,i1 in movement:
        m.addConstr(klane[i,i1]==quicksum(DeRT[i,i1,k] for k in range(1,K+1)))                        
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
    resultSheet.write(0,6,'green start')    
    resultSheet.write(0,7,'green end')        
    for i,i1 in movement:
        resultSheet.write((arm[i,i1]-1)*3+gdirect[i,i1],1,sta[i,i1].x * 1/c.x)
        resultSheet.write((arm[i,i1]-1)*3+gdirect[i,i1],2,phi[i,i1].x * 1/c.x)
        resultSheet.write((arm[i,i1]-1)*3+gdirect[i,i1],3,klane[i,i1].x)
        resultSheet.write((arm[i,i1]-1)*3+gdirect[i,i1],4,q[i,i1].x)

    print("cycle",1/c.x,miu.x)
    resultSheet=book.add_sheet('DeRT')
    resultSheet.write(0,0,'DeRTvalue')
    for k in range(1,K+1):
        resultSheet.write(0,k,k)    

    for i,i1 in movement:
        resultSheet.write(3*(arm[i,i1]-1)+gdirect[i,i1],0,gdirect[i,i1])        
        for k in range(1,K+1):
            resultSheet.write(3*(arm[i,i1]-1)+gdirect[i,i1],k,DeRT[i,i1,k].x)                  
      
    book.save('M4-Lane1.xls')    
except GurobiError:
    print('Encountered a Gurobi error')
