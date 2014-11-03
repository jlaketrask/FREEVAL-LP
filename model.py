from __future__ import division
import gurobipy as gbp
from pylab import *
from constraintGenerator import generate_max_constrs, generate_min_constrs, sum_add_t, sum_sum_add_t_p
__author__ = 'jltrask'

######## Model Parameters
# Indices and basic Freeway geometry parameters
NS = 7  # number of segments
Stilde = [el for el in xrange(7)]
Ftilde = [5]  # List of OFR segments
Ntilde = [2]  # List of ONR segments
P = 4  # number of time intervals (periods) in the analysis period
Ptilde = [el for el in xrange(P)]  # List of time intervals
S = 4 * 15  # Number of time steps in a single interval (each step is 15 seconds)
Ttilde = [el for el in xrange(S)]  # List of time steps
Th = 240  # Number of time stes in 1 hour

# Constants
KC = 45  # Ideal Density at capacity
KJ = 190  # Facility-wide jam density
L = [2640 for el in xrange(NS)]  # Length of each segment
SC = ones((NS, P))  # Segment capacity of segment i in interval p
mainline_demand = 4000
SD = mainline_demand*ones((NS, P))  # Segment demand for segment i in time interval p
N = 3 * ones((NS, P))  # Number of open lanes in segment i in interval p
WS = lambda i, p: SC[i][p]/(N[i][p] * (KJ-KC))  # Wave speed for segment i in interval p
WTT = lambda i, p: Th * (L[i]/WS(i, p))  # Wave travel time
ONRD = [[1000 if el_i in Ntilde else 0 for el_p in xrange(P)] for el_i in xrange(NS)]  # Demand flow rate for ONR at node i in interval p
ONRC = [[[2400 if el_i in Ntilde else 0 for el_p in xrange(P)] for el_t in xrange(S)] for el_i in xrange(NS)]  # Geometric capacity of ONR at node i in period t in interval p
RM = [[2400 if el_i in Ntilde else 0 for el_p in xrange(P)] for el_i in xrange(NS)]  # Ramp metering rate of node i during interval p (veh/h)
OFRD = [[1000 if el_i in Ftilde else 0 for el_p in xrange(P)] for el_i in xrange(NS)]  # Demand flow rate for OFR at node i in interval p

######## Creating Gurobi Model
# Initializing model instance
hcm = gbp.Model("hcm-test")

# Creating linear decision variables
EDv = []  # Expected dmand that would arrive at segment i over inteval p
for el_i in xrange(NS):
    EDv.append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ED' + str(el_i) + str(el_p)) for el_p in xrange(P)])
ED = lambda i, p: min(SD[0][p], SC[0][p]) if i is 0 else EDv[i][p]
KB = []  # Background density of segment i during time interval p
for el_i in xrange(NS):
    KB.append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='KB' + str(el_i) + str(el_p)) for el_p in xrange(P)])
KQ = []  # Queue density: vechicle density in the queue on segment i in step t in interval p
for el_i in xrange(NS):
    KQ.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='KQ'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
MF = []  # Actual mainline flow rate in node i during step t in interval p
for el_i in xrange(NS):
    MF.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='MF'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
SF = []  # Segment flow out of segment i during step t in interval p
for el_i in xrange(NS):
    SF.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='SF'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
MI = []  # Maximum mainline input: max flow desiring to enter segment i during step t in interval p
for el_i in xrange(NS):
    MI.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='MI'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
ONRF = []  # Actual ONR flow rate that can cross on ramp node i during step t in interval p
for el_i in xrange(NS):
    ONRF.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRF'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
ONRI = []  # Input flow rate desiring to enter the merge point at ONR node i during step t in interval p
for el_i in xrange(NS):
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
for el_i in xrange(NS):
    ONRO.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRO'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
DEF = []  # Deficit in flow at segment i at time step t in interval p
for el_i in xrange(NS):
    DEF.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='DEF'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
OFRF = []  # Actual flow that can exit at OFR node i during step t in interval p
for el_i in xrange(NS):
    OFRF.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='OFRF'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
UVv = []  # Unserved vehicles: additional # of vehicles stored in segment i at the end of step t in interval p
for el_i in xrange(NS):
    UVv.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='UV'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
#UV = lambda i, t, p: 0 if p is -1 else UVv[i][t][p]
def UV(i, t, p):
    if p < 0 or (p is 0 and t < 0):
        return 0
    elif t < 0:
        return UVv[i][S-1][p-1]  # TODO correct?
    else:
        return UVv[i][t][p]
MO1 = []  # Max mainline output 1: limited by ONR flow at segment i
for el_i in xrange(NS):
    MO1.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='MO1'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
MO2v = []  # Max mainline output 2: limited by available storage on segment i due to a downstream queue
for el_i in xrange(NS):
    MO2v.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='MO2'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
def MO2(i, t, p):
    if t < 0:
        if p is 0:
            return 0                  # TODO correcct?
        else:
            return MO2v[i][S-1][p-1]
    else:
        return MO2v[i][t][p]
MO3v = []  # Max mainline output 3: limited by the presence of qued vech at the upstream in up segment i while the queue clears from the downstream end of segment i
for el_i in xrange(NS):
    MO3v.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='MO3'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
def MO3(i, t, p):
    if t < 0:
        if p is 0:
            return 0                  # TODO correcct?
        else:
            return MO3v[i][S-1][p-1]
    else:
        return MO3v[i][t][p]
NV = []  # NV in segment i at step t in interval p
for el_i in xrange(NS):
    NV.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='NV'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S+1)])

# Integrating variables into model
hcm.update()

# Set objective
#hcm.setObjective()

# Adding equality/inquality constraints
# Step 1: Calculate background density for each segment in current time interval
ED_I = []
bigM = max(max(SC), max(SD)+max(ONRD))  # TODO should be okay
for el_i in xrange(1, NS):  # Estimated demand for the first segment is minimum of capacity and mainline demand for that period so no constraint needed (predetermined and accounted for in lambda function ED)
    ED_I.append([])
    for el_p in xrange(P):
        # Creating binary variables
        ED_I[el_i].append([hcm.addVar(vtype=gbp.GRB.BINARY, name='ED_I'+str(ii)+str(el_i)+str(el_p)) for ii in xrange(2)])  # TODO put with initial variable declaration
        hcm.update()
        # Min constraint #1
        hcm.addConstr(SC[el_i][el_p] - ED(el_i-1, el_p) - ONRD[el_i][el_p] + OFRD[el_i][el_p] <= bigM*ED_I[el_i][el_p][0], name="ED_Min1"+str(el_i)+str(el_p))
        # Min constraint #2
        hcm.addConstr(ED(el_i-1, el_p) + ONRD[el_i][el_p] - OFRD[el_i][el_p] - SC[el_i][el_p] <= bigM*ED_I[el_i][el_p][1], name="ED_Min2"+str(el_i)+str(el_p))
        # Constraint that one has to be true
        hcm.addConstr(ED_I[el_i][el_p][0] + ED_I[el_i][el_p][1] == 1, name="ED_Min3"+str(el_i)+str(el_p))
        # Constraint assigning minimum value to EDip
        bigM1 = 10000  # TODO calculate real value
        bigM2 = 10000  # TODO calculate real value
        hcm.addConstr(ED(el_i, el_p) - SC[el_i][el_p] <= bigM1*ED_I[el_i][el_p][0], name='ED_D1'+str(el_i)+str(el_p))
        hcm.addConstr(SC[el_i][el_p] - ED(el_i, el_p) <= bigM1*ED_I[el_i][el_p][0], name='ED_D2'+str(el_i)+str(el_p))
        hcm.addConstr(ED(el_i, el_p) - ED(el_i-1, el_p) - ONRD[el_i][el_p] + OFRD[el_i][el_p] <= bigM2*ED_I[el_i][el_p][1], name='ED_D3'+str(el_i)+str(el_p))
        hcm.addConstr(ED(el_i-1, el_p) + ONRD[el_i][el_p] - OFRD[el_i][el_p] - ED(el_i, el_p) <= bigM2*ED_I[el_i][el_p][1], name='ED_D4'+str(el_i)+str(el_p))

# hcm.update()

#Step 2: initialize the Freeway Facility
##### Need to calculate KB from Undersat
# Updateing # of vehicles - note t goes from 0 to S (i.e. S+1 steps) for NV, with 0 being  "before" interval p starts.
for el_i in xrange(NS):
    for el_p in xrange(P):  # Note that the lambda function on UV accounts for the case p = -1 (UV = 0 in that case)
        hcm.addConstr(NV[el_i][0][el_p] == KB[el_i][el_p]*L[el_i] + UV(el_i, S-1, el_p-1), name='NV_E'+str(el_i)+str(0)+str(el_p))

# Steps 3-4: Begin "loops" of vall segments, all time steps
# Steps 5-8: OFR Segment constraints
OFRF_I = []
for el_i in xrange(0, NS):
    OFRF_I.append([])
    if el_i in Ftilde:  # Check if OFR at segment
        # Calculate possible deficit from upstream queue
        sum_sd = sum(SD[el_i-1][0:el_p])  # Sum of segment demand in previous segment
        for el_t in xrange(S):
            OFRF_I[el_i-1].append([])
            for el_p in xrange(P):
                a1 = sum_sd + sum_sum_add_t_p(MF, ONRF, el_i-1, S-1, el_p-1) + sum_add_t(MF, ONRF, el_i-1, el_t-1, el_p)
                big_m = 10000  # TODO calculate
                big_m1 = 10000  # TODO calculate
                big_m2 = 10000  # TODO calculate
                generate_max_constrs(hcm, DEF[el_i][el_t][el_p], 0, a1, big_m, big_m1, big_m2, 'DEF_E', str(el_i)+str(el_t)+str(el_p))

                # Step 7: If there is a deficit (DEF[i,t,p]>0), use OFR flow with Deficit method
                # Creating the binary indicator variables
                OFRF_I[el_i][el_t].append([hcm.addVar(vtype=gbp.GRB.BINARY, name='OFRF_I'+str(el)+str(el_i)+str(el_t)+str(el_p)) for el in xrange(4)])
                hcm.update()
                # Constraints checking if there is a deficit
                big_m = 10000  # TODO calculate
                big_m1_1 = 10000  # TODO calculate
                big_m1_2 = 10000  # TODO calculate
                big_m2 = 10000  # TODO calculate
                hcm.addConstr(DEF[el_i][el_t][el_p] <= bigM*OFRF_I[el_i][el_t][el_p][0],
                              name='OFRF_IF_DEF1'+str(el_i)+str(el_t)+str(el_p))  # OFRF_I0i,t,p = 1 iplies there is a deficit
                hcm.addConstr(-1*DEF[el_i][el_t][el_p] <= bigM*OFRF_I[el_i][el_t][el_p][1],
                              name='OFRF_IF_DEF2'+str(el_i)+str(el_t)+str(el_p))  # OFRF_I1i,t,p = 1 iplies there is a deficit

                # Constraint that activates (or deactivates) situation 1/2 based on deficit check
                # If there is a deficit, i_2 = 0, so one of the following must hold.  If no deficit, i_2 = 1, which
                # means both of the following sets of "definition" inequalities will be inactive
                hcm.addConstr(OFRF_I[el_i][el_t][el_p][2]+OFRF_I[el_i][el_t][el_p][3] == OFRF_I[el_i][el_t][el_p][1]+1,
                              name='OFRF_IF_DEF3'+str(el_i)+str(el_t)+str(el_p))

                # Constraints to check to see if situation 1 or situation 2 is true. OFRF_I2i,t,p (i_3) = 1 implies that
                # situation 1 is used, while if OFRF_I3i,t,p (i_4) = 1 imples that situation 2 is used.
                hcm.addConstr(DEF[el_i][el_t][el_p]
                              - MF[el_i-1][el_t][el_p]
                              - ONRF[el_i-1][el_t][el_p]
                              <= big_m1*OFRF_I[el_i][el_t][el_p][2],
                              name="OFRF_IF_S1"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MF[el_i-1][el_t][el_p]
                              - ONRF[el_i-1][el_t][el_p]
                              - DEF[el_i][el_t][el_p]
                              <= big_m1*OFRF_I[el_i][el_t][el_p][3],
                              name="OFRF_IF_S2"+str(el_i)+str(el_t)+str(el_p))

                    # Situation 1: If upstream mainline flow plus the flow from an ONR at the upstream node is less than
                    # the deficit for this time step, then the OFR flow is equal to the mainline and the ONR flows times
                    # the OFR turning percentage in the preceeding itme interval
                ofr_tp1 = 0
                if el_p > 0:
                    ofr_tp1 = OFRD[el_i][el_p-1]/SD[el_i-1][el_p-1]
                else:  # TODO OFR turning percentage for -1 period?
                    ofr_tp1 = OFRD[el_i][el_p]/SD[el_i-1][el_p]
                hcm.addConstr(OFRF[el_i][el_t][el_p]
                              - ofr_tp1*MF[el_i-1][el_t][el_p]
                              - ofr_tp1*ONRF[el_i-1][el_t][el_p]
                              <= big_m1_1*OFRF_I[el_i][el_t][el_p][3],
                              name='OFRF_E1_1'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(OFRF[el_i][el_t][el_p]
                              - ofr_tp1*MF[el_i-1][el_t][el_p]
                              - ofr_tp1*ONRF[el_i-1][el_t][el_p]
                              >= -1*big_m1_1*OFRF_I[el_i][el_t][el_p][3],
                              name='OFRF_E1_2'+str(el_i)+str(el_t)+str(el_p))
                    # Situation 2: If the deficit is less than the upstream mainline flow plus the ONR flow from an ONR
                    # at the upstream node (if present)
                ofr_tp2_1 = 0
                if el_p > 0:
                    ofr_tp2_1 = OFRD[el_i][el_p-1]/SD[el_i-1][el_p-1]
                else:  # TODO OFR turning percentage for -1 period?
                    ofr_tp2_1 = OFRD[el_i][el_p]/SD[el_i-1][el_p]
                ofr_tp2_2 = OFRD[el_i][el_p]/SD[el_i-1][el_p]
                hcm.addConstr(OFRF[el_i][el_t][el_p]
                              - ofr_tp2_1*DEF[el_i][el_t][el_p]
                              - ofr_tp2_2*MF[el_i-1][el_t][el_p]
                              - ofr_tp2_2*ONRF[el_i-1][el_t][el_p]
                              + ofr_tp2_2*DEF[el_i][el_t][el_p]
                              <= big_m1_2*OFRF_I[el_i][el_t][el_p][2],
                              name='OFRF_E2_1'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(OFRF[el_i][el_t][el_p]
                              - ofr_tp2_1*DEF[el_i][el_t][el_p]
                              - ofr_tp2_2*MF[el_i-1][el_t][el_p]
                              - ofr_tp2_2*ONRF[el_i-1][el_t][el_p]
                              + ofr_tp2_2*DEF[el_i][el_t][el_p]
                              >= -1*big_m1_2*OFRF_I[el_i][el_t][el_p][2],
                              name='OFRF_E2_2'+str(el_i)+str(el_t)+str(el_p))

                # Step 8: If there is no deficit (DEF[i,t,p]=0), use OFR flow without deficit method
                ofr_tp3 = OFRD[el_i][el_p]/SD[el_i-1][el_p]
                hcm.addConstr(OFRF[el_i][el_t][el_p]
                              - ofr_tp3*MF[el_i-1][el_t][el_p]
                              - ofr_tp3*ONRF[el_i-1][el_t][el_p]
                              <= big_m2*OFRF_I[el_i][el_t][el_p][0],
                              name='OFRF_E3_1'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(OFRF[el_i][el_t][el_p]
                              - ofr_tp3*MF[el_i-1][el_t][el_p]
                              - ofr_tp3*ONRF[el_i-1][el_t][el_p]
                              >= -1*big_m2*OFRF_I[el_i][el_t][el_p][0],
                              name='OFRF_E3_2'+str(el_i)+str(el_t)+str(el_p))

hcm.update()

# Step 9: Calculate Mainline Input
for el_i in xrange(1,NS):                               # TODO strat loop at 0?
    for el_t in xrange(S):
        for el_p in xrange(P):
            hcm.addConstr(MI[el_i][el_t][el_p] ==       # TODO fix UV for t = -1?
                          MF[el_i-1][el_t][el_p]        # mainline flow at upstream segment
                          + ONRF[el_i-1][el_t][el_p]    # ONR flow at upstream segment
                          - OFRF[el_i][el_t][el_p]      # OFR flow at current segment
                          + UV(el_i-1, el_t - 1, el_p), # Unserved vehs in the upstream segment at the prev time step
                          name='MI_E'+str(el_i)+str(el_t)+str(el_p))

# Step 10: ONR at segment?
# Step 11: Calculate ONR input
for el_i in xrange(NS):
    if el_i in Ntilde:
        for el_t in xrange(S):
            for el_p in xrange(P):
                hcm.addConstr(ONRI[el_i][el_t][el_p] ==
                              ONRD[el_i][el_p]            # ONR demand
                              + ONRQ(el_i, el_t-1, el_p), # Queued vehicles on ONR at the previous step
                              name='ONRI_E'+str(el_i)+str(el_t)+str(el_p))

# Step 12: Calculate On-Ramp Input
ONRO_A = []  # List of auxiliary variables for step 12
ONRF_A = []  # List of auxiliary variables for steps 13-15
MO1_A = []   # List of auxiliary variables for step 16
for el_i in xrange(NS):
    ONRO_A.append([])
    ONRF_A.append([])
    MO1_A.append([])
    if el_i in Ntilde:
        for el_t in xrange(S):
            ONRO_A[el_i][el_t].append([])
            ONRF_A[el_i][el_t].append([])
            MO1_A[el_i][el_t].append([])
            for el_p in xrange(P):
                # Creating auxilary variables
                ONRO_A[el_i][el_t][el_p].append(hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRO_A1'+str(el_i)+str(el_t)+str(el_p)))
                ONRO_A[el_i][el_t][el_p].append(hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRO_A2'+str(el_i)+str(el_t)+str(el_p)))
                ONRO_A[el_i][el_t][el_p].append(hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRO_A3'+str(el_i)+str(el_t)+str(el_p)))
                #ONRO_A[el_i][el_t][el_p].append(hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRO_A4'+str(el_i)+str(el_t)+str(el_p)))
                #ONRO_A[el_i][el_t][el_p].append(hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRO_A5'+str(el_i)+str(el_t)+str(el_p)))
                #ONRO_A[el_i][el_t][el_p].append(hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRO_A6'+str(el_i)+str(el_t)+str(el_p)))
                hcm.update()

                if el_t is 0:
                    if el_p is 0:
                        temp_MF = 0    # TODO MF at t = -1 for p = 0
                        temp_ONRF = 0  # TODO ONRF at t = -1 for p = 0
                        temp_MO3 = 0   # TODO M03 at t = -1 for p = 0
                    else:
                        temp_MF = MF[el_i+1][S-1][el_p-1]
                        temp_ONRF = ONRF[el_i][S-1][el_p-1]
                        temp_MO3 = MO3[el_i][S-1][el_p-1]
                else:
                    temp_MF = MF[el_i+1][el_t-1][el_p]
                    temp_ONRF = ONRF[el_i][el_t-1][el_p]
                    temp_MO3 = MO3[el_i][el_t-1][el_p]
                generate_min_constrs(hcm,
                                     ONRO_A[el_i][el_t][el_p][0],
                                     SC[el_i][el_p],
                                     temp_MF + temp_ONRF,
                                     10000, 10000, 10000,
                                     'ONRO_MIN1', str(el_i)+str(el_t)+str(el_p))
                generate_min_constrs(hcm,
                                     ONRO_A[el_i][el_t][el_p][1],
                                     ONRO_A[el_i][el_t][el_p][0],
                                     temp_MO3 + temp_ONRF,
                                     10000, 10000, 10000,
                                     'ONRO_MIN2', str(el_i)+str(el_t)+str(el_p))
                generate_max_constrs(hcm,
                                     ONRO_A[el_i][el_t][el_p][2],
                                     ONRO_A[el_i][el_t][el_p][1] - MI[el_i][el_t][el_p],
                                     ONRO_A[el_i][el_t][el_p][1]/(2 * N[el_i][el_p]),
                                     10000, 10000, 10000,
                                     'ONRO_MAX1', str(el_i)+str(el_t)+str(el_p))

                max_of_rm_and_ramp_capacity = max(RM[el_i][el_p], ONRC[el_i][el_t][el_p])  # TODO treat RM as dv
                generate_min_constrs(hcm,
                                     ONRO[el_i][el_t][el_p],
                                     ONRO_A[el_i][el_t][el_p][2],
                                     max_of_rm_and_ramp_capacity,
                                     10000, 10000, 10000,
                                     'ONRO_E', str(el_i)+str(el_t)+str(el_p))

                big_m = 10000  # TODO calculate
                big_m11 = 10000 # TODO calculate
                big_m12 = 10000 # TODO calculate
                big_m2 = 10000 # TODO calculate
                ONRF_A[el_i][el_t][el_p].append([hcm.addVar(gbp.GRB.BINARY, name='ONRF_A'+str(el)+str(el_i)+str(el_t)+str(el_p)) for el in xrange(2)])
                hcm.update()
                hcm.addConstr(ONRF_A[el_i][el_t][el_p][0]+ONRF_A[el_i][el_t][el_p][1] == 1,
                              name='ONRF_A_E'+str(el_i)+str(el_t)+str(el_p))
                # Step 13: Is ONRO < ONRI?
                # ONRF_A1itp = 1 imples ONRO > ONRI
                # ONRF_A2itp = 1 imples ONRO < ONRI
                hcm.addConstr(ONRO[el_i][el_t][el_p]
                              - ONRI[el_i][el_t][el_p]
                              <= big_m*ONRF_A[el_i][el_t][el_p][0],
                              name="ONRF_IF1"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRI[el_i][el_t][el_p]
                              - ONRO[el_i][el_t][el_p]
                              <= big_m*ONRF_A[el_i][el_t][el_p][1],
                              name="ONRF_IF2"+str(el_i)+str(el_t)+str(el_p))
                # Step 14: If ONRO < ONRI,
                # ONRF = ONRO
                hcm.addConstr(ONRF[el_i][el_t][el_p]
                              - ONRO[el_i][el_t][el_p]
                              <= big_m11*ONRF_A[el_i][el_t][el_p][0],
                              name="ONRF_E1"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRF[el_i][el_t][el_p]
                              - ONRO[el_i][el_t][el_p]
                              <= -1*big_m11*ONRF_A[el_i][el_t][el_p][0],
                              name="ONRF_E2"+str(el_i)+str(el_t)+str(el_p))
                # Update number of vehs in the ramp queue
                # ONRQ = ONRQt-1 + ONRI - ONRO
                hcm.addConstr(ONRQ(el_i, el_t, el_p)
                              - ONRQ(el_i, el_t-1, el_p)
                              - ONRI[el_i][el_t][el_p]
                              + ONRO[el_i][el_t][el_p]
                              <= big_m12*ONRF_A[el_i][el_t][el_p][0],
                              name="ONRQ_E1"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRQ(el_i, el_t, el_p)
                              - ONRQ(el_i, el_t-1, el_p)
                              - ONRI[el_i][el_t][el_p]
                              + ONRO[el_i][el_t][el_p]
                              <= -1*big_m12*ONRF_A[el_i][el_t][el_p][0],
                              name="ONRQ_E2"+str(el_i)+str(el_t)+str(el_p))

                # Step 15: If ONRI < ONRO
                # ONRF = ONRI
                hcm.addConstr(ONRF[el_i][el_t][el_p]
                              - ONRI[el_i][el_t][el_p]
                              <= big_m2*ONRF_A[el_i][el_t][el_p][1],
                              name="ONRF_E3"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRF[el_i][el_t][el_p]
                              - ONRI[el_i][el_t][el_p]
                              <= -1*big_m2*ONRF_A[el_i][el_t][el_p][1],
                              name="ONRF_E4"+str(el_i)+str(el_t)+str(el_p))

                # Step 16: Calculate Mainline Output (1)
                MO1_A[el_i][el_t][el_p].append(hcm.addVar(gbp.GRB.CONTINUOUS,
                                                          name='MO1_A'+str(el_i)+str(el_t)+str(el_p)))
                hcm.update()
                generate_min_constrs(hcm,
                                     MO1_A[el_i][el_t][el_p][0],
                                     SC[el_i][el_p] - ONRF[el_i][el_t][el_p],
                                     MO2(el_i, el_t-1, el_p),                  # TODO t = -1
                                     10000, 10000, 10000,
                                     'MO1_MIN1', str(el_i)+str(el_t)+str(el_p))
                generate_min_constrs(hcm,
                                     MO1[el_i][el_t][el_p],
                                     MO1_A[el_i][el_t][el_p][0],
                                     MO3(el_i, el_t-1, el_p),           # TODO t = -1
                                     10000, 10000, 10000,
                                     'MO1_MIN2', str(el_i)+str(el_t)+str(el_p))

# Step 17: Queue present on segment?
MO3_A = []
for el_i in xrange(NS):
    MO3_A[el_i].append([])
    for el_t in xrange(S):
        MO3_A[el_i][el_t].append([])
        for el_p in xrange(P):
            # Check ONRQ and UV?
            # Creating auxiliary variables
            MO3_A[el_i][el_t][el_p].append([hcm.addVar(vtype=gbp.GRB.BINARY,
                                                      name='MO3_A'+str(el)+str(el_i)+str(el_t)+str(el_p)) for el in xrange(2)])
            hcm.update()

# Set Lower/Upper Bounds