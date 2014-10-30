from __future__ import division
import gurobipy as gbp
from pylab import *
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
ONRC = [[[2400 if el_i in Ntilde else 0 for el_P in xrange(P)] for el_t in xrange(S)] for el_i in xrange(NS)]  # Geometric capacity of ONR at node i in period t in interval p
RM = [[2400 if el_i in Ntilde else 0 for el_P in xrange(P)] for el_i in xrange(NS)]  # Ramp metering rate of node i during interval p (veh/h)

######## Creating Gurobi Model
# Initializing model instance
hcm = gbp.Model("hcm-test")

# Creating linear decision variables
ED = []  # Expected dmand that would arrive at segment i over inteval p
for el_i in xrange(NS):
    ED.append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ED' + str(el_i) + str(el_p)) for el_p in xrange(P)])
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
ONRF = []  # Actual OFR flow rate that can cross on ramp node i during step t in interval p
for el_i in xrange(NS):
    ONRF.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRF'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
ONRI = []  # Input flow rate desiring to enter the merge point at ONR node i during step t in interval p
for el_i in xrange(NS):
    ONRI.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRI'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
ONRQ = []  # Unment demand that is stored as a queu on the ONR roadway at node i during step t in interval p
for el_i in xrange(NS):
    ONRQ.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRQ'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
ONRO = []  # Max output flow rate that can enter the merge point from ONR node i during step t in interval p
for el_i in xrange(NS):
    ONRO.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRO'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
DEF = []  # Deficit in flow at segment i at time step t in interval p
for el_i in xrange(NS):
    DEF.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='DEF'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
OFRF = []  # Actual flow that can exit at OFR node i during step t in interval p
for el_i in xrange(NS):
    OFRF.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='OFRF'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
UV = []  # Unserved vehicles: additional # of vehicles stored in segment i at the end of step t in interval p
for el_i in xrange(NS):
    UV.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='UV'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
MO1 = []  # Max mainline output 1: limited by ONR flow at segment i
for el_i in xrange(NS):
    MO1.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='MO1'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
MO2 = []  # Max mainline output 2: limited by available storage on segment i due to a downstream queue
for el_i in xrange(NS):
    MO2.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='MO2'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])
MO3 = []  # Max mainline output 3: limited by the presence of qued vech at the upstream in up segment i while the queue clears from the downstream end of segment i
for el_i in xrange(NS):
    MO3.append([[hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='MO3'+str(el_i)+str(el_t)+str(el_p)) for el_p in xrange(P)] for el_t in xrange(S)])

# Integrating variables into model
hcm.update()

# Set objective
#hcm.setObjective()

# Adding equality/inquality constraints

hcm.addConstr()
