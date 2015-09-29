from __future__ import division
import time
import facilities
import gurobipy as gbp
from numpy import *
from constraintGenerator import generate_max_constrs, generate_min_constrs, sum_add_t, sum_sum_add_t_p
__author__ = 'jltrask'

use_sos = False
printFile = False
def_const_type = 0
example_problem  = 13

init_time = time.time()

# Importing Facility
fd = facilities.extract(example_problem)
NS = fd["NS"]
Stilde = fd["Stilde"]
Ftilde = fd["Ftilde"]  # List of OFR segments
Ntilde = fd["Ntilde"]  # List of ONR segments
Wtilde = fd["Wtilde"]   # List of Weave segments
P = fd["P"]  # number of time intervals (periods) in the analysis period
Ptilde = fd["Ptilde"]  # List of time intervals
S = fd["S"]  # Number of time steps in a single interval (each step is 15 seconds)
Ttilde = fd["Ttilde"]  # List of time steps
Th = fd["Th"]  # Number of time steps in 1 hour
alpha = fd["alpha"]  # %

# Constants
KC = fd["KC"]  # Ideal Density at capacity
KJ = fd["KJ"] # Facility-wide jam density
L = fd["L"]  # Length of each segment
SC = fd["SC"]  # Segment capacity of segment i in interval p
mainline_demand = fd["mainline_demand"]
N = fd["N"]  # Number of open lanes in segment i in interval p
WS = fd["WS"] # Wave speed for segment i in interval p
WTT = fd["WTT"]  # Wave travel time
ONRD = fd["ONRD"]  # Demand flow rate for ONR at node i in interval p
ONRC = fd["ONRC"] # Geometric capacity of ONR at node i in period t in interval p
RM = fd["RM"]  # Ramp metering rate of node i during interval p (veh/h)
OFRD = fd["OFRD"]  # Demand flow rate for OFR at node i in interval p
SD = fd["SD"] # Segment demand for segment i in time interval p
# Precomputing known values
# (1) Estimated demand (ED) and background density (KB)
EDv = facilities.compute_estimated_demand(SC, SD)
#KB = compute_background_density(ED, Ftilde, Ntilde)
KB = fd["KB"]

# (2) Wave Trave Time and Wave Speed

######## Auxiliary Functions
def generate_sc(i,t,p):
    if t < 0:
        return generate_sc(i,t+S, p-1)
    elif p<0:
        return SC[i][0]
    else:
        return SC[i][p]


######## Creating Gurobi Model
# Initializing model instance
hcm = gbp.Model("hcm-test")

# Creating linear decision variables
#EDv = []  # Expected dmand that would arrive at segment i over inteval p
#for el_i in xrange(NS):
#    EDv.append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ED' + str(el_i) + str(el_p)) for el_p in xrange(P)])
#ED = lambda i, p: min(SD[0][p], SC[0][p]) if i is 0 else EDv[i][p]
#KB = []  # Background density of segment i during time interval p
#for el_i in xrange(NS):
#    KB.append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='KB' + str(el_i) + str(el_p)) for el_p in xrange(P)])
KQ = []  # Queue density: vechicle density in the queue on segment i in step t in interval p
for el_i in xrange(NS):
    KQ.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='KQ'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
MFv = []  # Actual mainline flow rate in node i during step t in interval p
for el_i in xrange(NS):
    MFv.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='MF'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
def MF(i, t, p):
    if i < 0:
        return min(mainline_demand[p],SC[0][p])
    if i >= NS:
        return min(SD[NS-1][p], SC[NS-1][p]) ## Feasibility issue.
    elif t <  0:
        if p is 0:
            return min(mainline_demand[0],SC[0][p])  ## Feasibility issue.
        else:
            return MFv[i][S+t][p-1]
    else:
        return MFv[i][t][p]

SFv = []  # Segment flow out of segment i during step t in interval p
for el_i in xrange(NS):
    SFv.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='SF'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
init_flow = [1500 for i in xrange(NS)]  # TODO: Get undersat flow
def SF(s, t, p):
    if s>=NS:
        return 0
    elif t < 0:
        if p is 0:
            return 0
        else:
            return SFv[s][S+t][p-1]
    else:
        return SFv[s][t][p]
MI = []  # Maximum mainline input: max flow desiring to enter segment i during step t in interval p
for el_i in xrange(NS):
    MI.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='MI'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
ONRFv = []  # Actual ONR flow rate that can cross on ramp node i during step t in interval p
for el_i in xrange(NS):
    ONRFv.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRF'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
def ONRF(i, t, p):
    if i >= NS or i <0:
        return 0.0
    elif t<0:
        if p is 0:
            return 0.0
        else:
            return ONRFv[i][S+t][p-1]
    else:
        return ONRFv[i][t][p]
ONRI = []  # Input flow rate desiring to enter the merge point at ONR node i during step t in interval p
for el_i in xrange(len(Ntilde)): #nee NS
    ONRI.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRI'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
ONRQv = []  # Unment demand that is stored as a queu on the ONR roadway at node i during step t in interval p
for el_i in xrange(NS):
    ONRQv.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRQ'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
def ONRQ(i, t, p):
    if t < 0:
        if p is 0:
            return 0
        else:
            return ONRQv[i][S-1][p-1]
    else:
        return ONRQv[i][t][p]
ONRO = []  # Max output flow rate that can enter the merge point from ONR node i during step t in interval p
for el_i in xrange(len(Ntilde)): #nee NS
    ONRO.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRO'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
DEF = []  # Deficit in flow at segment i at time step t in interval p
DEF_A = []
for el_i in xrange(NS):
    DEF.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='DEF'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
    DEF_A.append([[hcm.addVar(lb=-1*gbp.GRB.INFINITY, ub=gbp.GRB.INFINITY, vtype=gbp.GRB.CONTINUOUS, name='DEF'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
OFRFv = []  # Actual flow that can exit at OFR node i during step t in interval p
for el_i in xrange(NS):
    OFRFv.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='OFRF'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
def OFRF(i, t, p):
    if i >= NS or i <0:
        return 0.0
    elif t < 0:
        if p is 0:
            return 0
        else:
            return OFRFv[i][S+t][p-1]
    else:
        return OFRFv[i][t][p]

UVv = []  # Unserved vehicles: additional # of vehicles stored in segment i at the end of step t in interval p
for el_i in xrange(NS):
    UVv.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='UV'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
#UV = lambda i, t, p: 0 if p is -1 else UVv[i][t][p]
def UV(i, t, p):
    if p < 0 or (p is 0 and t < 0):
        return 0
    elif t < 0:
        return UVv[i][S+t][p-1]  # TODO correct?
    else:
        return UVv[i][t][p]
MO1v = []  # Max mainline output 1: limited by ONR flow at segment i
for el_i in xrange(NS):
    MO1v.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='MO1'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
def MO1(i, t, p):
    if t < 0:
        if p is 0:
            return 9999
        else:
            #print(str(i) + "," +str((S+t)) + ","+str(p))
            return MO1v[i][S+t][p-1]
    else:
        return MO1v[i][t][p]

MO2v = []  # Max mainline output 2: limited by available storage on segment i due to a downstream queue
for el_i in xrange(NS):
    MO2v.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='MO2'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
def MO2(i, t, p):
    if t < 0:
        if p is 0:
            return 9999                  # TODO correcct?
        else:
            return MO2v[i][S+t][p-1]
    else:
        return MO2v[i][t][p]
MO3v = []  # Max mainline output 3: limited by the presence of qued vech at the upstream in up segment i while the queue clears from the downstream end of segment i
for el_i in xrange(NS):
    MO3v.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='MO3'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
def MO3(i, t, p):
    if t < 0:
        if p is 0:
            return 9999             # TODO correcct?
        else:
            return MO3v[i][S+t][p-1]
    else:
        return MO3v[i][t][p]
NVv = []  # NV in segment i at step t in interval p
for el_i in xrange(NS):
    NVv.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='NV'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S+1)])
NV = lambda i, t, p: NVv[i][t+1][p]


# More variable declarations
# Step 6-11 Variables
DEF_I = []
OFRF_I = []
#for el_i in xrange(NS): deprecated, do not need to create for all segments
for el_i in xrange(len(Ftilde)):
    DEF_I.append([])
    OFRF_I.append([])
    for el_t in xrange(S):
        DEF_I[el_i].append([])
        OFRF_I[el_i].append([])
        for el_p in xrange(P):
            DEF_I[el_i][el_t].append(
                [hcm.addVar(vtype=gbp.GRB.BINARY,
                            name = "DEF_I"+str(el_i)+str(el_t)+str(el_p)+str(el)) for el in xrange(2)])
            OFRF_I[el_i][el_t].append(
                [hcm.addVar(vtype=gbp.GRB.BINARY, name='OFRF_I'+str(el)+str(el_i)+str(el_t)+str(el_p)+"0"),
                 hcm.addVar(vtype=gbp.GRB.INTEGER, ub=2.0,
                            name='OFRF_I'+str(el)+str(el_i)+str(el_t)+str(el_p)+"1")])

# Step 12 variables
ONRO_A = []  # List of auxiliary variables for step 12
ONRF_I = []  # List of auxiliary variables for steps 13-15
ONRO_I = []
#for el_i in xrange(NS):  deprecated, do not need to create for all segments
for el_i in xrange(len(Ntilde)):
    ONRO_A.append([])
    ONRF_I.append([])
    ONRO_I.append([])
    for el_t in xrange(S):
        ONRO_A[el_i].append([])
        ONRF_I[el_i].append([])
        ONRO_I[el_i].append([])
        for el_p in xrange(P):
            # Creating auxilary variables
            ONRO_A[el_i][el_t].append(
                [hcm.addVar(vtype=gbp.GRB.CONTINUOUS,
                                                  name='ONRO_A1'+str(el_i)+str(el_t)+str(el_p)+str(el)) for el in xrange(4)])
            ONRF_I[el_i][el_t].append(
                [hcm.addVar(vtype=gbp.GRB.BINARY,
                                                  name='ONRF_A'+str(el)+str(el_i)+str(el_t)+str(el_p)) for el in xrange(2)])
            ONRO_I[el_i][el_t].append(
                [hcm.addVar(vtype=gbp.GRB.BINARY,
                            name = "ONRO_I"+str(el_i)+str(el_t)+str(el_p)+str(el)) for el in xrange(5)])

# Step 16-17,19,22 variables
MO1_I = []
MO1_A = []   # List of auxiliary variables for step 16
I_UV = [] # Array to hold binary indicator variables for step 17
MO3_A = [] # 4D array holding Auxiliary variables for step 19
MO3_I = [] # 4D array holding indicator variables for step 19
MF_A = [] # 4D array holding Auxiliary variables for step 22
MF_I = [] # 4D array holding indicator variables for step 22
for el_i in xrange(NS):
    MO1_I.append([])
    MO1_A.append([])
    I_UV.append([])
    MO3_A.append([])
    MO3_I.append([])
    MF_A.append([])
    MF_I.append([])
    for el_t in xrange(S):
        MO1_I[el_i].append([])
        MO1_A[el_i].append([])
        I_UV[el_i].append([])
        MO3_A[el_i].append([])
        MO3_I[el_i].append([])
        MF_A[el_i].append([])
        MF_I[el_i].append([])
        for el_p in xrange(P):
            MO1_I[el_i][el_t].append(
                [hcm.addVar(vtype=gbp.GRB.BINARY,
                            name = "MO1_I"+str(el_i)+str(el_t)+str(el_p)+str(el)) for el in xrange(2)])
            MO1_A[el_i][el_t].append(hcm.addVar(vtype=gbp.GRB.CONTINUOUS,
                            name='MO1_A'+str(el_i)+str(el_t)+str(el_p)))
            I_UV[el_i][el_t].append(
                [hcm.addVar(vtype=gbp.GRB.BINARY,
                            name = "I_UV"+str(var_id)+str(el_i)+str(el_t)+str(el_p))for var_id in xrange(2)])
            MO3_A[el_i][el_t].append(
                [hcm.addVar(vtype=gbp.GRB.CONTINUOUS,
                            name='MO3_A'+str(el)+str(el_i)+str(el_t)+str(el_p)) for el in xrange(4)])
            MO3_I[el_i][el_t].append(
                [hcm.addVar(vtype=gbp.GRB.BINARY,
                            name='MO3_I'+str(el)+str(el_i)+str(el_t)+str(el_p)) for el in xrange(8)])
            MF_A[el_i][el_t].append(
                [hcm.addVar(vtype=gbp.GRB.CONTINUOUS,
                            name='MF_A'+str(el)+str(el_i)+str(el_t)+str(el_p)) for el in xrange(4)])
            MF_I[el_i][el_t].append(
                [hcm.addVar(vtype=gbp.GRB.BINARY,
                            name='MF_I'+str(el)+str(el_i)+str(el_t)+str(el_p)) for el in xrange(10)])



# Integrating variables into model
hcm.update()

# Set objective
sum_nv = 0
for el_i in xrange(NS):
    for el_t in xrange(S):
        for el_p in xrange(P):
            sum_nv += (NV(el_i, el_t, el_p))

hcm.setObjective(sum_nv, gbp.GRB.MINIMIZE)
hcm.update()

################## DEPRECATED: ED IS A CONSTANT BASED ON KB #####################################################################################################################################################
# Adding equality/inquality constraints
# Step 1: Calculate background density for each segment in current time interval
# ED_I = []
# bigM = max(max(SC), max(SD)+max(ONRD))  # TODO should be okay
# for el_i in xrange(1, NS):  # Estimated demand for the first segment is minimum of capacity and mainline demand for that period so no constraint needed (predetermined and accounted for in lambda function ED)
#     ED_I.append([])
#     for el_p in xrange(P):
#         # Creating binary variables
#         ED_I[el_i].append([hcm.addVar(vtype=gbp.GRB.BINARY, name='ED_I'+str(ii)+str(el_i)+str(el_p)) for ii in xrange(2)])  # TODO put with initial variable declaration
#         hcm.update()
#         # Min constraint #1
#         hcm.addConstr(SC[el_i][el_p] - ED(el_i-1, el_p) - ONRD[el_i][el_p] + OFRD[el_i][el_p] <= bigM*ED_I[el_i][el_p][0], name="ED_Min1"+str(el_i)+str(el_p))
#         # Min constraint #2
#         hcm.addConstr(ED(el_i-1, el_p) + ONRD[el_i][el_p] - OFRD[el_i][el_p] - SC[el_i][el_p] <= bigM*ED_I[el_i][el_p][1], name="ED_Min2"+str(el_i)+str(el_p))
#         # Constraint that one has to be true
#         hcm.addConstr(ED_I[el_i][el_p][0] + ED_I[el_i][el_p][1] == 1, name="ED_Min3"+str(el_i)+str(el_p))
#         # Constraint assigning minimum value to EDip
#         bigM1 = 10000  # TODO calculate real value
#         bigM2 = 10000  # TODO calculate real value
#         hcm.addConstr(ED(el_i, el_p) - SC[el_i][el_p] <= bigM1*ED_I[el_i][el_p][0], name='ED_D1'+str(el_i)+str(el_p))
#         hcm.addConstr(SC[el_i][el_p] - ED(el_i, el_p) <= bigM1*ED_I[el_i][el_p][0], name='ED_D2'+str(el_i)+str(el_p))
#         hcm.addConstr(ED(el_i, el_p) - ED(el_i-1, el_p) - ONRD[el_i][el_p] + OFRD[el_i][el_p] <= bigM2*ED_I[el_i][el_p][1], name='ED_D3'+str(el_i)+str(el_p))
#         hcm.addConstr(ED(el_i-1, el_p) + ONRD[el_i][el_p] - OFRD[el_i][el_p] - ED(el_i, el_p) <= bigM2*ED_I[el_i][el_p][1], name='ED_D4'+str(el_i)+str(el_p))
#
# hcm.update()
#################################################################################################################################################################################################################

###################################################### Eq 25-7 #########################################################
# Step 2: initialize the Freeway Facility
# Updateing # of vehicles - note t goes from 0 to S (i.e. S+1 steps) for NV, with 0 being  "before" interval p starts.
##### Need to calculate KB from Undersat
for el_i in xrange(NS):
    for el_p in xrange(P):  # Note that the lambda function on UV accounts for the case p = -1 (UV = 0 in that case)
        hcm.addConstr(NV(el_i, -1, el_p) == KB[el_i][el_p]*L[el_i] + UV(el_i, S-1, el_p-1), name='NV_E'+str(el_i)+str(0)+str(el_p))
#hcm.update()
print("step 2 done")
########################################################################################################################


# Steps 3-4: Begin "loops" of all segments, all time steps
# Steps 5-8: OFR Segment constraints
big_m = 100000  # TODO calculate
big_m1 = 100000  # TODO calculate
big_m2 = 100000  # TODO calculate
big_m1_1 = 100000  # TODO calculate
big_m1_2 = 100000  # TODO calculate
def_zero_tol = 0.001
###################################################### Eq 25-22 ########################################################
for el_i in xrange(NS):
    if el_i in Ftilde:  # Check if OFR at segment
        # Convert segment idx to ofr var idx (for DEF_I, OFRF_I)
        ofr_i = Ftilde.index(el_i)
        # Calculate possible deficit from upstream queue (Note el_i-1 okay because the first segment cannot be OFR)
        for el_t in xrange(S):
            hcm.addConstr(DEF[el_i][el_t][0] == 0.0, name='DEF_E'+str(el_i)+str(el_t)+str(0)) # ASSUMED NO DEFICIT IN THE FIRST PERIOD
            for el_p in xrange(1,P):
                if def_const_type is 0: # Updated DEF_A equations
                    a1 = 0
                    if el_t is 0:
                        a1 = sum(SD[el_i-1][0:el_p])*(1/240.0) # Add Segment demand from first to previous period
                        a1-= sum([sum([MF(el_i-1, el1, el2)*(1/240.0)+ONRF(el_i-1, el1, el2)*(1/240.0) for el1 in xrange(S)]) for el2 in xrange(el_p)]) # Subtract (MF+ONRF)
                        hcm.addConstr(DEF_A[el_i][el_t][el_p] == a1, name="DEF_TEMP_A"+str(el_i)+str(el_t)+str(el_p))
                    else:
                        hcm.addConstr(DEF_A[el_i][el_t][el_p] == DEF_A[el_i][el_t-1][el_p] + MF(el_i-1, el_t-1, el_p)*(1/240.0) + ONRF(el_i-1, el_t-1, el_p)*(1/240.0), name="DEF_TEMP_A"+str(el_i)+str(el_t)+str(el_p))
                    #### Setting DEF to be max of DEF_A and 0
                    # Checking to see if DEF_A is greater than 0
                    hcm.addConstr(DEF_A[el_i][el_t][el_p] <= big_m * DEF_I[ofr_i][el_t][el_p][0],
                              name='DEF_E1'+str(el_i)+str(el_t)+str(el_p)) # To check if a1>=0
                    hcm.addConstr(-DEF_A[el_i][el_t][el_p] <= big_m * (1 - DEF_I[ofr_i][el_t][el_p][0]),
                              name='DEF_E2'+str(el_i)+str(el_t)+str(el_p)) # To check if a1>=0
                    # Setting DEF to be a1 (when DEF_A[el_i][el_t][el_p][0] = 1)
                    hcm.addConstr(DEF[el_i][el_t][el_p] - DEF_A[el_i][el_t][el_p]  <= big_m * (1 - DEF_I[ofr_i][el_t][el_p][0]),
                              name='DEF_E3'+str(el_i)+str(el_t)+str(el_p))
                    hcm.addConstr(DEF_A[el_i][el_t][el_p]  - DEF[el_i][el_t][el_p] <= big_m * (1 - DEF_I[ofr_i][el_t][el_p][0]),
                              name='DEF_E4'+str(el_i)+str(el_t)+str(el_p))
                    # Setting DEF to be 0 (when DEF_A[el_i][el_t][el_p][0] = 0)
                    hcm.addConstr(DEF[el_i][el_t][el_p] <= big_m*DEF_I[ofr_i][el_t][el_p][0],
                              name='DEF_E5'+str(el_i)+str(el_t)+str(el_p))
                    hcm.addConstr(-1*DEF[el_i][el_t][el_p] <= big_m*DEF_I[ofr_i][el_t][el_p][0],
                              name='DEF_E6'+str(el_i)+str(el_t)+str(el_p))
                else:
                    # Force Deficit to be 0 (debugging purposes)
                    hcm.addConstr(DEF_A[el_i][el_t][el_p] == 0.0, name='DEF_TEMP_A'+str(el_i)+str(el_t)+str(el_p))
                    hcm.addConstr(DEF[el_i][el_t][el_p] == 0.0, name='DEF_TEMP_A'+str(el_i)+str(el_t)+str(el_p))
########################################################################################################################


###################################################### Eq 25-23 ########################################################
                # Step 7: If there is a deficit (DEF[i,t,p]>0), use OFR flow with Deficit method
                # Constraints checking if there is a deficit
                hcm.addConstr(DEF[el_i][el_t][el_p] - def_zero_tol <= big_m * OFRF_I[ofr_i][el_t][el_p][0],
                              name='OFRF_IF_DEF1'+str(el_i)+str(el_t)+str(el_p))  # OFRF_Ii,t,p,0 = 1 implies DEF > 0
                hcm.addConstr(def_zero_tol - DEF[el_i][el_t][el_p] <= big_m * (1 - OFRF_I[ofr_i][el_t][el_p][0]),
                              name='OFRF_IF_DEF2'+str(el_i)+str(el_t)+str(el_p))  # OFRF_Ii,t,p,0 = 0 implies DEF < 0

                # Constraint that activates (or deactivates) situation 1/2 based on deficit check
                # If there is a deficit, i_0=0.
                # i_1 >= 2-2*i_0
                # i_1 <= M*(1-i_0)+1
                hcm.addConstr(OFRF_I[ofr_i][el_t][el_p][1] >= 2 - 2 * OFRF_I[ofr_i][el_t][el_p][0],
                              name='OFRF_IF_DEF3'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(OFRF_I[ofr_i][el_t][el_p][1] <= 1 * (1-OFRF_I[ofr_i][el_t][el_p][0]) + 1,
                              name='OFRF_IF_DEF4'+str(el_i)+str(el_t)+str(el_p)) # big_m=1 b/c i_1<=2 (ub)

                # Constraints to check to see if situation 1 or situation 2 is true. OFRF_Ii,t,p,1 (i_1) = 1 implies that
                # situation 1 is used, while if OFRF_Ii,t,p,1 (i_1) = 0 imples that situation 2 is used.
                hcm.addConstr(DEF[el_i][el_t][el_p]
                              - MF(el_i-1, el_t, el_p)
                              - ONRF(el_i-1, el_t, el_p)
                              <= big_m * OFRF_I[ofr_i][el_t][el_p][1],
                              name="OFRF_IF_S1"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MF(el_i-1, el_t, el_p)
                              + ONRF(el_i-1, el_t, el_p)
                              - DEF[el_i][el_t][el_p]
                              <= big_m * (OFRF_I[ofr_i][el_t][el_p][1] - 1),           # Reversed because i_1 can = 2
                              name="OFRF_IF_S2"+str(el_i)+str(el_t)+str(el_p))

                    # Situation 1: If upstream mainline flow plus the flow from an ONR at the upstream node is less than
                    # the deficit for this time step, then the OFR flow is equal to the mainline and the ONR flows times
                    # the OFR turning percentage in the preceeding itme interval
                ofr_tp1 = 0
                if el_p > 0:
                    ofr_tp1 = OFRD[el_i][el_p-1]/SD[el_i-1][el_p-1]
                else:  # TODO OFR turning percentage for -1 period?
                    ofr_tp1 = OFRD[el_i][el_p]/SD[el_i-1][el_p]
                hcm.addConstr(OFRF(el_i, el_t, el_p)
                              - ofr_tp1*MFv[el_i-1][el_t][el_p]
                              - ofr_tp1*ONRF(el_i-1, el_t, el_p)
                              <= big_m*(OFRF_I[ofr_i][el_t][el_p][1] - 1),
                              name='OFRF_E1_1'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(OFRF(el_i, el_t, el_p)
                              - ofr_tp1*MFv[el_i-1][el_t][el_p]
                              - ofr_tp1*ONRF(el_i-1, el_t, el_p)
                              >= -1*big_m * (OFRF_I[ofr_i][el_t][el_p][1] - 1),
                              name='OFRF_E1_2'+str(el_i)+str(el_t)+str(el_p))
###################################################### Eq 25-24 ########################################################
                    # Situation 2: If the deficit is less than the upstream mainline flow plus the ONR flow from an ONR
                    # at the upstream node (if present)
                ofr_tp2_1 = 0
                if el_p > 0:
                    ofr_tp2_1 = OFRD[el_i][el_p-1]/SD[el_i-1][el_p-1]
                else:  # TODO OFR turning percentage for -1 period?
                    ofr_tp2_1 = OFRD[el_i][el_p]/SD[el_i-1][el_p]
                ofr_tp2_2 = OFRD[el_i][el_p]/SD[el_i-1][el_p]
                hcm.addConstr(OFRF(el_i, el_t, el_p)
                              - ofr_tp2_1*DEF[el_i][el_t][el_p]
                              - ofr_tp2_2*MFv[el_i-1][el_t][el_p]
                              - ofr_tp2_2*ONRF(el_i-1, el_t, el_p)
                              + ofr_tp2_2*DEF[el_i][el_t][el_p]
                              <= big_m*OFRF_I[ofr_i][el_t][el_p][1],
                              name='OFRF_E2_1'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(OFRF(el_i, el_t, el_p)
                              - ofr_tp2_1*DEF[el_i][el_t][el_p]
                              - ofr_tp2_2*MFv[el_i-1][el_t][el_p]
                              - ofr_tp2_2*ONRF(el_i-1, el_t, el_p)
                              + ofr_tp2_2*DEF[el_i][el_t][el_p]
                              >= -1*big_m*OFRF_I[ofr_i][el_t][el_p][1],
                              name='OFRF_E2_2'+str(el_i)+str(el_t)+str(el_p))

###################################################### Eq 25-25 ########################################################
                # Step 8: If there is no deficit (DEF[i,t,p]=0), use OFR flow without deficit method
                ofr_tp3 = OFRD[el_i][el_p]/SD[el_i-1][el_p]
                hcm.addConstr(OFRF(el_i, el_t, el_p)
                              - ofr_tp3*MFv[el_i-1][el_t][el_p]
                              - ofr_tp3*ONRF(el_i-1, el_t, el_p)
                              <= big_m * OFRF_I[ofr_i][el_t][el_p][0],
                              name='OFRF_E3_1'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(OFRF(el_i, el_t, el_p)
                              - ofr_tp3*MFv[el_i-1][el_t][el_p]
                              - ofr_tp3*ONRF(el_i-1, el_t, el_p)
                              >= -1*big_m * OFRF_I[ofr_i][el_t][el_p][0],
                              name='OFRF_E3_2'+str(el_i)+str(el_t)+str(el_p))
    else:  # The segment is not an offramp
       for el_t in xrange(S):
            for el_p in xrange(P):
                hcm.addConstr(OFRF(el_i, el_t, el_p) == 0.0, name='OFRF_E3'+str(el_i)+str(el_t)+str(el_p))
print("step 8 done")
########################################################################################################################


###################################################### Eq 25-8 ########################################################
# Step 9: Calculate Mainline Input
for el_i in xrange(NS):                               # TODO start loop at 0?
    for el_t in xrange(S):
        for el_p in xrange(P):
            hcm.addConstr(MI[el_i][el_t][el_p] ==       # UV function accounts for t-1 < 0
                          MF(el_i-1, el_t, el_p)        # mainline flow at upstream segment
                          + ONRF(el_i-1, el_t, el_p)    # ONR flow at upstream segment
                          - OFRF(el_i, el_t, el_p)      # OFR flow at current segment
                          + UV(el_i-1, el_t - 1, el_p), # Unserved vehs in the upstream segment at the prev time step
                          name='MI_E'+str(el_i)+str(el_t)+str(el_p))
print("step 9 done")
########################################################################################################################


###################################################### Eq 25-17 ########################################################
# Step 10: ONR at segment?
# Step 11: Calculate ONR input
for el_i in xrange(NS):
    if el_i in Ntilde:
        # Convert segment idx to onr var idx (for ONRO_A, ONRO_I, ONRF_I)
        onr_i = Ntilde.index(el_i)
        for el_t in xrange(S):
            for el_p in xrange(P):
                hcm.addConstr(ONRI[onr_i][el_t][el_p] ==
                              ONRD[el_i][el_p]            # ONR demand
                              + ONRQ(el_i, el_t-1, el_p), # Queued vehicles on ONR at the previous step (t-1=-1 case implemented in function def)
                              name='ONRI_E'+str(el_i)+str(el_t)+str(el_p))

###################################################### Eq 25-18 ########################################################
                # a1 = min of MO3 & MF
                # a2 = min of a1+ONRF & SC
                # a3 = max of a2-MI & a2/(2N)
                # a4 = min of a3 & ONRC
                # a5 = min of a4 & RM
                # inequalities to approximate min/max functions - not likely to work
                # hcm.addConstr(ONRO_A[onr_i][el_t][el_p][0] <= MF(el_i+1, el_t-1, el_p) + ONRF(el_i, el_t-1, el_p))
                # hcm.addConstr(ONRO_A[onr_i][el_t][el_p][0] <= SC[el_i][el_p])
                # hcm.addConstr(ONRO_A[onr_i][el_t][el_p][0] <= MO3(el_i, el_t-1, el_p) + ONRF(el_i, el_t-1, el_p))
                # hcm.addConstr(ONRO_A[onr_i][el_t][el_p][1] >= ONRO_A[onr_i][el_t][el_p][0] - MI[el_i][el_t][el_p])
                # hcm.addConstr(ONRO_A[onr_i][el_t][el_p][1] >= ONRO_A[onr_i][el_t][el_p][0] * (1.0/(2 * N[el_i][el_p])))
                # hcm.addConstr(ONRO_A[onr_i][el_t][el_p][2] <= RM[el_i][el_p])
                # hcm.addConstr(ONRO_A[onr_i][el_t][el_p][2] <= ONRC(el_i, el_t, el_p))
                # hcm.addConstr(ONRO_A[onr_i][el_t][el_p][2] <= ONRO_A[onr_i][el_t][el_p][1])
                ########## Minimum #1: Min of MF & MO3
                hcm.addConstr(MF(el_i+1, el_t-1, el_p) - MO3(el_i, el_t-1, el_p)
                              <= big_m * ONRO_I[onr_i][el_t][el_p][0],
                              name='ONRO_MIN1_1'+str(el_i)+str(el_t)+str(el_p)) # ONRO_I0=1 => MF > MO3
                hcm.addConstr(MO3(el_i, el_t-1, el_p) - MF(el_i+1, el_t-1, el_p)
                              <= big_m * (1 - ONRO_I[onr_i][el_t][el_p][0]),
                              name='ONRO_MIN1_2'+str(el_i)+str(el_t)+str(el_p)) # ONRO_I0=0 => MF < MO3
                # If ONRO_I0 = 0, setting ONRO_A0 = MF
                hcm.addConstr(ONRO_A[onr_i][el_t][el_p][0] - MF(el_i+1, el_t-1, el_p)
                              <= big_m * ONRO_I[onr_i][el_t][el_p][0],
                              name='ONRO_MIN1_3'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRO_A[onr_i][el_t][el_p][0] - MF(el_i+1, el_t-1, el_p)
                              >= -1*big_m * ONRO_I[onr_i][el_t][el_p][0],
                              name='ONRO_MIN1_4'+str(el_i)+str(el_t)+str(el_p))
                # If ONRO_I0 = 1, setting ONRO_A0 = MO3
                hcm.addConstr(ONRO_A[onr_i][el_t][el_p][0] - MO3(el_i, el_t-1, el_p)
                              <= big_m * (1 - ONRO_I[onr_i][el_t][el_p][0]),
                              name='ONRO_MIN1_5'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRO_A[onr_i][el_t][el_p][0] - MO3(el_i, el_t-1, el_p)
                              >= -1*big_m * (1 - ONRO_I[onr_i][el_t][el_p][0]),
                              name='ONRO_MIN1_6'+str(el_i)+str(el_t)+str(el_p))

                ########## Minimum #2: Min of ONRO_A0+ONRF & SC
                hcm.addConstr(ONRO_A[onr_i][el_t][el_p][0] + ONRF(el_i, el_t-1, el_p) - SC[el_i][el_p]
                              <= big_m * ONRO_I[onr_i][el_t][el_p][1],
                              name='ONRO_MIN2_1'+str(el_i)+str(el_t)+str(el_p)) # ONRO_I1=1 => ONRO_A0+ONRF > SC
                hcm.addConstr(SC[el_i][el_p] - ONRO_A[onr_i][el_t][el_p][0] - ONRF(el_i, el_t-1, el_p)
                              <= big_m * (1 - ONRO_I[onr_i][el_t][el_p][1]),
                              name='ONRO_MIN2_2'+str(el_i)+str(el_t)+str(el_p)) # ONRO_I1=0 => ONRO_A0+ONRF < SC
                # If ONRO_I1 = 0, setting ONRO_A1 = ONRO_A0+ONRF
                hcm.addConstr(ONRO_A[onr_i][el_t][el_p][1] - ONRO_A[onr_i][el_t][el_p][0] - ONRF(el_i, el_t-1, el_p)
                              <= big_m * ONRO_I[onr_i][el_t][el_p][1],
                              name='ONRO_MIN2_3'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRO_A[onr_i][el_t][el_p][1] - ONRO_A[onr_i][el_t][el_p][0] - ONRF(el_i, el_t-1, el_p)
                              >= -1*big_m * ONRO_I[onr_i][el_t][el_p][1],
                              name='ONRO_MIN2_4'+str(el_i)+str(el_t)+str(el_p))
                # If ONRO_I1 = 1, setting ONRO_A1 = SC
                hcm.addConstr(ONRO_A[onr_i][el_t][el_p][1] - SC[el_i][el_p]
                              <= big_m * (1 - ONRO_I[onr_i][el_t][el_p][1]),
                              name='ONRO_MIN2_5'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRO_A[onr_i][el_t][el_p][1] - SC[el_i][el_p]
                              >= -1*big_m * (1 - ONRO_I[onr_i][el_t][el_p][1]),
                              name='ONRO_MIN2_6'+str(el_i)+str(el_t)+str(el_p))

                ########## Maximum #1: Max of ONRO_A1-MI & ONRO_A1/(2*N)
                hcm.addConstr(ONRO_A[onr_i][el_t][el_p][1] - MI[el_i][el_t][el_p]
                              - ONRO_A[onr_i][el_t][el_p][1] * (1.0/(2 * N[el_i][el_p]))
                              <= big_m * ONRO_I[onr_i][el_t][el_p][2],
                              name='ONRO_MAX1_1'+str(el_i)+str(el_t)+str(el_p)) # ONRO_I2=1 => ONRO_A1-MI > ONRO_A1/2N
                hcm.addConstr(ONRO_A[onr_i][el_t][el_p][1] * (1.0/(2 * N[el_i][el_p]))
                              - ONRO_A[onr_i][el_t][el_p][1] + MI[el_i][el_t][el_p]
                              <= big_m * (1 - ONRO_I[onr_i][el_t][el_p][2]),
                              name='ONRO_MAX1_2'+str(el_i)+str(el_t)+str(el_p)) # ONRO_I2=0 => ONRO_A1-MI < ONRO_A1/2N
                # If ONRO_I2 = 1, setting ONRO_A2 = ONRO_A1-MI
                hcm.addConstr(ONRO_A[onr_i][el_t][el_p][2] - ONRO_A[onr_i][el_t][el_p][1] + MI[el_i][el_t][el_p]
                              <= big_m * (1 - ONRO_I[onr_i][el_t][el_p][2]),
                              name='ONRO_MAX1_3'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRO_A[onr_i][el_t][el_p][2] - ONRO_A[onr_i][el_t][el_p][1] + MI[el_i][el_t][el_p]
                              >= -1*big_m * (1 - ONRO_I[onr_i][el_t][el_p][2]),
                              name='ONRO_MAX1_4'+str(el_i)+str(el_t)+str(el_p))
                # If ONRO_I2 = 0, setting ONRO_A2 = ONRO_A1/(2*N)
                hcm.addConstr(ONRO_A[onr_i][el_t][el_p][2] - ONRO_A[onr_i][el_t][el_p][1] * (1.0/(2 * N[el_i][el_p]))
                              <= big_m * ONRO_I[onr_i][el_t][el_p][2],
                              name='ONRO_MAX1_5'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRO_A[onr_i][el_t][el_p][2] - ONRO_A[onr_i][el_t][el_p][1] * (1.0/(2 * N[el_i][el_p]))
                              >= -1*big_m * ONRO_I[onr_i][el_t][el_p][2],
                              name='ONRO_MAX1_6'+str(el_i)+str(el_t)+str(el_p))

                ########## Minimum #3: Min of ONRO_A2 & ONRC
                hcm.addConstr(ONRO_A[onr_i][el_t][el_p][2] - ONRC(el_i, el_t, el_p)
                              <= big_m * ONRO_I[onr_i][el_t][el_p][3],
                              name='ONRO_MIN3_1'+str(el_i)+str(el_t)+str(el_p)) # ONRO_I3=1 => ONRO_A2 > ONRC
                hcm.addConstr(ONRC(el_i, el_t, el_p) - ONRO_A[onr_i][el_t][el_p][2]
                              <= big_m * (1 - ONRO_I[onr_i][el_t][el_p][3]),
                              name='ONRO_MIN3_2'+str(el_i)+str(el_t)+str(el_p)) # ONRO_I3=0 => ONRO_A2 < ONRC
                # If ONRO_I3 = 0, setting ONRO_A3 = ONRO_A2
                hcm.addConstr(ONRO_A[onr_i][el_t][el_p][3] - ONRO_A[onr_i][el_t][el_p][2]
                              <= big_m * ONRO_I[onr_i][el_t][el_p][3],
                              name='ONRO_MIN3_3'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRO_A[onr_i][el_t][el_p][3] - ONRO_A[onr_i][el_t][el_p][2]
                              >= -1*big_m * ONRO_I[onr_i][el_t][el_p][3],
                              name='ONRO_MIN3_4'+str(el_i)+str(el_t)+str(el_p))
                # If ONRO_I3 = 1, setting ONRO_A3 = ONRC
                hcm.addConstr(ONRO_A[onr_i][el_t][el_p][3] - ONRC(el_i, el_t, el_p)
                              <= big_m * (1 - ONRO_I[onr_i][el_t][el_p][3]),
                              name='ONRO_MIN3_5'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRO_A[onr_i][el_t][el_p][3] - ONRC(el_i, el_t, el_p)
                              >= -1*big_m * (1 - ONRO_I[onr_i][el_t][el_p][3]),
                              name='ONRO_MIN3_6'+str(el_i)+str(el_t)+str(el_p))

                ########## Minimum #4: Min of ONRO_A3 & RM
                hcm.addConstr(ONRO_A[onr_i][el_t][el_p][3] - RM[el_i][el_p]
                              <= big_m * ONRO_I[onr_i][el_t][el_p][4],
                              name='ONRO_MIN4_1'+str(el_i)+str(el_t)+str(el_p)) # ONRO_I4=1 => ONRO_A3 > RM
                hcm.addConstr(RM[el_i][el_p] - ONRO_A[onr_i][el_t][el_p][3]
                              <= big_m * (1 - ONRO_I[onr_i][el_t][el_p][4]),
                              name='ONRO_MIN4_2'+str(el_i)+str(el_t)+str(el_p)) # ONRO_I4=0 => ONRO_A3 < RM
                # If ONRO_I4 = 0, setting ONRO = ONRO_A3
                hcm.addConstr(ONRO[onr_i][el_t][el_p] - ONRO_A[onr_i][el_t][el_p][3]
                              <= big_m * ONRO_I[onr_i][el_t][el_p][4],
                              name='ONRO_MIN4_3'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRO[onr_i][el_t][el_p] - ONRO_A[onr_i][el_t][el_p][3]
                              >= -1*big_m * ONRO_I[onr_i][el_t][el_p][4],
                              name='ONRO_MIN4_4'+str(el_i)+str(el_t)+str(el_p))
                # If ONRO_I4 = 1, setting ONRO = $M
                hcm.addConstr(ONRO[onr_i][el_t][el_p] - RM[el_i][el_p]
                              <= big_m * (1 - ONRO_I[onr_i][el_t][el_p][4]),
                              name='ONRO_MIN4_5'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRO[onr_i][el_t][el_p] - RM[el_i][el_p]
                              >= -1*big_m * (1 - ONRO_I[onr_i][el_t][el_p][4]),
                              name='ONRO_MIN4_6'+str(el_i)+str(el_t)+str(el_p))

###################################################### Eq 25-19 ########################################################
                # Step 13: Is ONRI < ONRO? If so, ONRF = ONRI. Else, ONRF = ONRO.
                hcm.addConstr(ONRO[onr_i][el_t][el_p] - ONRI[onr_i][el_t][el_p]
                              <= big_m*ONRF_I[onr_i][el_t][el_p][0],
                              name="ONRF_IF1"+str(el_i)+str(el_t)+str(el_p)) # ONRF_I0 = 1 => ONRO > ONRI
                hcm.addConstr(ONRI[onr_i][el_t][el_p] - ONRO[onr_i][el_t][el_p]
                              <= big_m*(1 - ONRF_I[onr_i][el_t][el_p][0]),
                              name="ONRF_IF2"+str(el_i)+str(el_t)+str(el_p)) # ONRF_I0 = 0 => ONRO < ONRI

                # Step 15: ONRF_I0 = 1 => ONRI < ONRO => ONRF = ONRI
                # (Step 15 before step 14 b/c Re-ordered for chapter equation numbering)
                hcm.addConstr(ONRF(el_i, el_t, el_p) - ONRI[onr_i][el_t][el_p]
                              <= big_m * (1 - ONRF_I[onr_i][el_t][el_p][0]),
                              name="ONRF_E3"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRF(el_i, el_t, el_p) - ONRI[onr_i][el_t][el_p]
                              >= -1*big_m * (1 - ONRF_I[onr_i][el_t][el_p][0]),
                              name="ONRF_E4"+str(el_i)+str(el_t)+str(el_p))

###################################################### Eq 25-20 ########################################################
                # Step 14: ONRF_I0 = 0 => ONR0 < ONRI => ONRF = ONR0
                hcm.addConstr(ONRF(el_i, el_t, el_p) - ONRO[onr_i][el_t][el_p]
                              <= big_m*ONRF_I[onr_i][el_t][el_p][0],
                              name="ONRF_E1"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRF(el_i, el_t, el_p) - ONRO[onr_i][el_t][el_p]
                              >= -1*big_m*ONRF_I[onr_i][el_t][el_p][0],
                              name="ONRF_E2"+str(el_i)+str(el_t)+str(el_p))

###################################################### Eq 25-21 ########################################################
                # ONRF_I0 = 0 => ONR0 < ONRI => Update number of vehicles on the ramp queue
                # ONRQ = ONRQt-1 + ONRI - ONRO
                hcm.addConstr(ONRQ(el_i, el_t, el_p)
                              - ONRQ(el_i, el_t-1, el_p)
                              - ONRI[onr_i][el_t][el_p]
                              + ONRO[onr_i][el_t][el_p]
                              <= big_m*ONRF_I[onr_i][el_t][el_p][0],
                              name="ONRQ_E1"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRQ(el_i, el_t, el_p)
                              - ONRQ(el_i, el_t-1, el_p)
                              - ONRI[onr_i][el_t][el_p]
                              + ONRO[onr_i][el_t][el_p]
                              >= -1*big_m*ONRF_I[onr_i][el_t][el_p][0],
                              name="ONRQ_E2"+str(el_i)+str(el_t)+str(el_p))
                # If ONRI < ONRO (ONRF_I0 = 1), entire ONRQ is served, and is set to be 0
                hcm.addConstr(ONRQ(el_i, el_t, el_p) <= big_m * (1 - ONRF_I[onr_i][el_t][el_p][0]),
                              name="ONRQ_E3"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRQ(el_i, el_t, el_p) >= -1*big_m * (1 - ONRF_I[onr_i][el_t][el_p][0]),
                              name="ONRQ_E4"+str(el_i)+str(el_t)+str(el_p))


    else:
        for el_t in xrange(S):
            for el_p in xrange(P):
                hcm.addConstr(ONRF(el_i,el_t,el_p) == 0.0, name='ONRF'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRQ(el_i,el_t,el_p) == 0.0)
print("Step 15 Done")
########################################################################################################################

###################################################### Eq 25-9 #########################################################
for el_i in xrange(NS):
    for el_t in xrange(S):
        for el_p in xrange(P):
                # Step 16: Calculate Mainline Output (1)
                # inequalities to approximate min functions - not likely to work
                # hcm.addConstr(MO1(el_i, el_t, el_p) - (SC[el_i][el_p] - ONRF(el_i, el_t, el_p)) <= 0)
                # hcm.addConstr(MO1(el_i, el_t, el_p) - MO2(el_i, el_t-1, el_p) <= 0)
                # hcm.addConstr(MO1(el_i, el_t, el_p) - MO3(el_i, el_t-1, el_p) <= 0)

                ########## Minimum #1: Min of SC-ONRF & MO2t-1
                hcm.addConstr(SC[el_i][el_p] - ONRF(el_i, el_t, el_p) - MO2(el_i, el_t-1, el_p)
                              <= big_m * MO1_I[el_i][el_t][el_p][0],
                              name='MO1_MIN1_1'+str(el_i)+str(el_t)+str(el_p)) # MO1_I0=1 => SC-ONRF > MO2
                hcm.addConstr(MO2(el_i, el_t-1, el_p) - SC[el_i][el_p] + ONRF(el_i, el_t, el_p)
                              <= big_m * (1 - MO1_I[el_i][el_t][el_p][0]),
                              name='MO1_MIN1_2'+str(el_i)+str(el_t)+str(el_p)) # MO1_I0=0 => SC-ONRF < MO2
                # If MO1_I0 = 0, setting MO1_A0 = SC-ONRF
                hcm.addConstr(MO1_A[el_i][el_t][el_p] - SC[el_i][el_p] + ONRF(el_i, el_t, el_p)
                              <= big_m * MO1_I[el_i][el_t][el_p][0],
                              name='MO1_MIN1_3'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MO1_A[el_i][el_t][el_p] - SC[el_i][el_p] + ONRF(el_i, el_t, el_p)
                              >= -1*big_m * MO1_I[el_i][el_t][el_p][0],
                              name='MO1_MIN1_4'+str(el_i)+str(el_t)+str(el_p))
                # If MO1_I0 = 1, setting MO1_A0 = MO2t-1
                hcm.addConstr(MO1_A[el_i][el_t][el_p] - MO2(el_i, el_t-1, el_p)
                              <= big_m * (1 - MO1_I[el_i][el_t][el_p][0]),
                              name='MO1_MIN1_5'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MO1_A[el_i][el_t][el_p] - MO2(el_i, el_t-1, el_p)
                              >= -1*big_m * (1 - MO1_I[el_i][el_t][el_p][0]),
                              name='MO1_MIN1_6'+str(el_i)+str(el_t)+str(el_p))

                ########## Minimum #2: Min of MO1_A & MO3t-1
                hcm.addConstr(MO1_A[el_i][el_t][el_p] - MO3(el_i, el_t-1, el_p)
                              <= big_m * MO1_I[el_i][el_t][el_p][1],
                              name='MO1_MIN2_1'+str(el_i)+str(el_t)+str(el_p)) # MO1_I1=1 => MO1_A > MO3
                hcm.addConstr(MO3(el_i, el_t-1, el_p) - MO1_A[el_i][el_t][el_p]
                              <= big_m * (1 - MO1_I[el_i][el_t][el_p][1]),
                              name='MO1_MIN2_2'+str(el_i)+str(el_t)+str(el_p)) # MO1_I1=0 => MO1_A < MO3
                # If MO1_I1 = 0, setting MO1 = MO1_A
                hcm.addConstr(MO1(el_i, el_t, el_p) - MO1_A[el_i][el_t][el_p]
                              <= big_m * MO1_I[el_i][el_t][el_p][1],
                              name='MO1_MIN2_3'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MO1(el_i, el_t, el_p) - MO1_A[el_i][el_t][el_p]
                              >= -1*big_m * MO1_I[el_i][el_t][el_p][1],
                              name='MO1_MIN2_4'+str(el_i)+str(el_t)+str(el_p))
                # If MO1_I1 = 1, setting MO1 = MO3t-1
                hcm.addConstr(MO1(el_i, el_t, el_p) - MO3(el_i, el_t-1, el_p)
                              <= big_m * (1 - MO1_I[el_i][el_t][el_p][1]),
                              name='MO1_MIN2_5'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MO1(el_i, el_t, el_p) - MO3(el_i, el_t-1, el_p)
                              >= -1*big_m * (1 - MO1_I[el_i][el_t][el_p][1]),
                              name='MO1_MIN2_6'+str(el_i)+str(el_t)+str(el_p))
print("step 16 done")
########################################################################################################################

###################################################### Eq 25-15 ########################################################
# Step 17: First Checking to see if a Queue is Present
M_UV = 10000     # TODO Maximum of UV?
uv_zero_tol = 0.001
for el_i in xrange(NS):
    for el_t in xrange(S):
        for (el_p) in xrange(P):
            hcm.addConstr(UV(el_i,el_t,el_p) - uv_zero_tol
                          <= M_UV* I_UV[el_i][el_t][el_p][0],
                          name="I_UV0"+str(el_i)+str(el_t)+str(el_p)) # I_UV0=1 => UV>0 (Queue Present)
            hcm.addConstr(uv_zero_tol - UV(el_i,el_t,el_p)
                          <= M_UV * (1 - I_UV[el_i][el_t][el_p][0]),
                          name="I_UV1"+str(el_i)+str(el_t)+str(el_p)) # I_UV0=0 => UV<=0 (No Queue Present)
            #hcm.addConstr(I_UV[el_i][el_t][el_p][0]+I_UV[el_i][el_t][el_p][1] == 1, name="I_UVE"+str(el_i)+str(el_t)+str(el_p))
print("step 17 done")

# Step 18 Is there a front clearing queue in this time interval
front_clearing_queue_present = []
for el_i in xrange(NS):
    front_clearing_queue_present.append([])
    for el_p in xrange(P):
        front_clearing_queue_present[el_i].append(((SC[el_i][el_p] - ONRD[el_i][el_p]) > (SC[el_i][el_p-1]-ONRD[el_i][el_p-1]))  # TODO p-1
            and (SC[el_i][el_p]-ONRD[el_i][el_p] > SD[el_i][el_p]))
print("step 18 done")

# Steps 19: Calculate Mainline Output 3
M_MO3=[]
for el_i in xrange(NS - 1):  # TODO Check NS minus 1?
    M_MO3.append([])
    for el_t in xrange(S):
        M_MO3[el_i].append([])
        for el_p in xrange(P):
            M_MO3[el_i][el_t].append([10000 for el in xrange(16)])  # TODO Appropriate estimation for M_MO3?

for el_i in xrange(NS - 1):  # TODO Check NS minus 1?
    for el_t in xrange(S):
        for el_p in xrange(P):
            if not front_clearing_queue_present[el_i][el_p]:
                # If there is no front clearing queue, this value is set to 1e6 and effectively ignored
                hcm.addConstr(MO3(el_i,el_t,el_p) == SC[el_i][el_p], name="MO3_NFCQ"+str(el_i)+str(el_t)+str(el_p))
            else :
                # Binary indicator variable constraint
                hcm.addConstr(MO3_I[el_i][el_t][el_p][0]+MO3_I[el_i][el_t][el_p][1] == 2 - I_UV[el_i][el_t][el_p][0],
                               name = "3.65"+str(el_i)+str(el_t)+str(el_p))
                # Minimum of MO1 and (MO2-OFRF)
                hcm.addConstr(MO1(el_i+1, el_t - WTT(el_i, el_p), el_p)
                    - (MO2(el_i+1, el_t-WTT(el_i, el_p), el_p) + OFRF(el_i+1, el_t-WTT(el_i, el_p), el_p))
                    <= M_MO3[el_i][el_t][el_p][0]*MO3_I[el_i][el_t][el_p][0], name = "3.63"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr((MO2(el_i+1, el_t-WTT(el_i, el_p), el_p) + OFRF(el_i+1, el_t-WTT(el_i, el_p), el_p))
                    - MO1(el_i+1, el_t - WTT(el_i, el_p), el_p)
                    <= M_MO3[el_i][el_t][el_p][0]*MO3_I[el_i][el_t][el_p][1], name = "3.64"+str(el_i)+str(el_t)+str(el_p))
                # Setting minimum to MO3_A[i][t][p][0]
                hcm.addConstr(MO3_A[el_i][el_t][el_p][0] - MO1(el_i+1, el_t - WTT(el_i, el_p), el_p)
                    >= -M_MO3[el_i][el_t][el_p][1]*MO3_I[el_i][el_t][el_p][0],
                              name = "3.66a"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MO3_A[el_i][el_t][el_p][0] - MO1(el_i+1, el_t - WTT(el_i, el_p), el_p)
                    <= M_MO3[el_i][el_t][el_p][1]*MO3_I[el_i][el_t][el_p][0],
                              name = "3.66b"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MO3_A[el_i][el_t][el_p][0] - (MO2(el_i+1, el_t-WTT(el_i, el_p), el_p) + OFRF(el_i+1, el_t-WTT(el_i, el_p), el_p))
                    >= -M_MO3[el_i][el_t][el_p][2]*MO3_I[el_i][el_t][el_p][1],
                              name = "3.67a"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MO3_A[el_i][el_t][el_p][0] - (MO2(el_i+1, el_t-WTT(el_i, el_p), el_p) + OFRF(el_i+1, el_t-WTT(el_i, el_p), el_p))
                    <= M_MO3[el_i][el_t][el_p][2]*MO3_I[el_i][el_t][el_p][1],
                              name = "3.67b"+str(el_i)+str(el_t)+str(el_p))
                # Minimum of MO3[i+1][t-WTT][p] and MO3_A
                hcm.addConstr(MO3_A[el_i][el_t][el_p][0]
                    - (MO3(el_i+1, el_t-WTT(el_i, el_p), el_p) + OFRF(el_i+1, el_t-WTT(el_i, el_p), el_p))
                    <= M_MO3[el_i][el_t][el_p][3]*MO3_I[el_i][el_t][el_p][2], name = "3.68"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr((MO3(el_i+1, el_t-WTT(el_i, el_p), el_p) + OFRF(el_i+1, el_t-WTT(el_i, el_p), el_p))
                    - MO3_A[el_i][el_t][el_p][0]
                    <= M_MO3[el_i][el_t][el_p][4]*MO3_I[el_i][el_t][el_p][3], name = "3.69"+str(el_i)+str(el_t)+str(el_p))
                # Binary indicator variable constraint
                hcm.addConstr(MO3_I[el_i][el_t][el_p][2]+MO3_I[el_i][el_t][el_p][3] == 2 - I_UV[el_i][el_t][el_p][0],
                        name = "3.70"+str(el_i)+str(el_t)+str(el_p))
                # Setting minimum to MO3_A[i][t][p][1]
                hcm.addConstr(MO3_A[el_i][el_t][el_p][1] - MO3_A[el_i][el_t][el_p][0]
                    >= - M_MO3[el_i][el_t][el_p][5]*MO3_I[el_i][el_t][el_p][2],
                              name = "3.71a"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MO3_A[el_i][el_t][el_p][1] - MO3_A[el_i][el_t][el_p][0]
                    <= M_MO3[el_i][el_t][el_p][5]*MO3_I[el_i][el_t][el_p][2],
                              name = "3.71b"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MO3_A[el_i][el_t][el_p][1] - (MO3(el_i+1, el_t-WTT(el_i, el_p), el_p) + OFRF(el_i+1, el_t-WTT(el_i, el_p), el_p))
                    >= - M_MO3[el_i][el_t][el_p][6]*MO3_I[el_i][el_t][el_p][3],
                              name = "3.72a"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MO3_A[el_i][el_t][el_p][1] - (MO3(el_i+1, el_t-WTT(el_i, el_p), el_p) + OFRF(el_i+1, el_t-WTT(el_i, el_p), el_p))
                    <= M_MO3[el_i][el_t][el_p][6]*MO3_I[el_i][el_t][el_p][3],
                              name = "3.72b"+str(el_i)+str(el_t)+str(el_p))
                # Minimum of MO3_A[i][t][p][1] and SC[i][p]
                temp_sc = generate_sc(el_i, el_t-WTT(el_i, el_p), el_p)
                hcm.addConstr(MO3_A[el_i][el_t][el_p][1] - temp_sc
                    <=M_MO3[el_i][el_t][el_p][7]*MO3_I[el_i][el_t][el_p][4],
                              name = "3.73"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(temp_sc - MO3_A[el_i][el_t][el_p][1]
                    <=M_MO3[el_i][el_t][el_p][8]*MO3_I[el_i][el_t][el_p][5],
                              name = "3.74"+str(el_i)+str(el_t)+str(el_p))
                # Binary Indicator variable constraint
                hcm.addConstr(MO3_I[el_i][el_t][el_p][4]+MO3_I[el_i][el_t][el_p][5] == 2-I_UV[el_i][el_t][el_p][0],
                              name = "3.75"+str(el_i)+str(el_t)+str(el_p))
                # Setting minimum to MO3_A[i][t][p][2]
                hcm.addConstr(MO3_A[el_i][el_t][el_p][2] - MO3_A[el_i][el_t][el_p][1]
                    >= - M_MO3[el_i][el_t][el_p][9]*MO3_I[el_i][el_t][el_p][4],
                              name = "3.76a"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MO3_A[el_i][el_t][el_p][2] - MO3_A[el_i][el_t][el_p][1]
                    <= M_MO3[el_i][el_t][el_p][9]*MO3_I[el_i][el_t][el_p][4],
                              name = "3.76b"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MO3_A[el_i][el_t][el_p][2] - temp_sc
                    >= - M_MO3[el_i][el_t][el_p][10]*MO3_I[el_i][el_t][el_p][5],
                              name = "3.77a"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MO3_A[el_i][el_t][el_p][2] - temp_sc
                    <= M_MO3[el_i][el_t][el_p][10]*MO3_I[el_i][el_t][el_p][5],
                              name = "3.77b"+str(el_i)+str(el_t)+str(el_p))
                # Minimum of MO3_A[i][t][p][2] and SC+OFRF
                temp_sc = generate_sc(el_i+1, el_t-WTT(el_i, el_p), el_p)
                hcm.addConstr(MO3_A[el_i][el_t][el_p][2] - (temp_sc+OFRF(el_i+1, el_t-WTT(el_i, el_p), el_p))
                    <=M_MO3[el_i][el_t][el_p][11]*MO3_I[el_i][el_t][el_p][6],
                              name = "3.78"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr((temp_sc+OFRF(el_i+1, el_t-WTT(el_i, el_p), el_p)) - MO3_A[el_i][el_t][el_p][1]
                    <=M_MO3[el_i][el_t][el_p][11]*MO3_I[el_i][el_t][el_p][7],
                              name = "3.79"+str(el_i)+str(el_t)+str(el_p))
                # Binary Indicator variable constraints
                hcm.addConstr(MO3_I[el_i][el_t][el_p][6]+MO3_I[el_i][el_t][el_p][7] == 2-I_UV[el_i][el_t][el_p][0],
                              name = "3.80"+str(el_i)+str(el_t)+str(el_p))
                # Setting minimum to MO3_A[i][t][p][3]
                hcm.addConstr(MO3_A[el_i][el_t][el_p][3] - MO3_A[el_i][el_t][el_p][2]
                    >= - M_MO3[el_i][el_t][el_p][12]*MO3_I[el_i][el_t][el_p][6],
                              name = "3.81a"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MO3_A[el_i][el_t][el_p][3] - MO3_A[el_i][el_t][el_p][2]
                    <= M_MO3[el_i][el_t][el_p][12]*MO3_I[el_i][el_t][el_p][6],
                              name = "3.81b"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MO3_A[el_i][el_t][el_p][3] - (temp_sc+OFRF(el_i+1, el_t-WTT(el_i, el_p), el_p))
                    >= - M_MO3[el_i][el_t][el_p][13]*MO3_I[el_i][el_t][el_p][7],
                              name = "3.82a"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MO3_A[el_i][el_t][el_p][3] - (temp_sc+OFRF(el_i+1, el_t-WTT(el_i, el_p), el_p))
                    <= M_MO3[el_i][el_t][el_p][13]*MO3_I[el_i][el_t][el_p][7],
                              name = "3.82b"+str(el_i)+str(el_t)+str(el_p))
                # Setting to MO3[i][t][p], or setting MO3[i][t][p] to a large value if no front clearing queue
                hcm.addConstr(MO3(el_i,el_t,el_p) - (MO3_A[el_i][el_t][el_p][3] - ONRF(el_i, el_t, el_p))
                    >= - M_MO3[el_i][el_t][el_p][14]*(1-I_UV[el_i][el_t][el_p][0]),
                              name = "3.83a"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MO3(el_i,el_t,el_p) - (MO3_A[el_i][el_t][el_p][3] - ONRF(el_i, el_t, el_p))
                    <= M_MO3[el_i][el_t][el_p][14]*(1-I_UV[el_i][el_t][el_p][0]),
                              name = "3.83b"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MO3(el_i,el_t,el_p) - M_MO3[el_i][el_t][el_p][15]
                    >= - M_MO3[el_i][el_t][el_p][15]*(I_UV[el_i][el_t][el_p][0]),
                              name = "3.84a"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MO3(el_i,el_t,el_p) - M_MO3[el_i][el_t][el_p][15]
                    <= M_MO3[el_i][el_t][el_p][15]*(I_UV[el_i][el_t][el_p][0]),
                              name = "3.84b"+str(el_i)+str(el_t)+str(el_p))
print("step 19 done")

########################################################################################################################


###################################################### Eq 25-10 ########################################################
# Step 20: Calculate density of queue on segment
for el_i in xrange(NS):  # TODO -1?
    for el_t in xrange(S):  # Todo account for "t-1"
        for el_p in xrange(P):
            hcm.addConstr(KQ[el_i][el_t][el_p] == KJ - ((KJ-KC)/SC[el_i][el_p])*SF(el_i+1, el_t-1, el_p),
                          name="3.85"+str(el_i)+str(el_t)+str(el_p))
print("step 20 done")
########################################################################################################################


###################################################### Eq 25-11 ########################################################
# Step 21: Calculate Mainline Output 2
M_MO2 = 10000
for el_i in xrange(NS):  # TODO -1?
    for el_t in xrange(S):  # Todo account for "t-1" (MF/OFRF/ONRF/NV) (NV fixed)
        for el_p in xrange(P):
            #hcm.addConstr(MO2(el_i, el_t, el_p) == MF(el_i+1, el_t-1, el_p) + OFRF(el_i+1, el_t-1, el_p) - ONRF(el_i, el_t-1, el_p)+(L[el_i]*KQ[el_i][el_t][el_p]) - NV(el_i, el_t-1, el_p), name="3.86"+str(el_i)+str(el_t)+str(el_p))
            hcm.addConstr(MO2(el_i, el_t, el_p)
                          - MF(el_i+1, el_t-1, el_p)
                          - OFRF(el_i+1, el_t-1, el_p)
                          + ONRF(el_i, el_t-1, el_p)
                          - (L[el_i]*KQ[el_i][el_t][el_p])
                          + NV(el_i, el_t-1, el_p)
                          <= M_MO2*I_UV[el_i][el_t][el_p][1],
                          name="3.86"+str(el_i)+str(el_t)+str(el_p))
            hcm.addConstr(MO2(el_i, el_t, el_p)
                          - MF(el_i+1, el_t-1, el_p)
                          - OFRF(el_i+1, el_t-1, el_p)
                          + ONRF(el_i, el_t-1, el_p)
                          - (L[el_i]*KQ[el_i][el_t][el_p])
                          + NV(el_i, el_t-1, el_p)
                          >= -M_MO2*I_UV[el_i][el_t][el_p][1],
                          name="3.86"+str(el_i)+str(el_t)+str(el_p))
            hcm.addConstr(MO2(el_i, el_t, el_p) - SC[el_i][el_p]
                          <= M_MO2*I_UV[el_i][el_t][el_p][0],
                          name="3.86"+str(el_i)+str(el_t)+str(el_p))
            hcm.addConstr(MO2(el_i, el_t, el_p) - SC[el_i][el_p]
                          >= -M_MO2*I_UV[el_i][el_t][el_p][0],
                          name="3.86"+str(el_i)+str(el_t)+str(el_p))


# hcm.update()
# hcm.optimize()
# varCount = 0
# for p in xrange(P):
#     for t in xrange(S):
#         for i in xrange(NS):
#             varCount+=1
#             print(str(varCount)
#                   + ", "+ str(i)
#                   + ", " + str(p)
#                   + ", " + str(t)
#                   + ", " + str(NV(i,t, p).X)
#                   + ", " + str(MF(i,t, p).X/240.0)
#                   + ", " + str(MI[i][t][p].X/240.0)
#                   + ", " + str(MO1(i,t, p).X/240.0)
#                   + ", " + str(MO2(i,t, p).X/240.0)
#                   + ", " + str(MO3(i,t, p).X/240.0)
#                   #+ ", " + str(ONRI[i][t][p].X)
#                   #+ ", " + str(ONRD[i][p])
#                   #+ ", " + str(ONRQ(i,t, p).X)
#                   #+ ", " + str(ONRF_I[i][t][p][0].X)
#                   #+ ", " + str(ONRF_I[i][t][p][1].X)
#                   #+ ", " + str(ONRO[i][t][p].X)
#                   + ", " + str(ONRF(i,t, p).X/240.0)
#                   + ", " + str(OFRF(i,t, p).X/240.0)
#                   + ", " + str(DEF_A[i][t][p].X))

print("step 21 done")
# Step 22: Calculate Mainline Flow
M_MF=[]
for el_i in xrange(NS):  # TODO Check NS minus 1?
    M_MF.append([])
    for el_t in xrange(S):
        M_MF[el_i].append([])
        for el_p in xrange(P):
            #M_MF[el_i][el_t].append([SC[el_i][el_p] for el in xrange(15)])  # TODO Appropriate estimation for M_MO3?
            M_MF[el_i][el_t].append([10000 for el in xrange(15)])

for el_i in xrange(NS):
    for el_t in xrange(S):
        for el_p in xrange(P):
            # Mininum of Mainline Input (MI) and Mainline Output 1 (MO1)
            hcm.addConstr(MI[el_i][el_t][el_p] - MO1(el_i, el_t, el_p)
                    <= M_MF[el_i][el_t][el_p][0] * MF_I[el_i][el_t][el_p][0],
                          name="3.87"+str(el_i)+str(el_t)+str(el_p))
            hcm.addConstr(MO1(el_i, el_t, el_p) - MI[el_i][el_t][el_p]
                    <= M_MF[el_i][el_t][el_p][0] * MF_I[el_i][el_t][el_p][1],
                          name="3.88"+str(el_i)+str(el_t)+str(el_p))
            # Binary indicator variable constraint
            if use_sos:
                    hcm.addSOS(gbp.GRB.SOS_TYPE1, [MF_I[el_i][el_t][el_p][0],MF_I[el_i][el_t][el_p][1]])
            else:
                hcm.addConstr(MF_I[el_i][el_t][el_p][0] + MF_I[el_i][el_t][el_p][1] == 1,
                              name="3.89"+str(el_i)+str(el_t)+str(el_p))
            # Setting minimum to MF_A[i][t][p][0]
            hcm.addConstr(MF_A[el_i][el_t][el_p][0] - MI[el_i][el_t][el_p]
                <= M_MF[el_i][el_t][el_p][1] * MF_I[el_i][el_t][el_p][0],
                          name="3.90a"+str(el_i)+str(el_t)+str(el_p))
            hcm.addConstr(MF_A[el_i][el_t][el_p][0] - MI[el_i][el_t][el_p]
                >= -M_MF[el_i][el_t][el_p][1] * MF_I[el_i][el_t][el_p][0],
                          name="3.90b"+str(el_i)+str(el_t)+str(el_p))
            hcm.addConstr(MF_A[el_i][el_t][el_p][0] - MO1(el_i, el_t, el_p)
                <= M_MF[el_i][el_t][el_p][2] * MF_I[el_i][el_t][el_p][1],
                          name="3.91a"+str(el_i)+str(el_t)+str(el_p))
            hcm.addConstr(MF_A[el_i][el_t][el_p][0] - MO1(el_i, el_t, el_p)
                >= -M_MF[el_i][el_t][el_p][2] * MF_I[el_i][el_t][el_p][1],
                          name="3.91b"+str(el_i)+str(el_t)+str(el_p))

            # Minimum of MF_A[i][t][p][0] and Mainline Output 2 (MO2)
            hcm.addConstr(MF_A[el_i][el_t][el_p][0] - MO2(el_i, el_t, el_p)
                    <= M_MF[el_i][el_t][el_p][3] * MF_I[el_i][el_t][el_p][2],
                          name="3.92"+str(el_i)+str(el_t)+str(el_p))
            hcm.addConstr(MO2(el_i, el_t, el_p) - MF_A[el_i][el_t][el_p][0]
                    <= M_MF[el_i][el_t][el_p][3] * MF_I[el_i][el_t][el_p][3],
                          name="3.93"+str(el_i)+str(el_t)+str(el_p))
            # Binary indicator variable constraint
            if use_sos:
                    hcm.addSOS(gbp.GRB.SOS_TYPE1, [MF_I[el_i][el_t][el_p][2],MF_I[el_i][el_t][el_p][3]])
            else:
                hcm.addConstr(MF_I[el_i][el_t][el_p][2] + MF_I[el_i][el_t][el_p][3] == 1,
                          name="3.94"+str(el_i)+str(el_t)+str(el_p))
            # Setting minimum to MF_A[i][t][p][1]
            hcm.addConstr(MF_A[el_i][el_t][el_p][1] - MF_A[el_i][el_t][el_p][0]
                <= M_MF[el_i][el_t][el_p][4] * MF_I[el_i][el_t][el_p][2],
                          name="3.95a"+str(el_i)+str(el_t)+str(el_p))
            hcm.addConstr(MF_A[el_i][el_t][el_p][1] - MF_A[el_i][el_t][el_p][0]
                >= -M_MF[el_i][el_t][el_p][4] * MF_I[el_i][el_t][el_p][2],
                          name="3.95b"+str(el_i)+str(el_t)+str(el_p))
            hcm.addConstr(MF_A[el_i][el_t][el_p][1] - MO2(el_i, el_t, el_p)
                <= M_MF[el_i][el_t][el_p][5] * MF_I[el_i][el_t][el_p][3],
                          name="3.96a"+str(el_i)+str(el_t)+str(el_p))
            hcm.addConstr(MF_A[el_i][el_t][el_p][1] - MO2(el_i, el_t, el_p)
                >= -M_MF[el_i][el_t][el_p][5] * MF_I[el_i][el_t][el_p][3],
                          name="3.96b"+str(el_i)+str(el_t)+str(el_p))

            # Minimum of MF_A[i][t][p][1] and Mainline Output 3 (MO3)
            hcm.addConstr(MF_A[el_i][el_t][el_p][1] - MO3(el_i, el_t, el_p)
                    <= M_MF[el_i][el_t][el_p][6] * MF_I[el_i][el_t][el_p][4],
                          name="3.97"+str(el_i)+str(el_t)+str(el_p))
            hcm.addConstr(MO3(el_i, el_t, el_p) - MF_A[el_i][el_t][el_p][1]
                    <= M_MF[el_i][el_t][el_p][6] * MF_I[el_i][el_t][el_p][5],
                          name="3.98"+str(el_i)+str(el_t)+str(el_p))
            # Binary indicator variable constraint
            if use_sos:
                    hcm.addSOS(gbp.GRB.SOS_TYPE1, [MF_I[el_i][el_t][el_p][4],MF_I[el_i][el_t][el_p][5]])
            else:
                hcm.addConstr(MF_I[el_i][el_t][el_p][4] + MF_I[el_i][el_t][el_p][5] == 1,
                          name="3.99"+str(el_i)+str(el_t)+str(el_p))
            # Setting minimum to MF_A[i][t][p][2]
            hcm.addConstr(MF_A[el_i][el_t][el_p][2] - MF_A[el_i][el_t][el_p][1]
                <= M_MF[el_i][el_t][el_p][7] * MF_I[el_i][el_t][el_p][4],
                          name="3.100a"+str(el_i)+str(el_t)+str(el_p))
            hcm.addConstr(MF_A[el_i][el_t][el_p][2] - MF_A[el_i][el_t][el_p][1]
                >= -M_MF[el_i][el_t][el_p][7] * MF_I[el_i][el_t][el_p][4],
                          name="3.100b"+str(el_i)+str(el_t)+str(el_p))
            hcm.addConstr(MF_A[el_i][el_t][el_p][2] - MO3(el_i, el_t, el_p)
                <= M_MF[el_i][el_t][el_p][8] * MF_I[el_i][el_t][el_p][5],
                          name="3.101a"+str(el_i)+str(el_t)+str(el_p))
            hcm.addConstr(MF_A[el_i][el_t][el_p][2] - MO3(el_i, el_t, el_p)
                >= -M_MF[el_i][el_t][el_p][8] * MF_I[el_i][el_t][el_p][5],
                          name="3.101b"+str(el_i)+str(el_t)+str(el_p))

            # Minimum of MF_A[i][t][p][2] and Segment Capacity (SC) of current segment (of loop)
            hcm.addConstr(MF_A[el_i][el_t][el_p][2] - SC[el_i][el_p]
                    <= M_MF[el_i][el_t][el_p][9] * MF_I[el_i][el_t][el_p][6],
                          name="3.102"+str(el_i)+str(el_t)+str(el_p))
            hcm.addConstr(SC[el_i][el_p] - MF_A[el_i][el_t][el_p][2]
                    <= M_MF[el_i][el_t][el_p][9] * MF_I[el_i][el_t][el_p][7],
                          name="3.103"+str(el_i)+str(el_t)+str(el_p))
            # Binary indicator variable constraint
            if use_sos:
                    hcm.addSOS(gbp.GRB.SOS_TYPE1, [MF_I[el_i][el_t][el_p][6],MF_I[el_i][el_t][el_p][7]])
            else:
                hcm.addConstr(MF_I[el_i][el_t][el_p][6] + MF_I[el_i][el_t][el_p][7] == 1,
                          name="3.104"+str(el_i)+str(el_t)+str(el_p))
            # Setting minimum to MF_A[i][t][p][3]
            hcm.addConstr(MF_A[el_i][el_t][el_p][3] - MF_A[el_i][el_t][el_p][2]
                <= M_MF[el_i][el_t][el_p][10] * MF_I[el_i][el_t][el_p][6],
                          name="3.105a"+str(el_i)+str(el_t)+str(el_p))
            hcm.addConstr(MF_A[el_i][el_t][el_p][3] - MF_A[el_i][el_t][el_p][2]
                >= -M_MF[el_i][el_t][el_p][10] * MF_I[el_i][el_t][el_p][6],
                          name="3.105b"+str(el_i)+str(el_t)+str(el_p))
            hcm.addConstr(MF_A[el_i][el_t][el_p][3] - SC[el_i][el_p]
                <= M_MF[el_i][el_t][el_p][11] * MF_I[el_i][el_t][el_p][7],
                          name="3.106a"+str(el_i)+str(el_t)+str(el_p))
            hcm.addConstr(MF_A[el_i][el_t][el_p][3] - SC[el_i][el_p]
                >= -M_MF[el_i][el_t][el_p][11] * MF_I[el_i][el_t][el_p][7],
                          name="3.106b"+str(el_i)+str(el_t)+str(el_p))

            if el_i > 0: # Only consider if not 1st segment
                # Minimum of MF_A[i][t][p][3] and Segment Capacity (SC) of previous segment
                hcm.addConstr(MF_A[el_i][el_t][el_p][3] - SC[el_i - 1][el_p]
                        <= M_MF[el_i][el_t][el_p][12] * MF_I[el_i][el_t][el_p][8],
                              name="3.107"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(SC[el_i - 1][el_p] - MF_A[el_i][el_t][el_p][3]
                        <= M_MF[el_i][el_t][el_p][12] * MF_I[el_i][el_t][el_p][9],
                              name="3.108"+str(el_i)+str(el_t)+str(el_p))
                # Binary indicator variable constraint
                if use_sos:
                    hcm.addSOS(gbp.GRB.SOS_TYPE1, [MF_I[el_i][el_t][el_p][8],MF_I[el_i][el_t][el_p][9]])
                else:
                    hcm.addConstr(MF_I[el_i][el_t][el_p][8] + MF_I[el_i][el_t][el_p][9] == 1,
                              name="3.109"+str(el_i)+str(el_t)+str(el_p))
                # Setting minimum to MF[i][t][p]
                hcm.addConstr(MF(el_i,el_t,el_p) - MF_A[el_i][el_t][el_p][3]
                        <= M_MF[el_i][el_t][el_p][13] * MF_I[el_i][el_t][el_p][8],
                              name="3.110a"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MF(el_i,el_t,el_p) - MF_A[el_i][el_t][el_p][3]
                        >= -M_MF[el_i][el_t][el_p][13] * MF_I[el_i][el_t][el_p][8],
                              name="3.110b"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MF(el_i,el_t,el_p) - SC[el_i-1][el_p]
                        <= M_MF[el_i][el_t][el_p][14] * MF_I[el_i][el_t][el_p][9],
                              name="3.111a"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MF(el_i,el_t,el_p) - SC[el_i-1][el_p]
                        >= -M_MF[el_i][el_t][el_p][14] * MF_I[el_i][el_t][el_p][9],
                              name="3.111b"+str(el_i)+str(el_t)+str(el_p))
            else:
                hcm.addConstr(MF(el_i,el_t,el_p) == MF_A[el_i][el_t][el_p][3],
                              name="3.111a"+str(el_i)+str(el_t)+str(el_p))


print("step 22 done")
#hcm.update()
#hcm.optimize()
# Step 23: First segment?
# Step 24: Calculate segment flow
for el_i in xrange(NS):
    for el_t in xrange(S):
        for el_p in xrange(P):
            hcm.addConstr(SF(el_i, el_t, el_p) == MF(el_i+1,el_t,el_p) + OFRF(el_i+1, el_t, el_p),
                          name="3.112"+str(el_i)+str(el_t)+str(el_p))

#hcm.update()
print("step 24 done")
# Step 25: Update number of vehicles and unserved vehicles on the segment
for el_i in xrange(NS):  # TODO: NS-1 correct? If so specify value for NV[0][t][p] & UV[0] (0?)
    for el_t in xrange(S):
        for el_p in xrange(P):
            # Constraint determining number of vehicles on the segment
            hcm.addConstr(NV(el_i, el_t, el_p) == NV(el_i, el_t-1, el_p) + MF(el_i, el_t, el_p)
                        + ONRF(el_i, el_t, el_p) - MF(el_i+1, el_t, el_p) - OFRF(el_i+1 , el_t, el_p),
                        name="3.113" +str(el_i)+str(el_t)+str(el_p))

            # Constraint updating the number of unserved vehicles
            hcm.addConstr(UV(el_i, el_t, el_p) == NV(el_i, el_t, el_p) - KB[el_i][el_p]*L[el_i],
                          name = "3.114"+str(el_i)+str(el_t)+str(el_p))
print("step 25 done")
hcm.update()
model_build_time=time.time()
print("Model Built: "+str(model_build_time - init_time))
#hcm.setParam(gbp.GRB.param.ConcurrentMIP, 32)
# hcm.write("hcm.mst")
hcm.optimize()
optimize_finish_time = time.time()
print("Model Solved: "+str(optimize_finish_time - model_build_time))
#
varCount = 0
if printFile:
    f = open("output.txt", "w")
    for p in xrange(P):
        for t in xrange(S):
            for i in xrange(NS):
                varCount+=1
                f.write(str(varCount)
                      + ", "+ str(i)
                      + ", " + str(p)
                      + ", " + str(t)
                      + ", " + str(NV(i,t, p).X)
                      + ", " + str(MF(i,t, p).X/240.0)
                      + ", " + str(MI[i][t][p].X/240.0)
                      + ", " + str(MO1(i,t, p).X/240.0)
                      + ", " + str(MO2(i,t, p).X/240.0)
                      + ", " + str(MO3(i,t, p).X/240.0)
                      #+ ", " + str(ONRI[i][t][p].X)
                      #+ ", " + str(ONRD[i][p])
                      #+ ", " + str(ONRQ(i,t, p).X)
                      #+ ", " + str(ONRF_I[i][t][p][0].X)
                      #+ ", " + str(ONRF_I[i][t][p][1].X)
                      #+ ", " + str(ONRO[i][t][p].X)
                      + ", " + str(ONRF(i,t, p).X/240.0)
                      + ", " + str(OFRF(i,t, p).X/240.0)
                      + ", " + str(DEF_A[i][t][p].X)
                      + ", " + str(DEF[i][t][p].X)
                      + ", " + str(UV(i,t,p).X)
                      + ", " + str(I_UV[i][t][p][0].X)
                      + ", " + str(I_UV[i][t][p][1].X)+"\n")
    f.close()
# else:
#     for p in xrange(P):
#         for t in xrange(S):
#             for i in xrange(NS):
#                 varCount+=1
#                 print(str(varCount)
#                       + ", "+ str(i)
#                       + ", " + str(p)
#                       + ", " + str(t)
#                       + ", " + str(NV(i,t, p).X)
#                       + ", " + str(MF(i,t, p).X/240.0)
#                       + ", " + str(MI[i][t][p].X/240.0)
#                       + ", " + str(MO1(i,t, p).X/240.0)
#                       + ", " + str(MO2(i,t, p).X/240.0)
#                       + ", " + str(MO3(i,t, p).X/240.0)
#                       #+ ", " + str(ONRI[i][t][p].X)
#                       #+ ", " + str(ONRD[i][p])
#                       #+ ", " + str(ONRQ(i,t, p).X)
#                       #+ ", " + str(ONRF_I[i][t][p][0].X)
#                       #+ ", " + str(ONRF_I[i][t][p][1].X)
#                       #+ ", " + str(ONRO[i][t][p].X)
#                       + ", " + str(ONRF(i,t, p).X/240.0)
#                       + ", " + str(OFRF(i,t, p).X/240.0)
#                       + ", " + str(DEF_A[i][t][p].X)
#                       + ", " + str(DEF[i][t][p].X)
#                       + ", " + str(UV(i,t,p).X)
#                       + ", " + str(I_UV[i][t][p][0].X)
#                       + ", " + str(I_UV[i][t][p][1].X))


# Set Lower/Upper Bounds