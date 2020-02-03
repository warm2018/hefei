#  -*- coding='utf-8' -*-

from gurobipy import *
import numpy as np
from matplotlib import pyplot as plt
import datetime
import xlwt

start = datetime.datetime.now()

delay_cycle = []
clock = 5
        
#n = 2, 4, 6, create i in S
def xx(n):
    x = [1, 3, 5, 7]
    for m in [1, 3, 5, 7]:
        if n-m == 1:
            x.remove(m)
    return x
    
#n = 1, 3, 5, create in E
def yy(n):
    if n == 3:
        y = [4, 6, 8]
        for m in [4, 6, 8]:
            if m-n ==1:
                y.remove(m)
            return y
    else:
        y = [2, 4, 6, 8]
        for m in [2, 4, 6, 8]:
            if m-n == 1:
                y.remove(m)
        return y
            
def lp_optimize(c, bina):
    try:
        m = Model('si%i'%(c))
        gap = clock #clearance time
        mingreen = 15
        Totaltime = 540
        maxcell = 5
        Tc = int(Totaltime/clock)
        cc = int(c/clock)
        w = 20   #shock wave speed
        v = 60   #free flow speed
        d = 5    #jam headway in meters
        K = 2
        #K = [0, 2, 1, 1, 1, 1, 1]
        s = 1800    #saturated flow rate for one lane

        PQ = (s/3600*clock)*K
        N = (v/3.6*clock*1/d)*K
    
        M = 1000000 #infinite number
        U = [1, 2, 3, 4, 5, 6, 7, 8]
        S = [1, 3, 5, 7]
        E = [2, 4, 6, 8]
        Demand = 1800
        flowinput = [0, (200/3600)*clock, 0, (200/3600)*clock, 0, (200/3600)*clock, 0, (200/3600)*clock]
        initial = 0
        #gdirect = 1 signs left-turn, and 2 right-turn,
        #arm signs intersection arm
        movement, ratio, gdirect, arm = multidict({
        (1, 4): [0.2, 1, 1], (1, 6): [0.4, 2, 1], (1, 8): [0.4, 3, 1],
        (3, 6): [0.5, 1, 2], (3, 8): [0.5, 2, 2],
        (5, 8): [0.3, 1, 3], (5, 2): [0.4, 2, 3], (5, 4): [0.3, 3, 3],
        (7, 2): [0.3, 1, 4], (7, 4): [0.4, 2, 4], (7, 6): [0.3, 3, 4]})
        conflict, value = multidict({(1,4,3,8):1,(1,4,5,2):1,(1,4,7,2):1,(1,4,3,6):1,
                                     (1,6,7,4):1,(1,6,3,8):1,(1,6,7,2):1,(1,6,5,8):1,
                                     (3,8,1,6):1,(3,8,1,4):1,(3,8,7,2):1,(3,8,5,2):1,
                                     (3,6,7,4):1,(3,6,5,2):1,(3,6,5,8):1,(3,6,1,4):1,
                                     (5,2,1,4):1,(5,2,3,8):1,(5,2,3,6):1,(5,2,7,4):1,
                                     (5,8,1,6):1,(5,8,3,6):1,(5,8,7,2):1,(5,8,7,4):1,
                                     (7,2,1,6):1,(7,2,1,4):1,(7,2,3,8):1,(7,2,5,8):1,
                                     (7,4,1,6):1,(7,4,3,6):1,(7,4,5,8):1,(7,4,5,2):1})

            
        sta = {}
        phi = {}
        zs = {}
        for i,i1 in movement:
                sta[i,i1] = m.addVar(lb=0.0,ub=0.9,vtype=GRB.CONTINUOUS, name='sta%s_%s_'%(i,i1))
                phi[i,i1] = m.addVar(lb=mingreen/c,ub=1.0,vtype=GRB.CONTINUOUS, name='phi%s_%s'%(i,i1)) 
                zs[i,i1] = m.addVar(vtype=GRB.BINARY, name='zs%s_%s'%(i,i1))
        omg={}
        for i,i1,i2,i3 in conflict:
                omg[i,i1,i2,i3]= m.addVar(vtype=GRB.BINARY, name='omg%s_%s_%s_%s'%(i,i1,i2,i3))
        
        volve = {}
        fI = {}
        for i,i1 in movement:
            for t in range(1, Tc+1):
                fI[i,i1,t] = m.addVar(lb=0.0,vtype=GRB.CONTINUOUS, name='fI%s_%s_%s'%(i,i1,t))
                volve[i,i1,t] = m.addVar(vtype=GRB.BINARY, name='volve%s_%s_%s'%(i,i1,t))
        zs1={}
        zs2={}
        z3={}
        z4={}
    #zs1 and zs2: integer variable for signal settings
    #z3 and z4: integer variable for movement volve
        for i,i1 in movement:
            for t in range(1, Tc+1):
                zs1[i,i1,t] = m.addVar(vtype=GRB.BINARY, name='zs1%s_%s_%s'%(i,i1,t))
                zs2[i,i1,t] = m.addVar(vtype=GRB.BINARY, name='zs2%s_%s_%s'%(i,i1,t))
                z3[i,i1,t]= m.addVar( vtype=GRB.BINARY, name='z3%s_%s_%s'%(i,i1,t))
                z4[i,i1,t]= m.addVar( vtype=GRB.BINARY, name='z4%s_%s_%s'%(i,i1,t))
        z1={}
        z2={}
        n={}
    # z1 and z2: integer variable for flow constrains
    # n: accumulation
        for i in U:
            for j in range(1,maxcell):
                for t in range(1, Tc+2):
                    n[i,j,t] = m.addVar(lb = 0.0, vtype=GRB.CONTINUOUS, name='n%s_%s_%s'%(i,j,t))
                    z1[i,j,t]= m.addVar( vtype=GRB.BINARY, name='z1%s_%s_%s'%(i,j,t))
                    z2[i,j,t]= m.addVar( vtype=GRB.BINARY, name='z2%s_%s_%s'%(i,j,t))
        f={}
    #f: flow
        for i in U:
            for j in range(1,maxcell+1):
                for t in range(1, Tc+1):
                    f[i,j,t] = m.addVar(lb = 0.0, vtype=GRB.CONTINUOUS, name='f%s_%s_%s'%(i,j,t))
        # initial accumulation is 0
        for i in U:
            for j in range(1,maxcell):
                m.addConstr(n[i,j,1] == initial)
    # Integrate new variables
    #    m.update()
    ##link flow input
        for i in S:
            for t in range(1, Tc+1):
                m.addConstr(f[i,1,t] <= flowinput[i])
                m.addConstr(f[i,1,t] <= PQ)
                m.addConstr(f[i,1,t] <= w/v*(N-n[i,1,t]))
                m.addConstr(f[i,1,t] >= flowinput[i]-z1[i,1,t]*M)
                m.addConstr(f[i,1,t] >= PQ-z2[i,1,t]*M)
                m.addConstr(f[i,1,t] >= w/v*(N-n[i,1,t])-(2-z1[i,1,t]-z2[i,1,t])*M)
    #normal link flow constrains, from cell 2 to the last cell
        for i in U:
            for j in range(2,maxcell):   
                for t in range(1, Tc+1):
                    m.addConstr(f[i,j,t] <= n[i,j-1,t])
                    m.addConstr(f[i,j,t] <= PQ)
                    m.addConstr(f[i,j,t] <= w/v*(N-n[i,j,t]))
                    m.addConstr(f[i,j,t] >= n[i,j-1,t]-z1[i,j,t]*M)
                    m.addConstr(f[i,j,t] >= PQ-z2[i,j,t]*M)
                    m.addConstr(f[i,j,t] >= w/v*(N-n[i,j,t])-(2-z1[i,j,t]-z2[i,j,t])*M)
                    
        DeRT={}
        for i,i1 in movement:
            for k in range(1,K+1):
                DeRT[i,i1,k]=m.addVar(vtype=GRB.BINARY,name='DeRT%s_%s_%s'%(i,i1,k))
        #print(DeRT)
        
    #movement flow constrains
        for i,i1 in movement:
            for t in range(1, Tc+1):
                m.addConstr(fI[i,i1,t]<=n[i,maxcell-1,t]*ratio[i,i1])
                m.addConstr(fI[i,i1,t]<=PQ*ratio[i,i1]*volve[i,i1,t])
                m.addConstr(fI[i,i1,t]<=w/v*(N-n[i1,1,t]))
                m.addConstr(fI[i,i1,t]>=n[i,maxcell-1,t]*ratio[i,i1]-z3[i,i1,t]*M)
                m.addConstr(fI[i,i1,t]>=PQ*ratio[i,i1]*volve[i,i1,t]-z4[i,i1,t]*M)
                m.addConstr(fI[i,i1,t]>=w/v*(N-n[i1,1,t])-(2-z3[i,i1,t]-z4[i,i1,t])*M)
                
    #1 lane permission
    #2. one lane can share multiple directions
        for i in [1, 5, 7]:
            for k in range(1,K+1):
                m.addConstr(quicksum(DeRT[i,i1,k] for i1 in yy(i))>=1)
                m.addConstr(quicksum(DeRT[i,i1,k] for i1 in yy(i))<=2)
                
        for k in range(1, K+1):
            m.addConstr(quicksum(DeRT[3, i1, k] for i1 in [6, 8])>=1)
            m.addConstr(quicksum(DeRT[3, i1, k] for i1 in [6, 8])<=2)
    #share less than two directions
    #3.one movement can distribute on multiple lanes
        for i,i1 in movement:
            m.addConstr(quicksum(DeRT[i,i1,k] for k in range(1,K+1))>=1)
    
        #print(DeRT)
    #4.flow distribution
    #5. no conflict for adjacent lane settings
        #here 'k+1' constrains that the number of lanes must bigger than one
        for i in S:
            for i1 in yy(i):
                for i2 in yy(i):
                    for k in range(1,K):
                        if (gdirect[i,i1] > gdirect[i,i2]):
                            m.addConstr(DeRT[i,i1,k+1]+DeRT[i,i2,k]<=1)
    #6.Phase synchronization
        STA={}
        PHI={}
        for i in S:
            for k in range(1,K+1):
                STA[i,k] = m.addVar(lb=0.0,ub=0.9,vtype=GRB.CONTINUOUS, name='STA%s_%s'%(i,k))
                PHI[i,k] = m.addVar(lb=mingreen/c,ub=1.0,vtype=GRB.CONTINUOUS, name='PHI%s_%s'%(i,k))
    
        for i in S:
            for i1 in yy(i):
                for k in range(1,K+1):
                    m.addConstr(M*(1-DeRT[i,i1,k]) >= STA[i,k]-sta[i,i1])
                    m.addConstr(-M*(1-DeRT[i,i1,k]) <= STA[i,k]-sta[i,i1])
                    m.addConstr(M*(1-DeRT[i,i1,k]) >= PHI[i,k]-phi[i,i1])
                    m.addConstr(-M*(1-DeRT[i,i1,k]) <= PHI[i,k]-phi[i,i1])
    #signal for right turn#
        m.addConstr(phi[1,8]==1)
        m.addConstr(phi[5,4]==1)
        m.addConstr(phi[7,6]==1)
        m.addConstr(sta[1,8]==0)
        m.addConstr(sta[5,4]==0)
        m.addConstr(sta[7,6]==0)
                
    #flow into link in E
        for i1 in [4, 6, 8]:
            for t in range(1, Tc+1):
                m.addConstr(f[i1,1,t] == quicksum(fI[i,i1,t] for i in xx(i1)))
                
        for t in range(1, Tc+1):
            m.addConstr(f[2,1,t] == quicksum(fI[i,2,t] for i in [5, 7]))
    #last cell flow on link i in S
        for i in S:
            for t in range(1, Tc+1):
                m.addConstr(f[i,maxcell,t] == quicksum(fI[i,i1,t] for i1 in yy(i)))
                
        for i,i1 in movement:
            m.addConstr(sta[i,i1]+phi[i,i1]<=1+zs[i,i1]*M)
            m.addConstr(1.01<=sta[i,i1]+phi[i,i1]+(1-zs[i,i1])*M)
            for t in range(1, cc+1):
                m.addConstr(t<=c*(sta[i,i1]+phi[i,i1]) /clock +(1-volve[i,i1,t])*M+zs[i,i1]*M)
                m.addConstr(t>=c*(sta[i,i1])/clock-(1-volve[i,i1,t])*M-zs[i,i1]*M)
                m.addConstr(t<=c*sta[i,i1] /clock -1 +volve[i,i1,t]*M+zs[i,i1]*M+zs1[i,i1,t]*M)
                m.addConstr(t>=c*(sta[i,i1]+phi[i,i1])/clock+1-volve[i,i1,t]*M-zs[i,i1]*M-(1-zs1[i,i1,t])*M )
                m.addConstr(t<=c*sta[i,i1]/clock-1+volve[i,i1,t]*M+(1-zs[i,i1])*M)
                m.addConstr(t>=c*(sta[i,i1]+phi[i,i1]-1)/clock+1-volve[i,i1,t]*M-(1-zs[i,i1])*M)
                m.addConstr(t>=c*sta[i,i1]/clock-(1-zs[i,i1])*M-(1-zs2[i,i1,t])*M-(1-volve[i,i1,t])*M)
                m.addConstr(t<=c*(sta[i,i1]+phi[i,i1]-1)/clock+(1-zs[i,i1])*M+(1-volve[i,i1,t])*M+zs2[i,i1,t]*M)
                
    #outflow of link i1 in E
        for i1 in E:
            for t in range(1, Tc+1):
                m.addConstr(f[i1,maxcell,t] == n[i1,maxcell-1,t])
    #CTM update
        for i in U:
            for j in range(1,maxcell):
                for t in range(1,Tc+1):
                    m.addConstr(n[i,j,t+1] == n[i,j,t] + f[i,j,t] - f[i,j+1,t])
                
    #order of movement
        for i,i1,i2,i3 in conflict:
            m.addConstr(omg[i,i1,i2,i3]+omg[i2,i3,i,i1]==1)
            m.addConstr(sta[i2,i3]+omg[i,i1,i2,i3]>=sta[i,i1]+phi[i,i1]+gap/c)
            # m.addConstr(omg[1,4,3,6] == 1)
            # m.addConstr(omg[1,4,5,2] == 1)
            # m.addConstr(omg[3,6,5,2] == 1)
    #make sure that the value of variables volve is the same in every cycle
        for i,i1 in movement:
            for t in range(1,Tc+1-cc):
                m.addConstr(volve[i,i1,t]==volve[i,i1,t+cc])
                
    # total output
        OP={}
        for i in E:
            for t in range(1,Tc+1):
                OP=m.addVar(vtype=GRB.CONTINUOUS,name='OP%s_%s'%(i,t))
                m.addConstr(OP==quicksum(f[i,maxcell,t] for i in E
                                                            for t in range(1,Tc+1)))
                
        D={}
        for i in U:
            for t in range(1,Tc+1):
                D[i,t]=m.addVar(vtype=GRB.CONTINUOUS,name='D%s_%s'%(i,t))
    
        for i in U:
            for t in range(1,Tc+1):
                m.addConstr(D[i,t]==clock*quicksum(n[i,j,t]-f[i,j+1,t] for j in range(1,maxcell)))
        DT={}
        for t in range(1,Tc+1):
            DT[t]=m.addVar(vtype = GRB.CONTINUOUS,name='DT%s'%(t))
        for t in range(1,Tc+1):
            m.addConstr(DT[t] == quicksum(D[i,t] for i in U))
    
        m.update()
    #Set objective
        m.setObjective(clock*quicksum(n[i,maxcell-1,t]-f[i,maxcell,t] for i in S
                                                                        for t in range(Tc-int(300/clock),Tc+1)), GRB.MINIMIZE)
                
    #m.Params.MIPFocus=1
    #m.Params.ImproveStartGap=5
    #m.Params.Method=4
    
        m.optimize()

        book=xlwt.Workbook()
        resultSheet=book.add_sheet('phasesetting')
        resultSheet.write(0,0,'phase')
        for i,i1 in movement:
            resultSheet.write(3*(arm[i,i1]-1)+gdirect[i,i1],0,gdirect[i,i1])    
    ## write phi and sta into excel
        resultSheet.write(0,1,'sta')
        resultSheet.write(0,2,'phi')
        for i,i1 in movement:
            resultSheet.write((arm[i,i1]-1)*3+gdirect[i,i1],1,sta[i,i1].x)
            resultSheet.write((arm[i,i1]-1)*3+gdirect[i,i1],2,phi[i,i1].x)  

        resultSheet=book.add_sheet('DeRT')
        resultSheet.write(0,0,'DeRTvalue')

        for k in range(1,K+1):
            resultSheet.write(0,k,k)    

        for i,i1 in movement:
            resultSheet.write(3*(arm[i,i1]-1)+gdirect[i,i1],0,gdirect[i,i1])        
            for k in range(1,K+1):
                resultSheet.write(3*(arm[i,i1]-1)+gdirect[i,i1],k,DeRT[i,i1,k].x)                  
          
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

    # write fI into excel
        resultSheet=book.add_sheet('yI')
        resultSheet.write(0,0,'time')
        resultSheet.write(0,1,'left')
        resultSheet.write(0,2,'through')
        resultSheet.write(0,3,'righ')    
              
        for t in range(1,Totaltime+1):
            resultSheet.write(t,0,t)
                
        for i,i1 in movement:
            for t in range(1,Totaltime+1):
                resultSheet.write(Totaltime*(arm[i,i1]-1)+t,gdirect[i,i1],yI[i,i1,t].x)  
                resultSheet.write(Totaltime*(arm[i,i1]-1)+t,gdirect[i,i1]+3,volve[i,i1,t].x)  

        book.save('DemandVGL%g.xls'%Demand)    
    
    except AttributeError:
        print('Encountered an attribute error')
'''
for cy in range(45, 181, clock):
    lp_optimize(cy, 0)
        
all_delay = []
for i in range(len(delay_cycle)):
    all_delay.append(delay_cycle[i][1])
    
best_cycle = []
    
min_delay = min(all_delay)
for i in range(len(delay_cycle)):
    if delay_cycle[i][1] == min_delay:
        best_cycle.append(delay_cycle[i][0])
        
for cy in best_cycle:
    lp_optimize(cy, 1)

print('\n')
print(delay_cycle)
print('\n')
print(best_cycle)

end = datetime.datetime.now()
print(end-start)
'''
if __name__ == "__main__":
    lp_optimize(160, 1)