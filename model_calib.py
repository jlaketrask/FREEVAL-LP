import time
import model_check
from numpy import zeros
import matplotlib.pyplot as plt
import gurobipy as gbp
__author__ = 'jltrask'

xrange = range
use_speed_match = True
use_full_res = True

#def zeros(shape):
#    if len(shape) == 2:
#        return [[0 for el in xrange(shape[1])] for el2 in xrange(shape[0])]
#    elif len(shape) == 3:
#        return [[[0 for el in xrange(shape[2])] for el1 in xrange(shape[1])] for el2 in xrange(shape[0])]
#    else:
#        return [0 for el in xrange(shape[0])]


example_problem = 16

# Importing Facility
fd = model_check.extract(example_problem)
def func_KB(i,p):
    return func_SD(i,p) / fd.ffs[i][p] / fd.NL[i][p] #fd.ffs[i][p]
    
def func_SD(i,p):
    return MDv[p] + gbp.quicksum([ONRDv[idx][p] for idx in fd.Ntilde if idx <= i]) - gbp.quicksum([OFRDv[idx][p] for idx in fd.Ftilde if idx < i])
    
def func_L(i):
    return fd.L_mi[min(fd.NS-1, max(i, 0))]

######## Creating Gurobi Model
# Initializing model instance
hcm = gbp.Model("hcm-test")

############################################## Creating Segment Variables ##############################################
SFv = []  # Segment flow out of segment i during step t in interval p
ASF = []  # Maximum Allowable Segment flow (replaces MO2)
KQ = []   # Queue density: vechicle density in the queue on segment i in step t in interval p
NVv = []  # NV in segment i at step t in interval p
UVv = []  # Unserved vehicles: additional # of vehicles stored in segment i at the end of step t in interval p
NV_delta = [] # Variables to minimize the difference between observed and computed NV
UV_delta = [] # Variables to minimize the difference between observed and computed UV
V_delta = [] # Varaibles to minimize the difference between observed and computed speed (V)
Vhr_delta = []
SFv_avg = []
NVv_avg = []
Kv = []  # Segment performance measure density
MDv = [hcm.addVar(vtype=gbp.GRB.CONTINUOUS, lb=1.0, name='MDv_'+str(el_p)) for el_p in xrange(fd.P)]
OFRDv = [] # Off-ramp Demand
ONRDv = [] # On- ramp demand

for el_i in xrange(fd.NS): 
    KQ.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='KQ'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    SFv.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, lb=1.0, name='SF'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    ASF.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ASF'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    NVv.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='NV_'+str(el_i)+'_'+str(el_t-1)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S+1)])
    UVv.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='UV'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    NV_delta.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='NV_delta'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    UV_delta.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='UV_delta'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])   
    SFv_avg.append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='SFv_avg'+str(el_i)+'_'+str(el_p)) for el_p in xrange(fd.P)])
    NVv_avg.append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='NVv_avg'+str(el_i)+'_'+str(el_p)) for el_p in xrange(fd.P)])  
    Kv.append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='Kv'+str(el_i)+'_'+str(el_p)) for el_p in xrange(fd.P)])
    V_delta.append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='V_delta'+str(el_i)+'_'+str(el_p)) for el_p in xrange(fd.P)])
    Vhr_delta.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='Vhr_delta'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    #MDv.append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='MDv'+str(el_i)+'_'+str(el_p)) for el_p in xrange(fd.P)])
    OFRDv.append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='OFRDv'+str(el_i)+'_'+str(el_p)) for el_p in xrange(fd.P)])
    ONRDv.append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRDv'+str(el_i)+'_'+str(el_p)) for el_p in xrange(fd.P)])       
    
###### Creating Expressions for Segment Variables
def SF(i, t, p):
    if t < 0:
        if p == 0:
            return func_SD(max(0,min(i,fd.NS-1)), 0)*(1/fd.Th)
        else:
            return SF(i, fd.S+t, p-1)
    else:
        return SFv[i][t][p]
        
def NV(i, t, p):
    return NVv[i][t+1][p]  # Accounts for t=-1 for initialization

def UV(i, t, p):
    if i < 0:
        return 0.0  # Denied entry is lost
    if p < 0 or (p == 0 and t < 0):
        return 0
    elif t < 0:
        return UV(i, fd.S+t, p-1)
    else:
        return UVv[i][t][p]
        
########################################################################################################################

############################################## Creating Flow Node Variables ############################################
MFv = []    # Actual mainline flow rate in node i during step t in interval p
ONRFv = []  # Actual ONR flow rate that can cross on ramp node i during step t in interval p
ONRQv = []  # Unment demand that is stored as a queu on the ONR roadway at node i during step t in interval p
OFRFv = []  # Actual flow that can exit at OFR node i during step t in interval p
MI = []  # Maximum mainline input: max flow desiring to enter segment i during step t in interval p
MO1v = []  # Max mainline output 1: limited by ONR flow at segment i
MO2v = []  # Max mainline output 2: limited by available storage on segment i due to a downstream queue
MO3v = []  # Max mainline output 3: limited by the presence of qued vech at the upstream in up segment i while the queue clears from the downstream end of segment i
DEF = []    # Deficit in flow at segment i at time step t in interval p
ODEF = []


for el_i in xrange(fd.NS+1):  ## Node variables bookend each segment, thus there are NS+1 nodes
    MFv.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, lb=1.0, name='MF'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    ONRFv.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRF'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    ONRQv.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRQ'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    OFRFv.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='OFRF'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])   
    DEF.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='DEF'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    ODEF.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ODEF'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])    
    MI.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='MI'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    MO1v.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='MO1'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    MO2v.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='MO2'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    MO3v.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='MO3'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])

###### Creating Expressions for Node Variables
def MF(i, t, p):
    if i < 0:
        return MDv[p]*(1/fd.Th)
    elif t <  0:
        if p == 0:
            return func_SD(max(i-1,0), 0)*(1/fd.Th)
        else:
            return MF(i, fd.S+t, p-1)
    else:
        return MFv[i][t][p]

def ONRF(i, t, p):
    if i < 0:
        return 0.0
    elif t<0:
        if p == 0:
            return ONRDv[i][0]/fd.Th
        else:
            return ONRF(i, fd.S+t, p-1)
    else:
        return ONRFv[i][t][p]

def ONRQ(i, t, p):
    if t < 0:
        if p == 0:
            return 0
        else:
            return ONRQ(i, fd.S-1, p-1)
    else:
        return ONRQv[i][t][p]

def OFRF(i, t, p):
    if i < 0:
        return 0.0
    elif t < 0:
        if p == 0:
            return 0
        else:
            return OFRF(i, fd.S+t, p-1)
    else:
        return OFRFv[i][t][p]

def MO1(i, t, p):
    if t < 0:
        if p == 0:
            return fd.SC[max(0,min(fd.NS-1,i))][p]*(1/fd.Th)
        else:
            return MO1(i, fd.S+t, p-1)
    else:
        return MO1v[i][t][p]

def MO2(i, t, p):
    if t < 0:
        if p == 0:
            return fd.SC[max(0,min(fd.NS-1,i))][p]*(1/fd.Th)
        else:
            return MO2(i, fd.S+t, p-1)
    else:
        return MO2v[i][t][p]

def MO3(i, t, p):
    if t < 0:
        if p == 0:
            return fd.SC[max(0,min(fd.NS-1,i))][p]*(1/fd.Th)
        else:
            return MO3(i, fd.S+t, p-1)
    else:
        return MO3v[i][t][p]
        
######################################################################################################################## 

########################################## Creating ONR Node Only Variables ############################################
ONRO = []  # Max output flow rate that can enter the merge point from ONR node i during step t in interval p
ONRI = []  # Input flow rate desiring to enter the merge point at ONR node i during step t in interval p
ONRO_sMax = []
ONRO_sMin = []
for el_i in xrange(len(fd.Ntilde)):
    ONRI.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRI'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    ONRO.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRO'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    ONRO_sMax.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRO_sMax'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    ONRO_sMin.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRO_sMin'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
########################################################################################################################  
    
########################################## Creating OFR Node Only Variables ############################################
########################################################################################################################

# Integrating variables into model
hcm.update()
    
################################################ Capacity Constraints ##################################################    
# SC = fd["SC"]  # Retrieves constant capacities, no cap drop at step level
# Returned variable will always be a known constant
def func_SC(i,t,p):
    if t < 0:
        return func_SC(i, fd.S+t, p-1)
    else:
        return fd.SC[max(0,min(fd.NS-1, i))][max(p,0)]/fd.Th
########################################################################################################################
        
################################################ Front Clearing Queue ################################################## 
# If [SC(i,p)-ONRD(i,p)]>[SC(i,p-1)-ONRD(i,p-1)] && [SC(i,p)-ONRD(i,p)] > SD(i,p)
front_clearing_queue_present = []
for el_i in xrange(fd.NS+1):  # fd.NS+1 to account for final node - no front clearing queue allowed there
    if el_i == fd.NS:
        front_clearing_queue_present.append([False for el_p in xrange(fd.P)])        
    else:
        front_clearing_queue_present.append([])
        for el_p in xrange(fd.P):
            #################################################  FCC #########################################################
            if el_p == 0:
                front_clearing_queue_present[el_i].append(False)
            else:
                isFCC = ((fd.SC[el_i][el_p] - fd.ONRD[el_i][el_p]) > (fd.SC[el_i][el_p-1]-fd.ONRD[el_i][el_p-1])) and (fd.SC[el_i][el_p]-fd.ONRD[el_i][el_p] > fd.SD[el_i][el_p])
                front_clearing_queue_present[el_i].append(False)
########################################################################################################################




  
#######################################             BEGIN MODEL BUILD            #######################################
init_time = time.time()
# Setting objective - Minimize number of vehicles
if use_speed_match:
    big_lambda=70
    if use_full_res:
        #hcm.setObjective(gbp.quicksum(gbp.quicksum(gbp.quicksum(Vhr_delta[el_i][el_t][el_p] + big_lambda * UV(el_i,el_t,el_p) - MDv[el_p] - MF(fd.NS,el_t,el_p) for el_p in xrange(fd.P)) for el_t in xrange(fd.S)) for el_i in xrange(fd.NS)), gbp.GRB.MINIMIZE)  # +gbp.quicksum(CAFv[el_i] for el_i in xrange(fd.NS))
        obj = 0        
        for el_p in xrange(fd.P):        
            obj = obj + MDv[el_p]            
            for el_t in xrange(fd.S):
                obj = obj+MF(fd.NS, el_t, el_p)
                for el_i in xrange(fd.NS):
                    obj = obj - Vhr_delta[el_i][el_t][el_p] - big_lambda*UV(el_i, el_t, el_p)
        hcm.setObjective(obj, gbp.GRB.MAXIMIZE)
                    
    else:
        hcm.setObjective(gbp.quicksum(gbp.quicksum(V_delta[el_i][el_p] for el_p in xrange(fd.P)) for el_i in xrange(fd.NS)), gbp.GRB.MINIMIZE)
else:
    hcm.setObjective(gbp.quicksum(gbp.quicksum(gbp.quicksum(NV_delta[el_i][el_t][el_p]+UV_delta[el_i][el_t][el_p] for el_i in xrange(fd.NS)) for el_t in xrange(fd.S)) for el_p in xrange(fd.P)), gbp.GRB.MINIMIZE)
hcm.update()

###################################################### Init NV #########################################################
#Initialize the Freeway Facility
for el_i in xrange(fd.NS):  # NV is a Segment Quantity
    for el_p in xrange(fd.P):
        hcm.addConstr(NV(el_i, -1, el_p) == func_KB(el_i, el_p) + UV(el_i, fd.S-1, el_p-1),
                      name='NV_Init_'+str(el_i)+str(0)+str(el_p))
print("Init NV done")
########################################################################################################################

########################################## Demand/Flow Convervation ####################################################
# Total Input/Output Conservation
hcm.addConstr(gbp.quicksum(gbp.quicksum(MF(fd.NS, el_t, el_p) + gbp.quicksum(OFRF(el_i, el_t, el_p) for el_i in xrange(fd.NS+1)) for el_t in xrange(fd.S)) for el_p in xrange(fd.P))
                == gbp.quicksum(MDv[el_p] for el_p in xrange(fd.P))/4.0 + gbp.quicksum(gbp.quicksum(ONRDv[el_i][el_p] for el_i in xrange(fd.NS)) for el_p in xrange(fd.P))/4.0,
                name='Demand_Flow_Conservation')
hcm.addConstr(gbp.quicksum(MDv[el_p] for el_p in xrange(fd.P)) >= 34500)

# Off-ramp flow
for el_i in fd.Ftilde:
    hcm.addConstr(gbp.quicksum(OFRDv[el_i][x]/4.0 - gbp.quicksum(OFRF(el_i+1,tau,x) for tau in xrange(fd.S)) for x in xrange(fd.P)) == 0.0)
    #hcm.addConstr(gbp.quicksum(OFRDv[el_i][x] for x in xrange(fd.P)) == sum(fd.OFRD[el_i]))
    hcm.addConstr(gbp.quicksum(OFRDv[el_i][x] for x in xrange(fd.P)) >= 1000)
    #hcm.addConstr(gbp.quicksum(OFRDv[el_i][x] for x in xrange(fd.P)) <= 4000)

# On-Ramp Flow
for el_i in fd.Ntilde:
    hcm.addConstr(gbp.quicksum(ONRDv[el_i][x]/4.0 - gbp.quicksum(ONRF(el_i, tau, x) for tau in xrange(fd.S)) for x in xrange(fd.P)) == 0.0)
    #hcm.addConstr(gbp.quicksum(ONRDv[el_i][x] for x in xrange(fd.P)) == sum(fd.ONRD[el_i]))
    hcm.addConstr(gbp.quicksum(ONRDv[el_i][x] for x in xrange(fd.P)) >= 1000)
    #hcm.addConstr(gbp.quicksum(ONRDv[el_i][x] for x in xrange(fd.P)) <= 2000)

########################################### Begin loop over all nodes #################################################
for el_p in xrange(fd.P):
    for el_t in xrange(fd.S):
        for el_i in xrange(fd.NS+1):
            ########################################### Off-Ramp Flow #################################################
            # Note: OFRF exists at the node at the downstream end of an OFR segment
            # If i is OFR Seg, OFRF is at node i+1 (node at downstream end of segment)
            if el_i-1 in fd.Ftilde:  # Check if OFR at node. If i is OFR Seg, OFRF is at node i+1 (node at downstream end of segment)
                ofr_i = fd.Ftilde.index(el_i-1) # Convert segment idx to ofr var idx (for DEF_I, OFRF_I)
                # Upper bound on OFRF based on increment's OFRD and any deficit in OFRF from previous periods/steps
                lhs_sum1 = gbp.quicksum(OFRDv[el_i-1][x]/4.0 - gbp.quicksum(OFRF(el_i, tau, x) for tau in xrange(fd.S)) for x in xrange(el_p))  # uses el_p and not el_p-1 since xrange is exclusive
                lhs_sum2 = gbp.quicksum(OFRF(el_i, tau, el_p) - OFRDv[el_i-1][el_p]/fd.Th for tau in xrange(el_t)) # uses el_t and not el_t-1 since xrange is exclusive
                hcm.addConstr(ODEF[el_i][el_t][el_p] == lhs_sum1 - lhs_sum2, 
                              name='ODEF_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))                
                hcm.addConstr(OFRF(el_i, el_t, el_p) <= OFRDv[el_i-1][el_p]/fd.Th + ODEF[el_i][el_t][el_p],
                              name='OFRF_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            else:  # The segment is not an offramp
                hcm.addConstr(OFRF(el_i, el_t, el_p) == 0.0, name='OFRF_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(DEF[el_i][el_t][el_p] == 0.0, name='DEF_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            ############################################################################################################

            ######################################## On-Ramp Flow ######################################################
            # Note: ONRF exists at the node at the upstream end of an ONR segment
            if el_i in fd.Ntilde:
                onr_i = fd.Ntilde.index(el_i) # Convert segment idx to onr var idx (for ONRO_A, ONRO_I, ONRF_I)
                #################################### On-Ramp Input #####################################################
                # ONRI = ONRD + ONRQ
                hcm.addConstr(ONRI[onr_i][el_t][el_p] == ONRDv[el_i][el_p]*(1/fd.Th) + ONRQ(el_i, el_t-1, el_p),
                              name='ONRI_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                #################################### On-Ramp Output ####################################################
                # ONRO = min(RM, ONRC, sMax)
                hcm.addConstr(ONRO[onr_i][el_t][el_p] <= fd.RM[el_i][el_p],
                              name='ONRO_MIN_RM'+'_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(ONRO[onr_i][el_t][el_p] <= fd.func_ONRC(el_i, el_t, el_p)/fd.Th,
                              name='ONRO_MIN_ONRC'+'_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(ONRO[onr_i][el_t][el_p] <= ONRO_sMax[onr_i][el_t][el_p],
                              name='ONRO_MIN_sMAX'+'_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                # Sub Minimun: sMin = Min(SC, MF + ONRF, MO3 + ONRF)                            
                hcm.addConstr(ONRO_sMin[onr_i][el_t][el_p] <= func_SC(el_i, el_t, el_p),
                              name='ONRO_sMIN1_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(ONRO_sMin[onr_i][el_t][el_p] <= MF(el_i+1, el_t-1, el_p) + ONRF(el_i, el_t-1, el_p),
                              name='ONRO_sMIN2_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(ONRO_sMin[onr_i][el_t][el_p] <= MO3(el_i, el_t-1, el_p) + ONRF(el_i, el_t-1, el_p),
                              name='ONRO_sMIN3_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                # Sub Maximum: sMax = Max(sMin - MI, sMin/(2*numLanes))
                hcm.addConstr(ONRO_sMax[onr_i][el_t][el_p] >= ONRO_sMin[onr_i][el_t][el_p] - MI[el_i][el_t][el_p],
                              name='ONRO_sMAX1_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(ONRO_sMax[onr_i][el_t][el_p] >= ONRO_sMin[onr_i][el_t][el_p] * (1.0/(2 * fd.NL[el_i][el_p])),
                              name='ONRO_sMAX2_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                #################################### ONRF & ONRQ #####################################################
                # ONRF = min(ONRI, ONRO)
                hcm.addConstr(ONRF(el_i,el_t,el_p) <= ONRI[onr_i][el_t][el_p], name='ONRF_MinI_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(ONRF(el_i,el_t,el_p) <= ONRO[onr_i][el_t][el_p], name='ONRF_MinO_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                # Update ONRQ
                hcm.addConstr(ONRQ(el_i,el_t,el_p) == gbp.quicksum(ONRDv[el_i][x]/4.0 - gbp.quicksum(ONRF(el_i,tau,x) for tau in xrange(fd.S)) for x in xrange(el_p)) + gbp.quicksum(ONRDv[el_i][el_p]/fd.Th - ONRF(el_i,tau,el_p) for tau in xrange(el_t)),
                                       name='ONRQ_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))                
            else: # Segment is not ONR
                hcm.addConstr(ONRF(el_i,el_t,el_p) == 0.0, name='ONRF'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(ONRQ(el_i,el_t,el_p) == 0.0)
            ############################################################################################################

            ####################################### Mainline Input #####################################################
            # Step 9: Calculate Mainline Input
            hcm.addConstr(MI[el_i][el_t][el_p] ==       # Mainline Input at node i equals
                          MF(el_i-1, el_t, el_p)        # Mainline Flow at upstream node plus
                          + ONRF(el_i-1, el_t, el_p)    # ONR Flow at upstream node minus
                          - OFRF(el_i, el_t, el_p)      # OFR flow at current node i
                          + UV(el_i-1, el_t - 1, el_p), # UV of upstream segment at the prev time step
                          name='MI_E'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            ############################################################################################################

            ################################### Mainline Output 1 ######################################################
            # Calculate Mainline Output 1: MO1 = min (SC-ONRF, MO2, MO3)
            hcm.addConstr(MO1(el_i, el_t, el_p) <= func_SC(el_i, el_t, el_p) - ONRF(el_i, el_t, el_p),
                          name='MO1_Min1_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            hcm.addConstr(MO1(el_i, el_t, el_p) <= MO2(el_i, el_t-1, el_p),
                          name='MO1_Min2_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            hcm.addConstr(MO1(el_i, el_t, el_p) <= MO3(el_i, el_t-1, el_p),
                          name='MO1_Min3_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            ############################################################################################################

            #################################### Mainline Output 2 #####################################################
            ########################################### MO2/ASF ########################################################
            # Allowable Segment Flow
            if el_i < fd.NS:  # Not used for final node
                hcm.addConstr(KQ[el_i][el_t][el_p] == fd.KJ*fd.NL[el_i][el_p]- (fd.NL[el_i][el_p]*(fd.KJ-fd.KC))*SF(el_i,el_t-1,el_p)/(fd.SC[el_i][el_p]/fd.Th),
                              name='KQ_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(ASF[el_i][el_t][el_p] == (fd.KJ*fd.NL[el_i][el_p] - (NV(el_i, el_t-1, el_p)+NV(el_i, el_t, el_p))/(2*func_L(el_i)))*(func_SC(el_i, el_t, el_p)/(fd.NL[el_i][el_p]*(fd.KJ-fd.KC))),
                              name='ASF_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(MO2(el_i, el_t, el_p) == ASF[el_i][el_t][el_p] - OFRF(el_i, el_t, el_p),
                              name='MO2_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            else:  # Assume there is no queue downstream of facility end
                hcm.addConstr(MO2(el_i, el_t, el_p) == fd.SC[fd.NS-1][el_p]/fd.Th,
                              name='MO2_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            ############################################################################################################

            ############################################ MO3 ###########################################################
            if front_clearing_queue_present[el_i][el_p] == False:
                # If there is no front clearing queue, this value is set to segment capacity and effectively ignored
                # It is always considered FCC = False at the final downstream node
                hcm.addConstr(MO3(el_i, el_t, el_p) == func_SC(el_i, el_t, el_p), name="MO3_NFCQ"+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            else:
                # MO3(i,t,p) <= MO1(i+1,t-WTT,p) - ONRF(i,t,p)
                # MO3(i,t,p) <= MO2(i+1,t-WTT,p) + OFRF(i+1,t-WTT,p) - ONRF(i,t,p)
                # MO3(i,t,p) <= MO3(i+1,t-WTT,p) + OFRF(i+1,t-WTT,p) - ONRF(i,t,p)
                # MO3(i,t,p) <= SC(i,t-WTT,p) - ONRF(i,t,p)
                # MO3(i,t,p) <= SC(i+1,t-WTT,p) + OFRF(i+1,t-WTT,p) - ONRF(i,t,p)
                hcm.addConstr(MO3(el_i, el_t, el_p) <= MO1(el_i+1, el_t-fd.WTT(el_i, el_p), el_p) - ONRF(el_i, el_t, el_p),
                              name='MO3_m1_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(MO3(el_i, el_t, el_p) <= MO2(el_i+1, el_t-fd.WTT(el_i, el_p), el_p) + OFRF(el_i+1,el_t-fd.WTT(el_i,el_p),el_p) - ONRF(el_i, el_t, el_p),
                              name='MO3_m2_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(MO3(el_i, el_t, el_p) <= MO3(el_i+1, el_t-fd.WTT(el_i, el_p), el_p) + OFRF(el_i+1,el_t-fd.WTT(el_i, el_p),el_p) - ONRF(el_i, el_t, el_p),
                              name='MO3_m3_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(MO3(el_i, el_t, el_p) <= func_SC(el_i, el_t-fd.WTT(el_i, el_p), el_p) - ONRF(el_i, el_t, el_p),
                              name='MO3_m4_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(MO3(el_i, el_t, el_p) <= func_SC(el_i+1, el_t-fd.WTT(el_i, el_p), el_p) + OFRF(el_i+1,el_t-fd.WTT(el_i, el_p),el_p) - ONRF(el_i, el_t, el_p),
                              name='MO3_m5_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            ############################################################################################################

            ###################################### Mainline Flow #######################################################
            #MF(i,t,p) <= MI(i,t,p)
            #MF(i,t,p) <= MO1(i,t,p)
            #MF(i,t,p) <= MO2(i,t,p)
            #MF(i,t,p) <= MO3(i,t,p)
            #MF(i,t,p) <= SC(i,t,p)
            #MF(i,t,p) <= SC(i-1,t,p)
            if (el_i==0):
                hcm.addConstr(MF(el_i, el_t, el_p) == MI[el_i][el_t][el_p], name='MF_m1_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            else:
                hcm.addConstr(MF(el_i, el_t, el_p) <= MI[el_i][el_t][el_p], name='MF_m1_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(MF(el_i, el_t, el_p) <= MO1(el_i, el_t, el_p), name='MF_m2_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(MF(el_i, el_t, el_p) <= MO2(el_i, el_t, el_p), name='MF_m3_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(MF(el_i, el_t, el_p) <= MO3(el_i, el_t, el_p), name='MF_m4_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(MF(el_i, el_t, el_p) <= func_SC(el_i, el_t, el_p), name='MF_m5_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(MF(el_i, el_t, el_p) <= func_SC(el_i-1, el_t, el_p), name='MF_m6_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
########################################################################################################################
print("Node Constraints Added")

################################################ Segment Constraints ###################################################
# Segment flow is equal to the mainline flow plus off-ramp flow of node at downstream end
for el_i in xrange(fd.NS):
    for el_t in xrange(fd.S):
        for el_p in xrange(fd.P):
            ####################################### Max Density ########################################################
            hcm.addConstr(NV(el_i, el_t, el_p) <= fd.KJ*fd.NL[el_i][el_p]*func_L(el_i), 
                          name = 'KJ_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            ####################################### Segment FLow #######################################################
            hcm.addConstr(SF(el_i, el_t, el_p) == MF(el_i+1, el_t, el_p) + OFRF(el_i+1, el_t, el_p),  # i+1 -> uses nodes at downstream end of segment
                          name="3.112"+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            ############################################################################################################
            ###################################### Update NV and UV ####################################################
            # NV(i,t,p) = NV(i,t-1,p) + MF(i,t,p) + ONRF(i,t,p) - MF(i+1,t,p) - OFRF(i+1,t,p)
            # UV(i,t,p) = NV(i,t,p) - [KB(i,t,p)*L(i)]
            ########################################### NV #############################################################
            hcm.addConstr(NV(el_i, el_t, el_p) == NV(el_i, el_t-1, el_p) + MF(el_i, el_t, el_p)
                          + ONRF(el_i, el_t, el_p) - MF(el_i+1, el_t, el_p) - OFRF(el_i+1, el_t, el_p),
                          name="3.113" + str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            ########################################### UV #############################################################
            hcm.addConstr(UV(el_i, el_t, el_p) == MI[el_i+1][el_t][el_p] - MF(el_i+1, el_t, el_p),
                          name="3.114"+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            ######################################## UV Check ##########################################################
            #hcm.addConstr(SF(el_i, el_t, el_p)*func_L(el_i)*fd.Th <= 100.0*NV(el_i, el_t, el_p),
            #              name='Max_Speed_Constr_'+str(el_i)+','+str(el_t)+','+str(el_p))
print("Segment Constraints Added")


############################################ Segment Performance Measures ##############################################
for el_i in xrange(fd.NS):
    for el_p in xrange(fd.P):
        hcm.addConstr(SFv_avg[el_i][el_p] == (fd.Th/fd.S)*gbp.quicksum(SF(el_i,tau,el_p) for tau in xrange(fd.S)),
                      name='SFv_avg_'+str(el_i)+'_'+str(el_p))
        hcm.addConstr(NVv_avg[el_i][el_p] == (1.0/fd.S)*gbp.quicksum(NV(el_i,tau,el_p) for tau in xrange(fd.S)),
                      name='NVv_avg_'+str(el_i)+'_'+str(el_p))
        hcm.addConstr(Kv[el_i][el_p] == NVv_avg[el_i][el_p]/fd.L_mi[el_i],
                      name='Kv_'+str(el_i)+'_'+str(el_p))
        if use_speed_match:
            if use_full_res: # Match Step Level Speeds
                for el_t in xrange(fd.S):
                    #hcm.addConstr(Vhr_delta[el_i][el_t][el_p] >= SF(el_i,el_t,el_p)*func_L(el_i)*fd.Th - fd.Vhr[el_i][el_t][el_p]*NV(el_i,el_t,el_p),
                    #              name='Obj_constr1_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                    #hcm.addConstr(Vhr_delta[el_i][el_t][el_p] >= fd.Vhr[el_i][el_t][el_p]*NV(el_i,el_t,el_p) - SF(el_i,el_t,el_p)*func_L(el_i)*fd.Th,
                    #              name='Obj_constr2_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                    hcm.addConstr(Vhr_delta[el_i][el_t][el_p] >= SF(el_i,el_t,el_p)*func_L(el_i)*fd.Th - fd.V[el_i][el_p]*NV(el_i,el_t,el_p),
                                  name='Obj_constr1_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                    hcm.addConstr(Vhr_delta[el_i][el_t][el_p] >= fd.V[el_i][el_p]*NV(el_i,el_t,el_p) - SF(el_i,el_t,el_p)*func_L(el_i)*fd.Th,
                                  name='Obj_constr2_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            else:  # Match Period Level Speeds
                hcm.addConstr(V_delta[el_i][el_p] >= SFv_avg[el_i][el_p] - fd.V[el_i][el_p]*Kv[el_i][el_p],
                            name='Obj_Constr1_'+str(el_i)+'_'+str(el_p))
                hcm.addConstr(V_delta[el_i][el_p] >= fd.V[el_i][el_p]*Kv[el_i][el_p] -SFv_avg[el_i][el_p],
                            name='Obj_Constr2_'+str(el_i)+'_'+str(el_p))
        else:
            for el_t in xrange(fd.S):
                hcm.addConstr(NV_delta[el_i][el_t][el_p] >= NV(el_i, el_t, el_p) - fd.fNV[el_i][el_t][el_p],
                              name='Obj_Constr1_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(NV_delta[el_i][el_t][el_p] >= fd.fNV[el_i][el_t][el_p] - NV(el_i, el_t, el_p),
                              name='Obj_Constr2_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(UV_delta[el_i][el_t][el_p] >= UV(el_i, el_t, el_p) - fd.fUV[el_i][el_t][el_p],
                              name='Obj_Constr3_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(UV_delta[el_i][el_t][el_p] >= fd.fUV[el_i][el_t][el_p] - UV(el_i, el_t, el_p),
                              name='Obj_Constr4_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
print("Segment Perforamance Measure Constraints Added")    
########################################################################################################################

hcm.update()
model_build_time=time.time()
print("Model Built: "+str(model_build_time - init_time))
#hcm.setParam(gbp.GRB.param.ConcurrentMIP, 32)
#hcm.setParam(gbp.GRB.param.SubMIPNodes, 5000000)
#hcm.update()
#hcm.presolve()
#hcm.computeIIS()
#hcm.write('mod2_mc1_full.ilp')
hcm.optimize()
optimize_finish_time = time.time()
print("Model Solved: "+str(optimize_finish_time - model_build_time))

f=open('gpex1_ht_out.csv','w')
f.write('Segment, Period, Step, NV, MF, MI, MO1, MO2, MO3, ONRF, OFRF, DEF, UV, SF, KQ, ASF\n')
varCount = 0
for p in xrange(fd.P):
    for t in xrange(fd.S):
        for i in xrange(fd.NS):
            varCount+=1
            #s = str(varCount)
            s = str(i)
            s += ", " + str(p)
            s += ", " + str(t)
            s += ", " + str(NV(i, t, p).X)
            s += ", " + str(MF(i+1, t, p).X)
            s += ", " + str(MI[i+1][t][p].X)
            s += ", " + str(MO1(i+1, t, p).X)
            s += ", " + str(MO2(i+1, t, p).X)
            s += ", " + str(MO3(i+1, t, p).X)
            s += ", " + str(ONRF(i,t, p).X)
            #s+= ", " + str(ONRQ(i,t, p).X)
            s += ", " + str(OFRF(i+1,t, p).X)
            s += ", " + str(DEF[i+1][t][p].X)
            s+= ", " + str(UV(i,t,p).X)
            s+=", " + str(SF(i, t, p).X)
            s+=", " + str(KQ[i][t][p].X)
            s+=", " + str(ASF[i][t][p].X)
            f.write(s +'\n')
            #print(s)
f.close()

# Computing Performance Measures
segFlow = zeros((fd.NS, fd.P))
numVeh = zeros((fd.NS,fd.P))
K = zeros((fd.NS,fd.P))
U = zeros((fd.NS,fd.P))
recalc_V = zeros((fd.NS, fd.P))
print("\nSPEED DIFFERENCES")
boxes1 = [0 for el in xrange(fd.NS)]
boxes5 = [0 for el in xrange(fd.NS)]
boxes10 = [0 for el in xrange(fd.NS)]
for p in xrange(fd.P):
    for i in xrange(fd.NS):
        if abs(U[i][p] - recalc_V[i][p]) > 1:
                    boxes1[i]+=1
                    if abs(U[i][p] - recalc_V[i][p]) > 5:
                        boxes5[i]+=1   
                        if abs(U[i][p] - recalc_V[i][p]) > 10:
                            boxes10[i]+=1
                            
x = [el for el in xrange(fd.NS)]
fig = plt.figure(1)
plt.plot(x, boxes1, figure = fig, label='box1')
plt.plot(x, boxes5, figure = fig, label='box5')
plt.plot(x, boxes10, figure = fig, label='box10')
plt.legend(loc=2)
#plt.savefig('abs_err_i40.png')
plt.show()


for p in xrange(fd.P):
    for i in xrange(fd.NS):
        segFlow[i][p] = (fd.Th/fd.S)*sum([SF(i,tau,p).X for tau in xrange(fd.S)])
        numVeh[i][p] = (1.0/fd.S)*sum([NV(i,tau,p).X for tau in xrange(fd.S)])
        K[i][p] = numVeh[i][p]/fd.L_mi[i]
        U[i][p] = segFlow[i][p]/K[i][p]
        #temp_segFlow=(fd.Th/fd.S)*sum([fd.fSF[i][tau][p] for tau in xrange(fd.S)])
        #temp_numVeh = (1.0/fd.S)*sum([fd.fNV[i][tau][p] for tau in xrange(fd.S)])
        #recalc_V[i][p]=temp_segFlow/(temp_numVeh/fd.L_mi[i])
        recalc_V[i][p] = fd.V[i][p]
        print(str(i)+','+str(p)+','+"{0:.2f}".format(U[i][p])+','+"{0:.2f}".format(recalc_V[i][p])+','+"{0:.2f}".format(U[i][p]-recalc_V[i][p])) # +','+"{0:.2f}".format(KBv[i][p].X)+','+"{0:.2f}".format(CAFv[i].X)
        