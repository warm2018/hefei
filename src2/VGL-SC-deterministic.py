#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 09:31:58 2016

@author: zz-mac
#Lane-based model, O2, minimize delay"""

# -*- coding: utf-8 -*-
"""
Created on Sun Oct 23 20:55:32 2016

@author: Administrator
"""
from gurobipy import *
import xlrd
import xlwt
import numpy

try:

    # Create a new model
    m = Model("O2")
    initial=0
    gap = 5
    P=0.95 ## maximum degree of saturation
    mingreen = 20
    maxgreen = 90
    l=300 # link distance
    K = 4 # maximum lane number
    s = 1800 # link capacity in veh/h
    d=6  #jam headway in meters
    w = 20 #shock wave speed
    v = 60 #free flow speed
    Total=192  #simulation time in seconds
    c = 120  #cycle in seconds
    clock = 4  #clock in seconds
    cc=int(c/clock) # cycle length in clock
    Totaltime = int(Total/clock)  #simulation time in clock
    M = 1000000
    U=[1,2,3,4,5,6,7,8]
    S=[1,3,5,7] # set of approach link
    E=[2,4,6,8] # set of exit link
    Demand = 1080 #？？
    a = Demand/3600*clock  #demand in veh/clock
    flowinput = [0,a,0,a,0,a,0,a,]
    PQ = (s/3600*clock)*K  #2.5=1800/3600*clock
    N = (v/3.6*clock*1/d)*K  #v/3.6*clock*1/6
    dcell=v/3.6*clock # cell length
    maxcell = int(l/dcell)+1 # max number of cells 
    initial=0

    movement,ratio,gdirect,arm,nlane=multidict({(1,4):[0.3,1,1,1],(1,6):[0.3,2,1,2],(1,8):[0.4,3,1,1],
                                                (3,2):[0.4,3,2,1],(3,6):[0.3,1,2,1],(3,8):[0.3,2,2,2],
                                                (5,4):[0.3,3,3,1],(5,2):[0.5,2,3,2],(5,8):[0.2,1,3,1],
                                                (7,4):[0.4,2,4,2],(7,6):[0.3,3,4,1],(7,2):[0.3,1,4,1]})
    left,value=multidict({(1,4):1,
                          (3,6):1,
                          (5,8):1,
                          (7,2):1})
    through,value=multidict({(1,6):1,
                             (3,8):1,
                             (5,2):1,
                             (7,4):1})
    right,value=multidict({(1,8):1,
                             (3,2):1,
                             (5,4):1,
                             (7,6):1})
    
    conflict,value=multidict({(1,4,3,8):1,(1,4,5,2):1,(1,4,7,2):1,(1,4,3,6):1,
                              (1,6,7,4):1,(1,6,3,8):1,(1,6,7,2):1,(1,6,5,8):1,
                              (3,8,1,6):1,(3,8,1,4):1,(3,8,7,2):1,(3,8,5,2):1,
                              (3,6,7,4):1,(3,6,5,2):1,(3,6,5,8):1,(3,6,1,4):1,
                              (5,2,1,4):1,(5,2,3,8):1,(5,2,3,6):1,(5,2,7,4):1,
                              (5,8,1,6):1,(5,8,3,6):1,(5,8,7,2):1,(5,8,7,4):1,
                              (7,2,1,6):1,(7,2,1,4):1,(7,2,3,8):1,(7,2,5,8):1,
                              (7,4,1,6):1,(7,4,3,6):1,(7,4,5,8):1,(7,4,5,2):1})
#cities,supply,demand=multidict({
#            'A':[100,20],
#            'B':[150,50],
#            'C':[20,300],
#            'D':[10,200]})

# n=2,4,6,8,create i in S
    def xx(n): # set proceding link
        x=[1,3,5,7]
        for m in [1,3,5,7]:
            if n-m==1:
                x.remove(m)
        return x
# n=1,3,5,7,create i1 in E
    def yy(n): # set of downstream link
        y=[2,4,6,8]
        for m in [2,4,6,8]:
            if m-n==1:
                y.remove(m)
        return y

            

    # Create variables
    sta={}
    phi={}
    zs={}
    klane={}
    alpha={}
    #zs denote the variable for two scenarios for signal settings
    for i,i1 in movement:
            sta[i,i1] = m.addVar(lb=0,ub=0.9*c,vtype=GRB.INTEGER, name='sta%s_%s_'%(i,i1))
            phi[i,i1] = m.addVar(lb=mingreen,ub=c,vtype=GRB.INTEGER, name='phi%s_%s'%(i,i1)) 
            zs[i,i1] = m.addVar(vtype=GRB.BINARY, name='zs%s_%s'%(i,i1))
            klane[i,i1] = m.addVar(lb=1,ub=3,vtype=GRB.INTEGER, name='klane%s_%s'%(i,i1))
    for i in S:            
            alpha[i] = m.addVar(lb=-1,ub=1,vtype=GRB.INTEGER, name='alpha%s'%(i))  #VGL的设置变量
            
            
    omg={}
    for i,i1,i2,i3 in conflict:
            omg[i,i1,i2,i3]= m.addVar(vtype=GRB.BINARY, name='omg%s_%s_%s_%s'%(i,i1,i2,i3))
#fI: movement flow
#QI movement capacity
#volve movement binary variable            
    volve={}
    yI={}
    for i,i1 in movement:
        for t in range(1, Totaltime+1):
            yI[i,i1,t] = m.addVar(lb=0.0,vtype=GRB.CONTINUOUS, name='yI%s_%s_%s'%(i,i1,t))
            volve[i,i1,t] = m.addVar(vtype=GRB.BINARY, name='volve%s_%s_%s'%(i,i1,t))        
    zs1={}
    zs2={}
    z3={}
    z4={}
    z3o={}
    z4o={}    
#zs1 and zs2: integer variable for signal settings
#z3 and z4: integer variable for movement volve               
    for i,i1 in movement:
        for t in range(1, Totaltime+1):
            zs1[i,i1,t] = m.addVar(vtype=GRB.BINARY, name='zs1%s_%s_%s'%(i,i1,t)) 
            zs2[i,i1,t] = m.addVar(vtype=GRB.BINARY, name='zs2%s_%s_%s'%(i,i1,t)) 
            z3[i,i1,t]= m.addVar( vtype=GRB.BINARY, name='z3%s_%s_%s'%(i,i1,t))  
            z4[i,i1,t]= m.addVar( vtype=GRB.BINARY, name='z4%s_%s_%s'%(i,i1,t))      
            z3o[i,i1,t]= m.addVar( vtype=GRB.BINARY, name='z3o%s_%s_%s'%(i,i1,t))  
            z4o[i,i1,t]= m.addVar( vtype=GRB.BINARY, name='z4o%s_%s_%s'%(i,i1,t))              
    z1={}
    z2={}
    n={}
# z1 and z2: integer variable for flow constrains
# n: accumulation         
    for i in U:
        for j in range(1,maxcell):   
            for t in range(1, Totaltime+2):
                n[i,j,t] = m.addVar(lb = 0.0,ub = N, vtype=GRB.CONTINUOUS, name='n%s_%s_%s'%(i,j,t))    
                z1[i,j,t]= m.addVar( vtype=GRB.BINARY, name='z1%s_%s_%s'%(i,j,t))  
                z2[i,j,t]= m.addVar( vtype=GRB.BINARY, name='z2%s_%s_%s'%(i,j,t))  
    y={}
#f: flow                  
    for i in U:
        for j in range(1,maxcell+1):   
            for t in range(1, Totaltime+1):
                y[i,j,t] = m.addVar(lb = 0.0, vtype=GRB.CONTINUOUS, name='y%s_%s_%s'%(i,j,t))    
# initial accumulation is 0
    for i in U:
        for j in range(1,maxcell):  
            m.addConstr(n[i,j,1] == initial)
                   
# Integrate new variables
#    m.update()
##1. link flow input    
    for i in S:
        for t in range(1, Totaltime+1):   
             m.addConstr(y[i,1,t] <= flowinput[i])
             m.addConstr(y[i,1,t] <= PQ) 
             m.addConstr(y[i,1,t] <=w/v*(N-n[i,1,t]))  
             m.addConstr(y[i,1,t] >= flowinput[i]-z1[i,1,t]*M)
             m.addConstr(y[i,1,t] >= PQ-z2[i,1,t]*M) 
             m.addConstr(y[i,1,t] >=w/v*(N-n[i,1,t])-(2-z1[i,1,t]-z2[i,1,t])*M)    
#                       
##2. normal link flow constrains, from cell 2 to the second last cell              
    for i in U:
        for j in range(2,maxcell-1):   
            for t in range(1, Totaltime+1):
                m.addConstr(y[i,j,t]<=n[i,j-1,t])
                m.addConstr(y[i,j,t]<=PQ)
                m.addConstr(y[i,j,t]<=w/v*(N-n[i,j,t]))
                m.addConstr(y[i,j,t]>=n[i,j-1,t]-z1[i,j,t]*M)
                m.addConstr(y[i,j,t]>=PQ-z2[i,j,t]*M)
                m.addConstr(y[i,j,t]>=w/v*(N-n[i,j,t])-(2-z1[i,j,t]-z2[i,j,t])*M)    
#
##3. movement flow constrains
#
# 3.1 small cell dynamics  
    sn={}
    yi={}
    yo={}
    NS={} 
    QI={}
    #variable definition
    for i,i1 in movement:
        QI[i,i1] = m.addVar(lb=0,vtype=GRB.CONTINUOUS, name='QI%s_%s'%(i,i1))  
        NS[i,i1] = m.addVar(lb=0,vtype=GRB.CONTINUOUS, name='NS%s_%s'%(i,i1))                
        for t in range(1, Totaltime+1): 
            sn[i,i1,t] = m.addVar(lb=0,vtype=GRB.CONTINUOUS, name='sn%s_%s_%s'%(i,i1,t)) 
            yo[i,i1,t] = m.addVar(lb=0,vtype=GRB.CONTINUOUS, name='yo%s_%s_%s'%(i,i1,t)) 
            yi[i,i1,t] = m.addVar(lb=0,vtype=GRB.CONTINUOUS, name='yi%s_%s_%s'%(i,i1,t)) 
    #dynamics            
    for i,i1 in movement:
        m.addConstr(QI[i,i1]==PQ*klane[i,i1]/K)  
        m.addConstr(NS[i,i1]==N*klane[i,i1]/K)          
        for t in range(1, Totaltime+1): 
            m.addConstr(yi[i,i1,t]<=n[i,maxcell-2,t]*ratio[i,i1])
            m.addConstr(yi[i,i1,t]<=QI[i,i1])                ##VGL这里需要修改
            m.addConstr(yi[i,i1,t]<=w/v*(NS[i,i1]-sn[i,i1,t]))
            m.addConstr(yi[i,i1,t]>=n[i,maxcell-2,t]*ratio[i,i1]-z3[i,i1,t]*M)
            m.addConstr(yi[i,i1,t]>=QI[i,i1]-z4[i,i1,t]*M)   ##VGL这里需要修改
            m.addConstr(yi[i,i1,t]>=w/v*(NS[i,i1]-sn[i,i1,t]-(2-z3[i,i1,t]-z4[i,i1,t])*M)) 
#                #below small cell outflow
            m.addConstr(yo[i,i1,t]<=sn[i,i1,t])
            m.addConstr(yo[i,i1,t]<=QI[i,i1]*volve[i,i1,t])                ##VGL这里需要修改
            m.addConstr(yo[i,i1,t]<=w/v*(N-n[i1,1,t]))                 
            m.addConstr(yo[i,i1,t]>=sn[i,i1,t]-z3o[i,i1,t]*M)
            m.addConstr(yo[i,i1,t]>=QI[i,i1]*volve[i,i1,t]-z4o[i,i1,t]*M)   ##VGL这里需要修改
            m.addConstr(yo[i,i1,t]>=w/v*(N-n[i1,1,t])-(2-z3o[i,i1,t]-z4o[i,i1,t])*M)                 
                      
##4. VGL设置

    for i,i1 in movement:
        m.addConstr(klane[i,i1]>=1)
    for i,i1 in left:        
        m.addConstr(klane[i,i1]==nlane[i,i1]+alpha[i])
    for i,i1 in through:        
        m.addConstr(klane[i,i1]==nlane[i,i1]-alpha[i]) 
    for i,i1 in right:        
        m.addConstr(klane[i,i1]==1)         
##5. signal settings
       
    for i,i1 in movement:
        m.addConstr(sta[i,i1]+phi[i,i1]<=c+zs[i,i1]*M)
        m.addConstr(1+c<=sta[i,i1]+phi[i,i1]+(1-zs[i,i1])*M)
        for t in range(1, cc+1):       
            m.addConstr(t<=(sta[i,i1]+phi[i,i1]) /clock +(1-volve[i,i1,t])*M+zs[i,i1]*M)
            m.addConstr(t>=(sta[i,i1])/clock-(1-volve[i,i1,t])*M-zs[i,i1]*M)            
            m.addConstr(t<=(sta[i,i1]-1) /clock  +volve[i,i1,t]*M+zs[i,i1]*M+zs1[i,i1,t]*M)   
            m.addConstr(t>=(sta[i,i1]+phi[i,i1]+1)/clock-volve[i,i1,t]*M-zs[i,i1]*M-(1-zs1[i,i1,t])*M )                  
            m.addConstr(t<=(sta[i,i1]-1)/clock+volve[i,i1,t]*M+(1-zs[i,i1])*M)  
            m.addConstr(t>=(sta[i,i1]+phi[i,i1]-c+1)/clock-volve[i,i1,t]*M-(1-zs[i,i1])*M)    
            m.addConstr(t>=sta[i,i1]/clock-(1-zs[i,i1])*M-(1-zs2[i,i1,t])*M-(1-volve[i,i1,t])*M)     
            m.addConstr(t<=(sta[i,i1]+phi[i,i1]-c)/clock+(1-zs[i,i1])*M+(1-volve[i,i1,t])*M+zs2[i,i1,t]*M)           
            
#signal for right turn#
    for i,i1 in right:        
        m.addConstr(sta[i,i1]==0)
        m.addConstr(phi[i,i1]==c)
        
        
                ##9. order of movement
    for i,i1,i2,i3 in conflict:
        m.addConstr(omg[i,i1,i2,i3]+omg[i2,i3,i,i1]==1)
        m.addConstr(sta[i2,i3]+c*omg[i,i1,i2,i3]>=sta[i,i1]+phi[i,i1]+gap)
    for i,i1 in movement:
        for t in range(1,Totaltime+1-cc):
            m.addConstr(volve[i,i1,t]==volve[i,i1,t+cc])       
###6.flow into link in E
    for i1 in E:
        for t in range(1, Totaltime+1):
            m.addConstr(y[i1,1,t] == quicksum(yo[i,i1,t] for i in xx(i1)))
##7.last big cell outflow on link i in S
    for i in S:
        for t in range(1, Totaltime+1):
            m.addConstr(y[i,maxcell-1,t] == quicksum(yi[i,i1,t] for i1 in yy(i)))           
#
##outflow of link i1 in E   
    for i1 in E:
        for t in range(1, Totaltime+1):
            m.addConstr(y[i1,maxcell,t] ==n[i1,maxcell-1,t])  
##8. CTM¸update  
    for i in S:
        for j in range(1,maxcell-1):
            for t in range(1,Totaltime+1):
                m.addConstr(n[i,j,t+1] == n[i,j,t] + y[i,j,t] - y[i,j+1,t])                        
    for i in E:
        for j in range(1,maxcell):
            for t in range(1,Totaltime+1):
                m.addConstr(n[i,j,t+1] == n[i,j,t] + y[i,j,t] - y[i,j+1,t])  
                
##9. intersection ctm update
    for i,i1 in movement:   
        for t in range(1, Totaltime): 
            m.addConstr(sn[i,i1,t+1]==sn[i,i1,t]+yi[i,i1,t]-yo[i,i1,t])                   
                           
## total output
    OP={}
    for i in E:
        for t in range(1,Totaltime+1):
            OP=m.addVar(vtype=GRB.CONTINUOUS,name='OP%s_%s'%(i,t))
            m.addConstr(OP==quicksum(y[i,maxcell,t] for i in E
                                                           for t in range(1,Totaltime+1))) 
    sT={}            
    sT= quicksum(sn[i,i1,t]-yo[i,i1,t] for i,i1 in movement
                                             for t in range(1,Totaltime+1))                               
    D={}
    for i in U:
        for t in range(1,Totaltime+1):
            D[i,t]=m.addVar(vtype=GRB.CONTINUOUS,name='D%s_%s'%(i,t))
    for i in U: 
        for t in range(1,Totaltime+1):
            m.addConstr(D[i,t]==clock*quicksum(n[i,j,t]-y[i,j+1,t] for j in range(1,maxcell-2)))      
            
    DT={}
    for t in range(1,Totaltime+1):
        DT[t]=m.addVar(vtype=GRB.CONTINUOUS,name='DT%s'%(t)) 
    for t in range(1,Totaltime+1):
        m.addConstr(DT[t]==quicksum(D[i,t] for i in U))          
    TD={}
    TD=m.addVar(vtype=GRB.CONTINUOUS,name='DT%s'%(t))
    m.addConstr(TD==quicksum(DT[t] for t in range(1,Totaltime+1)))               
#     
#Delay calculation by time        
       
    m.update()    
    m.setObjective(TD+sT, GRB.MINIMIZE)
#    m.Params.MIPFocus=1
#    m.Params.ImproveStartGap=5
    m.Params.Method=4
    m.Params.Heuristics=0.001
    m.Params.CutPasses=1
    m.optimize()

    book=xlwt.Workbook()
    resultSheet=book.add_sheet('phasesetting')
    resultSheet.write(0,0,'phase')
    for i,i1 in movement:
        resultSheet.write(3*(arm[i,i1]-1)+gdirect[i,i1],0,gdirect[i,i1])    
## write phi and sta into excel
    resultSheet.write(0,1,'sta')
    resultSheet.write(0,2,'phi')
    resultSheet.write(0,3,'klane')    
    for i,i1 in movement:
        resultSheet.write((arm[i,i1]-1)*3+gdirect[i,i1],1,sta[i,i1].x)
        resultSheet.write((arm[i,i1]-1)*3+gdirect[i,i1],2,phi[i,i1].x)       
        resultSheet.write((arm[i,i1]-1)*3+gdirect[i,i1],3,klane[i,i1].x)   
    resultSheet=book.add_sheet('accumulation')
    resultSheet.write(0,0,'link')
    resultSheet.write(0,1,'time')
    for j in range(1,maxcell):
        resultSheet.write(0,j+1,j)    

    for i in U:
        for t in range(1, Totaltime+1):
                resultSheet.write(Totaltime*(i-1)+t,0,i)
                resultSheet.write(Totaltime*(i-1)+t,1,t)
            
    for i in U:
        for j in range(1,maxcell):            
            for t in range(1, Totaltime+1):                                
                resultSheet.write(Totaltime*(i-1)+t,j+1,n[i,j,t].x)

    resultSheet=book.add_sheet('flow')
    resultSheet.write(0,0,'link')
    resultSheet.write(0,1,'time')
    for j in range(1,maxcell+1):
        resultSheet.write(0,j+1,j)  
        
    for i in U:
        for t in range(1, Totaltime+1):
                resultSheet.write(Totaltime*(i-1)+t,0,i)
                resultSheet.write(Totaltime*(i-1)+t,1,t)    
        
    for i in U:
        for j in range(1,maxcell+1):            
            for t in range(1, Totaltime+1):                                
                resultSheet.write(Totaltime*(i-1)+t,j+1,y[i,j,t].x)                    
    resultSheet=book.add_sheet('samll cell accumulation')
    resultSheet.write(0,0,'time')

    for i,i1 in left:
            resultSheet.write(0,i+gdirect[i,i1]-1,'left')    
    for i,i1 in through:
            resultSheet.write(0,i+gdirect[i,i1]-1,'through')    

    for t in range(1, Totaltime+1):
        resultSheet.write(t,0,t)
#            
    for i,i1 in left:           
            for t in range(1, Totaltime+1):                                
                resultSheet.write(t,i+gdirect[i,i1]-1,sn[i,i1,t].x)
    for i,i1 in through:           
            for t in range(1, Totaltime+1):                                
                resultSheet.write(t,i+gdirect[i,i1]-1,sn[i,i1,t].x)
                
    resultSheet=book.add_sheet('samll cell inflow')
    resultSheet.write(0,0,'time')

    for i,i1 in left:
            resultSheet.write(0,i+gdirect[i,i1]-1,'left')    
    for i,i1 in through:
            resultSheet.write(0,i+gdirect[i,i1]-1,'through')    

    for t in range(1, Totaltime+1):
        resultSheet.write(t,0,t)
#            
    for i,i1 in left:           
            for t in range(1, Totaltime+1):                                
                resultSheet.write(t,i+gdirect[i,i1]-1,yi[i,i1,t].x)
    for i,i1 in through:           
            for t in range(1, Totaltime+1):                                
                resultSheet.write(t,i+gdirect[i,i1]-1,yi[i,i1,t].x)
    resultSheet=book.add_sheet('samll cell outflow')
    resultSheet.write(0,0,'time')

    for i,i1 in left:
            resultSheet.write(0,i+gdirect[i,i1]-1,'left')    
    for i,i1 in through:
            resultSheet.write(0,i+gdirect[i,i1]-1,'through')    

    for t in range(1, Totaltime+1):
        resultSheet.write(t,0,t)
#            
    for i,i1 in left:           
            for t in range(1, Totaltime+1):                                
                resultSheet.write(t,i+gdirect[i,i1]-1,yo[i,i1,t].x)
    for i,i1 in through:           
            for t in range(1, Totaltime+1):                                
                resultSheet.write(t,i+gdirect[i,i1]-1,yo[i,i1,t].x)
    resultSheet=book.add_sheet('samll cell delay')
    resultSheet.write(0,0,'time')

    for i,i1 in left:
            resultSheet.write(0,i+gdirect[i,i1]-1,'left')    
    for i,i1 in through:
            resultSheet.write(0,i+gdirect[i,i1]-1,'through')    

    for t in range(1, Totaltime+1):
        resultSheet.write(t,0,t)
#            
    for i,i1 in left:           
            for t in range(1, Totaltime+1):                                
                resultSheet.write(t,i+gdirect[i,i1]-1,sn[i,i1,t].x-yo[i,i1,t].x)
    for i,i1 in through:           
            for t in range(1, Totaltime+1):                                
                resultSheet.write(t,i+gdirect[i,i1]-1,sn[i,i1,t].x-yo[i,i1,t].x)
# write Delay into excel
    resultSheet=book.add_sheet('Delay')
    resultSheet.write(0,0,'DT')
    resultSheet.write(0,1,'DIT')
    for i in U:
        resultSheet.write(0,i+1,i)
    for t in range(1,Totaltime+1):
        resultSheet.write(t,0,DT[t].x)          
        for i in U:
            resultSheet.write(t,i+1,D[i,t].x)

    book.save('DemandscellVGL%g.xls'%Demand)    
    
    
except GurobiError:
    print('Encountered a Gurobi error')

except AttributeError:
    print('Encountered an attribute error')                