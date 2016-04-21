import time
import model_check
#from numpy import zeros
import gurobipy as gbp
__author__ = 'jltrask'

xrange = range
use_speed_match = True
use_known_kb = True
use_known_ofrd = True
use_full_res = True
use_classic_mo2 = False
use_dta_obj = False

example_problem = 6

def zeros(shape):
    if len(shape) == 2:
        return [[0 for el in xrange(shape[1])] for el2 in xrange(shape[0])]
    elif len(shape) == 3:
        return [[[0 for el in xrange(shape[2])] for el1 in xrange(shape[1])] for el2 in xrange(shape[0])]
    else:
        return [0 for el in xrange(shape[0])]

init_time = time.time()

# Importing Facility
fd = model_check.extract(example_problem)

if use_known_kb:
    def func_KB(i,p):
        return fd.KB[i][p]
else:
    def func_KB(i,p):
        return KBv[i][p] 

def func_L(i):
    return fd.L_mi[min(fd.NS-1, max(i, 0))]

# (2) Wave Trave Time and Wave Speed


######## Creating Gurobi Model
# Initializing model instance
hcm = gbp.Model("hcm-test")

############################################## Creating Segment Variables ##############################################
SFv = []  # Segment flow out of segment i during step t in interval p
ASF = []
KQ = []   # Queue density: vechicle density in the queue on segment i in step t in interval p
KBv = []  # Decision variable for background density
NVv = []  # NV in segment i at step t in interval p
UVv = []  # Unserved vehicles: additional # of vehicles stored in segment i at the end of step t in interval p
NV_delta = [] # Variables to minimize the difference between observed and computed NV
UV_delta = [] # Variables to minimize the difference between observed and computed UV
V_delta = [] # Varaibles to minimize the difference between observed and computed speed (V)
Vhr_delta = []
SFv_avg = []
NVv_avg = []
Kv = []  # Segment performance measure density


for el_i in xrange(fd.NS): 
    KQ.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='KQ'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    SFv.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='SF'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    ASF.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ASF'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    NVv.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='NV'+str(el_i)+str(el_t-1)+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S+1)])
    UVv.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='UV'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    NV_delta.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='NV_delta'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    UV_delta.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='UV_delta'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    KBv.append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS, lb=fd.KC, name='KB_'+str(el_i)+'_'+str(el_p)) for el_p in xrange(fd.P)])    
    SFv_avg.append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='SFv_avg'+str(el_i)+'_'+str(el_p)) for el_p in xrange(fd.P)])
    NVv_avg.append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='NVv_avg'+str(el_i)+'_'+str(el_p)) for el_p in xrange(fd.P)])  
    Kv.append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='Kv'+str(el_i)+'_'+str(el_p)) for el_p in xrange(fd.P)])      
    V_delta.append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='V_delta'+str(el_i)+'_'+str(el_p)) for el_p in xrange(fd.P)])
    Vhr_delta.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='Vhr_delta'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    
################################ Unserved Vehicles Indicator ###################################
I_UVv = [] # Array to hold binary indicator
for el_i in xrange(fd.NS):  # Segment Variable
    I_UVv.append([])
    for el_t in xrange(fd.S):
        I_UVv[el_i].append([])
        for el_p in xrange(fd.P):
            I_UVv[el_i][el_t].append(hcm.addVar(vtype=gbp.GRB.BINARY, name="I_UV"+str(el_i)+'_'+str(el_t)+'_'+str(el_p)))
    
###### Creating Expressions for Segment Variables
def SF(i, t, p):
    if t < 0:
        if p == 0:
            return min(fd.SD[max(i-1,0)][0],fd.SC[max(i-1,0)][0])*(1/fd.Th)
        else:
            return SFv[i][fd.S+t][p-1]
    else:
        return SFv[i][t][p]
        
def NV(i, t, p):
    return NVv[i][t+1][p]  # t=-1 from MO2 accounted for

def UV(i, t, p):
    if i < 0:
        return 0.0  # Denied entry is lost
    if p < 0 or (p == 0 and t < 0):
        return 0
    elif t < 0:
        return UV(i, fd.S+t, p-1)  #UVv[i][S+t][p-1]
    else:
        return UVv[i][t][p]

def I_UV(i, t, p):
    if p < 0 or (p == 0 and t < 0):
        return 0
    elif t < 0:
        return I_UV(i, fd.S+t, p-1)
    else:
        return I_UVv[i][t][p]
        
########################################################################################################################

############################################## Creating Flow Node Variables ############################################
MFv = []    # Actual mainline flow rate in node i during step t in interval p
ONRFv = []  # Actual ONR flow rate that can cross on ramp node i during step t in interval p
ONRQv = []  # Unment demand that is stored as a queu on the ONR roadway at node i during step t in interval p
OFRFv = []  # Actual flow that can exit at OFR node i during step t in interval p
if use_known_ofrd == False:
    OFRD = []   # Off-ramp Demand variable
MI = []  # Maximum mainline input: max flow desiring to enter segment i during step t in interval p
MO1v = []  # Max mainline output 1: limited by ONR flow at segment i
MO2v = []  # Max mainline output 2: limited by available storage on segment i due to a downstream queue
MO3v = []  # Max mainline output 3: limited by the presence of qued vech at the upstream in up segment i while the queue clears from the downstream end of segment i
DEF = []    # Deficit in flow at segment i at time step t in interval p
DEF_A = []  # Auxiliary Variable to hold the Deficit as it is determined by Min function
DEF_I = []  # Binary variable used to indicate the presence of a mainline deficit


for el_i in xrange(fd.NS+1):  ## Node variables bookend each segment, thus there are NS+1 nodes
    MFv.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='MF'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    ONRFv.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRF'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    ONRQv.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRQ'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    OFRFv.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='OFRF'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    if use_known_ofrd == False:    
        OFRD.append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='OFRD'+str(el_i)+'_'+str(el_p)) for el_p in xrange(fd.P)])    
    DEF.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='DEF'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    DEF_A.append([[hcm.addVar(lb=-1*gbp.GRB.INFINITY, ub=gbp.GRB.INFINITY, vtype=gbp.GRB.CONTINUOUS, name='DEF'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    DEF_I.append([[hcm.addVar(vtype=gbp.GRB.BINARY, name='DEF_I'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])    
    MI.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='MI'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    MO1v.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='MO1'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    MO2v.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='MO2'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])
    MO3v.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='MO3'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_p in xrange(fd.P)] for el_t in xrange(fd.S)])

###### Creating Expressions for Node Variables
def MF(i, t, p):
    if i < 0:
        return min(fd.mainline_demand[p],fd.SC[0][p])*(1/fd.Th)
    elif t <  0:
        if p == 0:
            return min(fd.SD[max(i-1,0)][0],fd.SC[i][p])*(1/fd.Th)  ## Feasibility issue?
        else:
            return MFv[i][fd.S+t][p-1]
    else:
        return MFv[i][t][p]

def ONRF(i, t, p):
    if i < 0:
        return 0.0
    elif t<0:
        if p == 0:
            return fd.ONRD[i][0]/fd.Th
        else:
            return ONRFv[i][fd.S+t][p-1]
    else:
        return ONRFv[i][t][p]

def ONRQ(i, t, p):
    if t < 0:
        if p == 0:
            return 0
        else:
            return ONRQv[i][fd.S-1][p-1]
    else:
        return ONRQv[i][t][p]

def OFRF(i, t, p):
    if i < 0:
        return 0.0
    elif t < 0:
        if p == 0:
            return 0
        else:
            return OFRFv[i][fd.S+t][p-1]
    else:
        return OFRFv[i][t][p]

def MO1(i, t, p):
    if t < 0:
        if p == 0:
            return fd.SC[i][p]*(1/fd.Th)
        else:
            return MO1v[i][fd.S+t][p-1]
    else:
        return MO1v[i][t][p]

def MO2(i, t, p):
    if t < 0:
        if p == 0:
            return fd.SC[i][p]*(1/fd.Th)
        else:
            return MO2v[i][fd.S+t][p-1]
    else:
        return MO2v[i][t][p]

def MO3(i, t, p):
    if t < 0:
        if p == 0:
            return fd.SC[i][p]*(1/fd.Th)
        else:
            return MO3v[i][fd.S+t][p-1]
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
# Need to address depending on case
# Case 1: Capacities fully known
# Case 2: Calibration of CAF factors, underlying capacities known  
# Case 3: Capacities partially known, use capacity drop (bottlenecks only?)  # NOT READY
# Case 4: Capacities unknown, are decision variables. # NOT READY
capacity_var_case = 1;
########################################################################################################################
################################################## Capacity Case 1 #####################################################
# Base Case
if capacity_var_case == 1:
    # SC = fd["SC"]  # Retrieves constant capacities, no cap drop at step level
    # Returned variable will always be a known constant
    def func_SC(i,t,p):
        if t < 0:
            return func_SC(i, fd.S+t, p-1)
        else:
            return fd.SC[max(0,min(fd.NS-1, i))][max(p,0)]/fd.Th
########################################################################################################################
################################################## Capacity Case 2 #####################################################
# Assumes underlying capacities are known.  Uses CAF variables.
elif capacity_var_case == 2:
    # SC = fd["SC"]  # Retrieves constant capacities, no cap drop at step level
    CAFv = []  # Capacity Adjustment Factors
    for el_i in xrange(fd.NS): # CAF and Capacity are segment variables
        # CAF varies by segment only
        CAFv.append(hcm.addVar(vtype=gbp.GRB.CONTINUOUS, ub = 2.0, lb=0.5, name='CAFv_'+str(el_i)))
        # CAF varies by segment and period
        #CAFv.append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS, ub = 2.0, lb=0.5, name='CAFv_'+str(el_i)+'_'+str(el_p)) for el_p in xrange(fd.P)])
        # CAF Varies by segment, period, and step (can compute capacity drop)
        #CAFv.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, ub = 2.0, lb=0.5, name='CAFv_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) for el_t in xrange(fd.S)] for el_p in xrange(fd.P)])
    hcm.update()
    def func_SC(i,t,p):
        if t < 0:
            return func_SC(i, fd.S+t, p-1)
        else:
            i = max(0,min(fd.NS-1,i))  # To maintain 0<=i<=NS-1 indexing
            p = max(p,0)            
            tempVar = CAFv[i]*fd.SC[i][p]
            #tempVar = CAFv[i][p]*SC[i][p]
            #tempVar = CAFv[i][t][p]*SC[i][p]
            return tempVar/fd.Th
########################################################################################################################
################################################## Capacity Case 3 #####################################################
elif capacity_var_case == 3:
    # NOT READY FOR USE
    # Creating segment capacity decision variables
    # SC cannot change at the step level (capacity drop can take effect though)
    SCv = [] # Capacity of a segment, allows for capacity drop to take effect
    for el_i in xrange(fd.NS):
        SCv.append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='SCv'+str(el_i)+'_'+str(el_p)) for el_p in xrange(fd.P)])
    def func_SC(i, t, p):
        if t < 0:
            return func_SC(i, S+t, p-1)
        if i < 0:
            return SCv[0][p]/fd.Th
        else:
            return SCv[max(0,min(fd.NS-1, i))][max(p,0)]/fd.Th
    # Assumes underlying capacities are konwn, but allows capacity drop to be
    # applied when there are unserved vehicles.
    # NEED TO CHECK LOCATION WHERE ALPHA IS USED, BOTTLENECK ONLY OR ALL SEGMENTS
    # WITH UNSERVED VEHICLES.
    for el_i in xrange(fd.NS):  # UV and I_UV are segment quantities
        for el_t in xrange(fd.S):
            for (el_p) in xrange(fd.P):
                ########################################### SC*Alpha #############################################################
                if el_i > 0:
                    hcm.addConstr(func_SC(el_i, el_t, el_p) == (1.0 - I_UV(el_i-1, el_t-1, el_p)*fd.alpha) * (fd.SC[el_i][el_p]/fd.Th),
                                  name='SC_E'+str(el_i)+str(el_t)+str(el_p))
                else:
                    hcm.addConstr(func_SC(el_i, el_t, el_p) == fd.SC[el_i][el_p]/fd.Th,
                                  name='SC_E'+str(el_i)+str(el_t)+str(el_p))
########################################################################################################################
################################################## Capacity Case 4 #####################################################
# Assumes capacities are unknown.  SCv is used as a decision variable.
# Need to account for capacity drop in some way.
elif capacity_Var_case == 4:
    # Creating segment capacity decision variables
    # SC cannot change at the step level (capacity drop can take effect though)
    SCv = [] # Capacity of a segment, allows for capacity drop to take effect
    for el_i in xrange(fd.NS):
        SCv.append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='SCv'+str(el_i)+'_'+str(el_p)) for el_p in xrange(fd.P)])
    def func_SC(i,t,p):
        if t < 0:
            return func_SC(i,S+t,p-1)
        else:
            return SCv[max(0,min(fd.NS-1, i))][max(p,0)]/fd.Th
########################################################################################################################


  
#######################################             BEGIN MODEL BUILD            #######################################

# Setting objective
if use_dta_obj is False:
    if use_full_res:
        hcm.setObjective(gbp.quicksum(gbp.quicksum(gbp.quicksum(Vhr_delta[el_i][el_t][el_p] for el_p in xrange(fd.P)) for el_t in xrange(fd.S)) for el_i in xrange(fd.NS)), gbp.GRB.MINIMIZE)  # +gbp.quicksum(CAFv[el_i] for el_i in xrange(fd.NS))
    else:
        hcm.setObjective(gbp.quicksum(gbp.quicksum(V_delta[el_i][el_p] for el_p in xrange(fd.P)) for el_i in xrange(fd.NS)), gbp.GRB.MINIMIZE)
else:
    hcm.setObjective(gbp.quicksum(gbp.quicksum((MF(el_i, el_t, el_p)+ONRF(el_i,el_t,el_p)+OFRF(el_i,el_t,el_p))*(1-(el_p*fd.S+el_t)/(fd.P*fd.S)) for el_p in xrange(fd.P)) for el_i in xrange(fd.NS)),
                                               gbp.GRB.MAXIMIZE)

hcm.update()

###################################################### Init NV #########################################################
# Step 1: ED is based on KB - Which is a constant for now.
# Step 2: initialize the Freeway Facility
# Updating # of vehicles - note t goes from 0 to S (inclusive so S+1 steps) for NV, with 0 being  "before" interval p starts.
for el_i in xrange(fd.NS):  # NV is a Segment Quantity
    for el_p in xrange(fd.P):  # Note that the lambda function on UV accounts for the case p = -1 (UV = 0 in that case)
        hcm.addConstr(NV(el_i, -1, el_p) == func_KB(el_i, el_p)*func_L(el_i) + UV(el_i, fd.S-1, el_p-1),
                      name='NV_E'+str(el_i)+str(0)+str(el_p))
print("Init NV done")
########################################################################################################################


# Steps 3-4: Begin "loops" of all segments, all time steps
# Steps 5-8: OFR Segment constraints
################################################### Off-Ramp Flow ######################################################
# Note: OFRF exists at the node at the downstream end of an OFR segment
# If i is OFR Seg, OFRF is at node i+1 (node at downstream end of segment)
big_m = sum([sum(fd.SD[el]) for el in xrange(len(fd.SD))])  # TODO calculate more exact bound on what the deficit can be in each period?
def_zero_tol = 0.01 # From vba_code.txt line 218
for el_i in xrange(fd.NS+1):
    if el_i-1 in fd.Ftilde:  # Check if OFR at node. If i is OFR Seg, OFRF is at node i+1 (node at downstream end of segment)
        hcm.addConstr(gbp.quicksum(fd.OFRD[el_i-1][x]/4.0 - gbp.quicksum(OFRF(el_i,tau,x) for tau in xrange(fd.S)) for x in xrange(fd.P)) == 0.0)        
        ofr_i = fd.Ftilde.index(el_i-1) # Convert segment idx to ofr var idx (for DEF_I, OFRF_I)
        for el_p in xrange(fd.P):
            for el_t in xrange(fd.S):                                
                # Upper bound on OFRF based on increment's OFRD and any deficit in OFRF from previous periods/steps
                lhs_sum1 = gbp.quicksum(fd.OFRD[el_i-1][x]/4.0 - gbp.quicksum(OFRF(el_i, tau, x) for tau in xrange(fd.S)) for x in xrange(el_p))  # uses el_p and not el_p-1 since xrange is exclusive
                lhs_sum2 = gbp.quicksum(OFRF(el_i, tau, el_p) - fd.OFRD[el_i-1][el_p]/fd.Th for tau in xrange(el_t)) # uses el_t and not el_t-1 since xrange is exclusive
                hcm.addConstr(OFRF(el_i, el_t, el_p) - fd.OFRD[el_i-1][el_p]/fd.Th - lhs_sum1 + lhs_sum2 <= 0.0)
                
                # Adding lower bound constraint if there is no deficit.
#                hcm.addConstr(OFRF(el_i, el_t, el_p) - OFRD[el_i-1][el_p]/Th >= -1.0*big_m*DEF_I[ofr_i][el_t][el_p])
#                
#                # Computing Mainline Flow Deficit (Altered version of HCM's Deficit Equation)                
#                if el_t == 0:
#                    # Deficit sum for first step
#                    def_sum = gbp.quicksum(SD[el_i-1][x]/4.0 -gbp.quicksum(MF(el_i-1, tau , x) + ONRF(el_i-1, tau, x) for tau in xrange(fd.S)) for x in xrange(el_p))
#                    hcm.addConstr(DEF_A[el_i][el_t][el_p] == def_sum, name="DEF_TEMP_A"+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
#                else:
#                    hcm.addConstr(DEF_A[el_i][el_t][el_p] == DEF_A[el_i][el_t-1][el_p] + SD[el_i-1][el_p]/Th - MF(el_i-1, el_t-1, el_p) - ONRF(el_i-1, el_t-1, el_p),
#                                  name="DEF_TEMP_A"+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
#                #### Setting DEF to be max of DEF_A and 0
#                # Checking to see if DEF_A is greater than 0
#                hcm.addConstr(DEF_A[el_i][el_t][el_p] - def_zero_tol
#                              <= big_m * DEF_I[ofr_i][el_t][el_p],
#                          name='DEF_E1'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) # DEF_I=1 => DEF_A>0
#                hcm.addConstr(def_zero_tol-DEF_A[el_i][el_t][el_p]
#                              <= big_m * (1 - DEF_I[ofr_i][el_t][el_p]),
#                          name='DEF_E2'+str(el_i)+'_'+str(el_t)+'_'+str(el_p)) # DEF_I=0 => DEF_A<=0
#                # Setting DEF to be a1 (when DEF_I=1)
#                hcm.addConstr(DEF[el_i][el_t][el_p] - DEF_A[el_i][el_t][el_p]
#                              <= big_m * (1 - DEF_I[ofr_i][el_t][el_p]),
#                          name='DEF_E3'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
#                hcm.addConstr(DEF[el_i][el_t][el_p] - DEF_A[el_i][el_t][el_p]
#                              >= -1*big_m * (1 - DEF_I[ofr_i][el_t][el_p]),
#                          name='DEF_E4'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
#                # Setting DEF to be 0 (when DEF_A<=0)
#                hcm.addConstr(DEF[el_i][el_t][el_p]
#                              <= big_m*DEF_I[ofr_i][el_t][el_p],
#                          name='DEF_E5'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
#                hcm.addConstr(DEF[el_i][el_t][el_p]
#                              >= -1*big_m*DEF_I[ofr_i][el_t][el_p],
#                          name='DEF_E6'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            ##################################################################

    else:  # The segment is not an offramp
        for el_t in xrange(fd.S):
            for el_p in xrange(fd.P):
                hcm.addConstr(OFRF(el_i, el_t, el_p) == 0.0, name='OFRF_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(DEF[el_i][el_t][el_p] == 0.0, name='DEF_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
print("OFRF done")
########################################################################################################################

#################################################### On-Ramp Flow ######################################################
# Note: ONRF exists at the node at the upstream end of an ONR segment
for el_i in xrange(fd.NS+1):
    if el_i in fd.Ntilde:
        onr_i = fd.Ntilde.index(el_i) # Convert segment idx to onr var idx (for ONRO_A, ONRO_I, ONRF_I)
        for el_t in xrange(fd.S):
            for el_p in xrange(fd.P):
                #################################### On-Ramp Input #####################################################
                hcm.addConstr(ONRI[onr_i][el_t][el_p] ==  # ONRI at node i equals
                              fd.ONRD[el_i][el_p]*(1/fd.Th)     # ONR demand at segment i (ONRF is computed for node at upstream end of ONR segment)
                              + ONRQ(el_i, el_t-1, el_p),   # Queued vehicles on ONR at the previous step (t-1=-1 case implemented in function def)
                              name='ONRI_E'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                #################################### On-Ramp Output ####################################################
                # a1 = min of MO3 & MF
                # a2 = min of a1+ONRF & SC
                # a3 = max of a2-MI & a2/(2N)
                # a4 = min of a3 & ONRC
                # a5 = min of a4 & RM
                # inequalities to approximate min/max functions
                hcm.addConstr(ONRO[onr_i][el_t][el_p] <= fd.RM[el_i][el_p],
                              name='ONRO_MIN_RM'+'_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(ONRO[onr_i][el_t][el_p] <= fd.func_ONRC(el_i, el_t, el_p),
                              name='ONRO_MIN_ONRC'+'_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(ONRO[onr_i][el_t][el_p] <= ONRO_sMax[onr_i][el_t][el_p],
                              name='ONRO_MIN_sMAX'+'_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))

                # Sub Minimum                              
                hcm.addConstr(ONRO_sMin[onr_i][el_t][el_p] <= func_SC(el_i, el_t, el_p))
                hcm.addConstr(ONRO_sMin[onr_i][el_t][el_p] <= MF(el_i+1, el_t-1, el_p) + ONRF(el_i, el_t-1, el_p))
                hcm.addConstr(ONRO_sMin[onr_i][el_t][el_p] <= MO3(el_i, el_t-1, el_p) + ONRF(el_i, el_t-1, el_p))
                
                # Sub Maximum
                hcm.addConstr(ONRO_sMax[onr_i][el_t][el_p] >= ONRO_sMin[onr_i][el_t][el_p] - MI[el_i][el_t][el_p])
                hcm.addConstr(ONRO_sMax[onr_i][el_t][el_p] >= ONRO_sMin[onr_i][el_t][el_p] * (1.0/(2 * fd.NL[el_i][el_p])))
                
                #################################### ONRF & ONRQ #####################################################
                # ONRF = min(ONRI, ONRO)
                hcm.addConstr(ONRF(el_i,el_t,el_p) <= ONRI[onr_i][el_t][el_p], name='ONRF_MinI_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(ONRF(el_i,el_t,el_p) <= ONRO[onr_i][el_t][el_p], name='ONRF_MinO_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                
                # Update ONRQ
                #hcm.addConstr(ONRQ(el_i,el_t,el_p) >= 0.0, name='ONRQ_Min1_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                #hcm.addConstr(ONRQ(el_i,el_t,el_p) >= ONRQ(el_i,el_t-1,el_p)+ONRI[onr_i][el_t][el_p] - ONRO[onr_i][el_t][el_p], name='ONRQ_Min2_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(ONRQ(el_i,el_t,el_p) 
                            ==gbp.quicksum(fd.ONRD[el_i][x]/4.0 - gbp.quicksum(ONRF(el_i,tau,x) for tau in xrange(fd.S)) for x in xrange(el_p))
                            + gbp.quicksum(fd.ONRD[el_i][el_p]/fd.Th - ONRF(el_i,tau,el_p) for tau in xrange(el_t)),
                                       name='ONRQ_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))                
                
    # Segment is not ONR
    else:
        for el_t in xrange(fd.S):
            for el_p in xrange(fd.P):
                hcm.addConstr(ONRF(el_i,el_t,el_p) == 0.0, name='ONRF'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(ONRQ(el_i,el_t,el_p) == 0.0)
print("ONRF Done")
########################################################################################################################

################################################### Mainline Input #####################################################
# Step 9: Calculate Mainline Input
for el_i in xrange(fd.NS+1):                               # 
    for el_t in xrange(fd.S):
        for el_p in xrange(fd.P):
            hcm.addConstr(MI[el_i][el_t][el_p] ==       # Mainline Input at node i equals
                          MF(el_i-1, el_t, el_p)        # Mainline Flow at upstream node plus
                          + ONRF(el_i-1, el_t, el_p)    # ONR Flow at upstream node minus
                          - OFRF(el_i, el_t, el_p)      # OFR flow at current node i
                          + UV(el_i-1, el_t - 1, el_p), # UV of upstream segment at the prev time step
                          name='MI_E'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
print("MI done")
########################################################################################################################

############################################### Mainline Output 1 ######################################################
for el_i in xrange(fd.NS):
    for el_t in xrange(fd.S):
        for el_p in xrange(fd.P):
                # Step 16: Calculate Mainline Output (1)
                # inequalities to approximate min functions - not likely to work
                hcm.addConstr(MO1(el_i, el_t, el_p) <= func_SC(el_i, el_t, el_p) - ONRF(el_i, el_t, el_p),
                              name='MO1_Min1_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(MO1(el_i, el_t, el_p) <= MO2(el_i,el_t-1, el_p),
                              name='MO1_Min2_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(MO1(el_i, el_t, el_p) <= MO3(el_i,el_t-1, el_p),
                              name='MO1_Min3_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
for el_t in xrange(fd.S):
    for el_p in xrange(fd.P):
        hcm.addConstr(MO1(fd.NS,el_t, el_p) == fd.SC[fd.NS-1][el_p]*(1/fd.Th),
                      name='MO1_'+str(fd.NS)+'_'+str(el_t)+'_'+str(el_p))
print("MO1 done")
########################################################################################################################

################################################ Mainline Output 2 #####################################################
# Step 20: Calculate density of queue on segment
for el_i in xrange(fd.NS):  # KQ is a segment quantity
    for el_t in xrange(fd.S):  # Todo account for "t-1"
        for el_p in xrange(fd.P):
            ########################################### KQ  ###########################################################
            hcm.addConstr(KQ[el_i][el_t][el_p] == fd.KJ*fd.NL[el_i][el_p]- (fd.NL[el_i][el_p]*(fd.KJ-fd.KC))*SF(el_i,el_t-1,el_p)/(fd.SC[el_i][el_p]/fd.Th),
                          name='KQ_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))

            ########################################### MO2 ###########################################################
            # Original Single Equation            
            #hcm.addConstr(MO2(el_i, el_t, el_p) == SF(el_i, el_t-1, el_p) - ONRF(el_i, el_t, el_p) + KQ[el_i][el_t][el_p]*fd.L_mi[el_i] - NV(el_i, el_t-1, el_p),
            #              name='MO2_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            if use_classic_mo2 is True:
                # Using I_UV            
                hcm.addConstr(MO2(el_i, el_t, el_p) - SF(el_i, el_t-1, el_p) + ONRF(el_i, el_t, el_p) - KQ[el_i][el_t][el_p]*fd.L_mi[el_i] + NV(el_i, el_t-1, el_p) <= big_m*(1-I_UV(el_i, el_t-1, el_p)),
                              name='MO2_C1_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(SF(el_i, el_t-1, el_p) - ONRF(el_i, el_t, el_p) + KQ[el_i][el_t][el_p]*fd.L_mi[el_i] - NV(el_i, el_t-1, el_p) - MO2(el_i, el_t, el_p) <= big_m*(1-I_UV(el_i, el_t-1, el_p)),
                              name='MO2_C2_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            else:
                # Using Allowable Segment Flow
                hcm.addConstr(NV(el_i, el_t, el_p) <= fd.KJ*fd.NL[el_i][el_p]*func_L(el_i),
                              name = 'KJ_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                hcm.addConstr(ASF[el_i][el_t][el_p] == (fd.KJ*fd.NL[el_i][el_p] - (NV(el_i, el_t-1, el_p)+NV(el_i, el_t, el_p))/(2*func_L(el_i)))*(func_SC(el_i, el_t, el_p)/(fd.NL[el_i][el_p]*(fd.KJ-fd.KC))),
                              name='ASF_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                if (el_i > 0): # Not used at first node
                    hcm.addConstr(MO2(el_i, el_t, el_p) == ASF[el_i][el_t][el_p] - OFRF(el_i, el_t, el_p),
                                  name='MO2_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
for el_t in xrange(fd.S):
    for el_p in xrange(fd.P):
        hcm.addConstr(MO2(fd.NS,el_t, el_p) == fd.SC[fd.NS-1][el_p]*(1/fd.Th),
                      name='MO2_'+str(fd.NS)+'_'+str(el_t)+'_'+str(el_p))
print("MO2 and KQ done")
########################################################################################################################

###################################################### MO3 and FCC ######################################################
# Check for Front Clearing Queue
# If [SC(i,p)-ONRD(i,p)]>[SC(i,p-1)-ONRD(i,p-1)] && [SC(i,p)-ONRD(i,p)] > SD(i,p)
front_clearing_queue_present = []
for el_i in xrange(fd.NS):
    front_clearing_queue_present.append([])
    for el_p in xrange(fd.P):
        #################################################  FCC #########################################################
        if el_p == 0:
            front_clearing_queue_present[el_i].append(False)
        else:
            isFCC = ((fd.SC[el_i][el_p] - fd.ONRD[el_i][el_p]) > (fd.SC[el_i][el_p-1]-fd.ONRD[el_i][el_p-1])) and (fd.SC[el_i][el_p]-fd.ONRD[el_i][el_p] > fd.SD[el_i][el_p])
            front_clearing_queue_present[el_i].append(isFCC)
## Uncomment and create FCC_I vars to use dynamically determined front clearing queue
#for el_i in xrange(fd.NS):
#    hcm.addConstr(fccv[el_i][0] == 0, name='fcc_'+str(el_i)+'_0') 
#    for el_p in xrange(1,P):
#        # fcc_I0 = 1 -> SC(i,p)-ONRD(i,p)]>[SC(i,p-1)-ONRD(i,p-1) == true
#        hcm.addConstr(func_SC(el_i, 0, el_p) - ONRD[el_i][el_p] - func_SC(el_i, 0, el_p-1) + ONRD[el_i][el_p-1] >= -big_m*(1-fcc_I[el_i][el_p][0]),  # p-1 is fine as p>1
#                      name='fcc_s1_'+str(el_i)+'_'+str(el_p))
#        hcm.addConstr(func_SC(el_i, 0, el_p-1) - ONRD[el_i][el_p-1] - func_SC(el_i, 0, el_p) + ONRD[el_i][el_p] >= -big_m*(fcc_I[el_i][el_p][0]),  # p-1 is fine as p>1
#                      name='fcc_s2_'+str(el_i)+'_'+str(el_p))
#        # fcc_I1 = 1 -> [SC(i,p)-ONRD(i,p)] > SD(i,p)
#        hcm.addConstr(func_SC(el_i, 0, el_p) - ONRD[el_i][el_p] - SD[el_i][el_p] >= -big_m*(1-fcc_I[el_i][el_p][1]),  # p-1 is fine as p>1
#                      name='fcc_s1_'+str(el_i)+'_'+str(el_p))
#        hcm.addConstr(SD[el_i][el_p] - func_SC(el_i, 0, el_p) + ONRD[el_i][el_p] >= -big_m* (fcc_I[el_i][el_p][1]),  # p-1 is fine as p>1
 #                     name='fcc_s2_'+str(el_i)+'_'+str(el_p)) 

# MO3 Constraints
for el_i in xrange(fd.NS):  # Not computed for final node as it is assumed there is not queue there?
    for el_t in xrange(fd.S):
        for el_p in xrange(fd.P):
            ############################################ MO3 #########################################################
            if front_clearing_queue_present[el_i][el_p] == False:
                # If there is no front clearing queue, this value is set to segment capacity and effectively ignored
                hcm.addConstr(MO3(el_i, el_t, el_p) == func_SC(el_i, el_t, el_p), name="MO3_NFCQ"+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            else:
                # MO3 is minimum of following 5 quantities
                #MO3(i,t,p) <= MO1(i+1,t-WTT,p) - ONRF(i,t,p)
                #MO3(i,t,p) <= MO2(i+1,t-WTT,p) + OFRF(i+1,t-WTT,p) - ONRF(i,t,p)
                #MO3(i,t,p) <= MO3(i+1,t-WTT,p) + OFRF(i+1,t-WTT,p) - ONRF(i,t,p)
                #MO3(i,t,p) <= SC(i,t-WTT,p) - ONRF(i,t,p)
                #MO3(i,t,p) <= SC(i+1,t-WTT,p) + OFRF(i+1,t-WTT,p) - ONRF(i,t,p)
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
for el_t in xrange(fd.S):
    for el_p in xrange(fd.P):
        hcm.addConstr(MO3(fd.NS,el_t, el_p) == fd.SC[fd.NS-1][el_p]*(1/fd.Th),
                      name='MO3_'+str(fd.NS)+'_'+str(el_t)+'_'+str(el_p))
print("MO3 and FCC done")

########################################################################################################################

################################################## Mainline FLow #######################################################
# Mainline flow minimum calclation
#MF(i,t,p) <= MI(i,t,p)
#MF(i,t,p) <= MO1(i,t,p)
#MF(i,t,p) <= MO2(i,t,p)
#MF(i,t,p) <= MO3(i,t,p)
#MF(i,t,p) <= SC(i,t,p)
#MF(i,t,p) <= SC(i-1,t,p)
for el_i in xrange(fd.NS+1):
    for el_t in xrange(fd.S):
        for el_p in xrange(fd.P):
            hcm.addConstr(MF(el_i, el_t, el_p) <= MI[el_i][el_t][el_p], name='MF_m1_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            hcm.addConstr(MF(el_i, el_t, el_p) <= MO1(el_i, el_t, el_p), name='MF_m2_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            hcm.addConstr(MF(el_i, el_t, el_p) <= MO2(el_i, el_t, el_p), name='MF_m3_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            hcm.addConstr(MF(el_i, el_t, el_p) <= MO3(el_i, el_t, el_p), name='MF_m4_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            hcm.addConstr(MF(el_i, el_t, el_p) <= func_SC(el_i, el_t, el_p), name='MF_m5_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            hcm.addConstr(MF(el_i, el_t, el_p) <= func_SC(el_i-1, el_t, el_p), name='MF_m6_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            
# Flow Conservation
total_demand = sum([sum(fd.SD[el]) for el in xrange(len(fd.SD))])/4
hcm.addConstr(gbp.quicksum(gbp.quicksum(gbp.quicksum(SF(el_i, el_t, el_p) for el_p in xrange(fd.P)) for el_t in xrange(fd.S)) for el_i in xrange(fd.NS)) == total_demand,name='MF_Conservation')            
print("MF done")
########################################################################################################################


################################################### Segment FLow #######################################################
# Segment flow is equal to the mainline flow plus off-ramp flow of node at downstream end
for el_i in xrange(fd.NS):
    for el_t in xrange(fd.S):
        for el_p in xrange(fd.P):
            hcm.addConstr(SF(el_i, el_t, el_p) == MF(el_i+1, el_t, el_p) + OFRF(el_i+1, el_t, el_p),  # i+1 -> uses nodes at downstream end of segment
                          name="3.112"+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
print("SF done")
########################################################################################################################


################################################## Update NV and UV ####################################################
# Update number of vehicles and unserved vehicles on the segment
# NV(i,t,p) = NV(i,t-1,p) + MF(i,t,p) + ONRF(i,t,p) - MF(i+1,t,p) - OFRF(i+1,t,p)
# UV(i,t,p) = NV(i,t,p) - [KB(i,t,p)*L(i)]
M_UV = 10000
uv_zero_tol = 0.01
for el_i in xrange(fd.NS):  # NV and UV are segment quantities
    for el_t in xrange(fd.S):
        for el_p in xrange(fd.P):
            ########################################### NV #############################################################
            hcm.addConstr(NV(el_i, el_t, el_p) == NV(el_i, el_t-1, el_p) + MF(el_i, el_t, el_p)
                          + ONRF(el_i, el_t, el_p) - MF(el_i+1, el_t, el_p) - OFRF(el_i+1, el_t, el_p),
                          name="3.113" + str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            ########################################### UV #############################################################
            hcm.addConstr(UV(el_i, el_t, el_p) == NV(el_i, el_t, el_p) - func_KB(el_i, el_p)*func_L(el_i),
                          name="3.114"+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
            ######################################## UV Check ##########################################################            
            if use_classic_mo2 is True:
                # I_UV0=1 => UV>0 (Queue Present)
                hcm.addConstr(UV(el_i, el_t, el_p) - uv_zero_tol <= M_UV * I_UV(el_i, el_t, el_p),
                              name="I_UV0"+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                # I_UV0=0 => UV=0 (No Queue Present)
                hcm.addConstr(uv_zero_tol - UV(el_i, el_t, el_p) <= M_UV * (1-I_UV(el_i, el_t, el_p)),
                              name="I_UV1"+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
print("NV and UV done")

################################################ Capacity Constraints ##################################################    
# Addressed at beginning of model
########################################################################################################################

############################################ Segment Performance Measures ##############################################
for el_i in xrange(fd.NS):
    for el_p in xrange(fd.P):
        hcm.addConstr(SFv_avg[el_i][el_p] == (fd.Th/fd.S)*gbp.quicksum(SF(el_i,tau,el_p) for tau in xrange(fd.S)),
                      name='SFv_avg_'+str(el_i)+'_'+str(el_p))
        hcm.addConstr(NVv_avg[el_i][el_p] == (1.0/fd.S)*gbp.quicksum(NV(el_i,tau,el_p) for tau in xrange(fd.S)),
                      name='NVv_avg_'+str(el_i)+'_'+str(el_p))
        hcm.addConstr(Kv[el_i][el_p] == NVv_avg[el_i][el_p]/fd.L_mi[el_i],
                      name='Kv_'+str(el_i)+'_'+str(el_p))

###################################### Add Objective Abs Val Constraints ###############################################
if use_dta_obj == False:
    if use_speed_match == False:
        for el_i in xrange(fd.NS):
            for el_t in xrange(fd.S):
                for el_p in xrange(fd.P):
                    hcm.addConstr(NV_delta[el_i][el_t][el_p] >= NV(el_i, el_t, el_p) - fd.fNV[el_i][el_t][el_p],
                                  name='Obj_Constr1_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                    hcm.addConstr(NV_delta[el_i][el_t][el_p] >= fd.fNV[el_i][el_t][el_p] - NV(el_i, el_t, el_p),
                                  name='Obj_Constr2_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                    hcm.addConstr(UV_delta[el_i][el_t][el_p] >= UV(el_i, el_t, el_p) - fd.fUV[el_i][el_t][el_p],
                                  name='Obj_Constr3_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                    hcm.addConstr(UV_delta[el_i][el_t][el_p] >= fUV[el_i][el_t][el_p] - UV(el_i, el_t, el_p),
                                  name='Obj_Constr4_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                                  
    if use_speed_match == True:
        if use_full_res == False:    
            for el_i in xrange(fd.NS):
                for el_p in xrange(fd.P):
                    hcm.addConstr(V_delta[el_i][el_p] >= SFv_avg[el_i][el_p] - fd.V[el_i][el_p]*Kv[el_i][el_p],
                                name='Obj_Constr1_'+str(el_i)+'_'+str(el_p))
                    hcm.addConstr(V_delta[el_i][el_p] >= fd.V[el_i][el_p]*Kv[el_i][el_p] -SFv_avg[el_i][el_p],
                                name='Obj_Constr2_'+str(el_i)+'_'+str(el_p))
        else:
            for el_i in xrange(fd.NS):
                for el_t in xrange(fd.S):
                    for el_p in xrange(fd.P):
                        hcm.addConstr(Vhr_delta[el_i][el_t][el_p] >= SF(el_i,el_t,el_p)*func_L(el_i)*fd.Th - fd.Vhr[el_i][el_t][el_p]*NV(el_i,el_t,el_p),
                                      name='Obj_constr1_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
                        hcm.addConstr(Vhr_delta[el_i][el_t][el_p] >= fd.Vhr[el_i][el_t][el_p]*NV(el_i,el_t,el_p) - SF(el_i,el_t,el_p)*func_L(el_i)*fd.Th,
                                      name='Obj_constr2_'+str(el_i)+'_'+str(el_t)+'_'+str(el_p))
    
########################################################################################################################

hcm.update()
model_build_time=time.time()
print("Model Built: "+str(model_build_time - init_time))
#hcm.setParam(gbp.GRB.param.ConcurrentMIP, 32)
#hcm.read('sto_cq3.mst')
hcm.update()
# hcm.setParam(gbp.GRB.param.SubMIPNodes, 5000000)
hcm.optimize()
#hcm.presolve()
#hcm.computeIIS()
#hcm.write('model.ilp')
optimize_finish_time = time.time()
print("Model Solved: "+str(optimize_finish_time - model_build_time))

input("Press Enter to Print Output")
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
            #s+= ", " + str(ONRI[i][t][p].X)
            #s+= ", " + str(ONRD[i][p])
            #s+=", " + str(ONRQ(i,t, p).X)
            #s+= ", " + str(ONRF_I[i][t][p][0].X)
            #s+= ", " + str(ONRF_I[i][t][p][1].X)
            #s+= ", " + str(ONRO[i][t][p].X)
            s += ", " + str(ONRF(i+1,t, p).X)
            #s+= ", " + str(ONRQ(i,t, p).X)
            s += ", " + str(OFRF(i+1,t, p).X)
            #s+= ", " + str(DEF_A[i][t][p].X)
            s += ", " + str(DEF[i+1][t][p].X)
            #if i in Ftilde:
            #    s+= ", " + str(DEF_I[Ftilde.index(i)][t][p].X)
            #    s+= ", " + str(OFRF_I[Ftilde.index(i)][t][p][0].X)
            #    s+= ", " + str(OFRF_I[Ftilde.index(i)][t][p][1].x)
            #else:
            #    s+=", 0.0, 0.0, 0.0"
            #if i in Ntilde:
            #    s+= ", " + str(ONRI[Ntilde.index(i)][t][p].X)
            #    s+= ", " + str(ONRO[Ntilde.index(i)][t][p].X)
            #    s+= ", " + str(ONRF_I[Ntilde.index(i)][t][p][0].X)
            #    s+= ", " + str(ONRO_A[Ntilde.index(i)][t][p][0].X)
            #    s+= ", " + str(ONRO_A[Ntilde.index(i)][t][p][1].X)
            #    s+= ", " + str(ONRO_A[Ntilde.index(i)][t][p][2].X)
            #    s+= ", " + str(ONRO_A[Ntilde.index(i)][t][p][3].X)
            #else:
            #    s+=", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0"
            s+= ", " + str(UV(i,t,p).X)
            #s+= ", " + str(I_UV(i,t,p).X)
            #if p < 0 or (p == 0 and t == 0):
            #    s+=", 0.0"
            #else:
            #    s+= ", " + str(UV(i-1, t - 1, p).X)
            s+=", " + str(SF(i, t, p).X)
            s+=", " + str(KQ[i][t][p].X)
            s+=", " + str(ASF[i][t][p].X)
            print(s)

# Computing Performance Measures
segFlow = zeros((fd.NS, fd.P))
numVeh = zeros((fd.NS,fd.P))
K = zeros((fd.NS,fd.P))
U = zeros((fd.NS,fd.P))
recalc_V = zeros((fd.NS, fd.P))
print("\nSPEED DIFFERENCES")
for p in xrange(fd.P):
    for i in xrange(fd.NS):
        segFlow[i][p] = (fd.Th/fd.S)*sum([SF(i,tau,p).X for tau in xrange(fd.S)])
        numVeh[i][p] = (1.0/fd.S)*sum([NV(i,tau,p).X for tau in xrange(fd.S)])
        K[i][p] = numVeh[i][p]/fd.L_mi[i]
        U[i][p] = segFlow[i][p]/K[i][p]
        temp_segFlow=(fd.Th/fd.S)*sum([fd.fSF[i][tau][p] for tau in xrange(fd.S)])
        temp_numVeh = (1.0/fd.S)*sum([fd.fNV[i][tau][p] for tau in xrange(fd.S)])
        recalc_V[i][p]=temp_segFlow/(temp_numVeh/fd.L_mi[i])
        print(str(i)+','+str(p)+','+"{0:.2f}".format(U[i][p])+','+"{0:.2f}".format(recalc_V[i][p])+','+"{0:.2f}".format(U[i][p]-recalc_V[i][p])) # +','+"{0:.2f}".format(KBv[i][p].X)+','+"{0:.2f}".format(CAFv[i].X)
        