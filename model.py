from __future__ import division
import time
import gurobipy as gbp
from numpy import *
from aux_functions import compute_segment_demand, compute_estimated_demand, compute_background_density, read_facility_data_from_file
from constraintGenerator import generate_max_constrs, generate_min_constrs, sum_add_t, sum_sum_add_t_p
__author__ = 'jltrask'

use_sos = False
printFile = False
def_const_type = 0
example_problem  = 9

init_time = time.time()
######## Model Parameters
# # Indices and basic Freeway geometry parameters
# NS = 11  # number of segments
# Stilde = [el for el in xrange(NS)]
# Ftilde = [3,5,9]  # List of OFR segments
# Ntilde = [1,5,7]  # List of ONR segments
# Wtilde = [5]   # List of Weave segments
# P = 5  # number of time intervals (periods) in the analysis period
# Ptilde = [el for el in xrange(P)]  # List of time intervals
# S = 4 * 15  # Number of time steps in a single interval (each step is 15 seconds)
# Ttilde = [el for el in xrange(S)]  # List of time steps
# Th = 240  # Number of time steps in 1 hour
# alpha = 5  # %
#
# facility_data = read_facility_data_from_file("gp_example_1_facility_data.csv", NS, P)
#
# # Constants
# KC = 45  # Ideal Density at capacity
# KJ = 190  # Facility-wide jam density
# L = [5280,1500,2280,1500,5280,2640,5280,1140,360,1140,5280]  # Length of each segment
# SC = facility_data["SC"]  # Segment capacity of segment i in interval p
# mainline_demand = [4505, 4955, 5225, 4685, 3785]
# N = facility_data["NL"]  # Number of open lanes in segment i in interval p
# WS = lambda i, p: SC[i][p]/(N[i][p] * (KJ-KC))  # Wave speed for segment i in interval p
# WTT = lambda i, p: int(round(Th * (L[i]/5280.0/WS(i, p))))  # Wave travel time
# ONRD = facility_data["ONRD"]  # Demand flow rate for ONR at node i in interval p
# ONRCv = facility_data["ONRC"]
# ONRC = lambda i, t, p: ONRCv[i][p]  # Geometric capacity of ONR at node i in period t in interval p
# RM = facility_data["RM"]  # Ramp metering rate of node i during interval p (veh/h)
# OFRD = facility_data["OFRD"]  # Demand flow rate for OFR at node i in interval p
# SD = compute_segment_demand(NS, mainline_demand, ONRD, OFRD) # Segment demand for segment i in time interval p

if example_problem is 1:
    # Simple Test Case 1
    NS = 3  # number of segments
    Stilde = [el for el in xrange(NS)]
    Ftilde = []  # List of OFR segments
    Ntilde = []  # List of ONR segments
    Wtilde = []   # List of Weave segments
    P = 2  # number of time intervals (periods) in the analysis period
    Ptilde = [el for el in xrange(P)]  # List of time intervals
    S = 4 * 15  # Number of time steps in a single interval (each step is 15 seconds)
    Ttilde = [el for el in xrange(S)]  # List of time steps
    Th = 240  # Number of time steps in 1 hour
    alpha = 5  # %

    facility_data = read_facility_data_from_file("simple_test_case_1.csv", NS, P)

    # Constants
    KC = 45  # Ideal Density at capacity
    KJ = 190  # Facility-wide jam density
    L = [2640,2640,2640]  # Length of each segment
    L = [el_l/5280.0 for el_l in L]
    SC = facility_data["SC"]  # Segment capacity of segment i in interval p
    mainline_demand = [4000,4000]
    N = facility_data["NL"]  # Number of open lanes in segment i in interval p
    WS = lambda i, p: SC[i][p]/(N[i][p] * (KJ-KC))  # Wave speed for segment i in interval p
    WTT = lambda i, p: int(round(Th * (L[i]/5280.0/WS(i, p))))  # Wave travel time
    ONRD = facility_data["ONRD"]  # Demand flow rate for ONR at node i in interval p
    ONRCv = facility_data["ONRC"]
    ONRC = lambda i, t, p: ONRCv[i][p]  # Geometric capacity of ONR at node i in period t in interval p
    RM = facility_data["RM"]  # Ramp metering rate of node i during interval p (veh/h)
    OFRD = facility_data["OFRD"]  # Demand flow rate for OFR at node i in interval p
    SD = compute_segment_demand(NS, mainline_demand, ONRD, OFRD) # Segment demand for segment i in time interval p

elif example_problem is 2:
    # Simple Test Case 2
    NS = 3  # number of segments
    Stilde = [el for el in xrange(NS)]
    Ftilde = [1]  # List of OFR segments
    Ntilde = []  # List of ONR segments
    Wtilde = []   # List of Weave segments
    P = 2  # number of time intervals (periods) in the analysis period
    Ptilde = [el for el in xrange(P)]  # List of time intervals
    S = 4 * 15  # Number of time steps in a single interval (each step is 15 seconds)
    Ttilde = [el for el in xrange(S)]  # List of time steps
    Th = 240  # Number of time steps in 1 hour
    alpha = 5  # %

    facility_data = read_facility_data_from_file("simple_test_case_2.csv", NS, P)

    # Constants
    KC = 45  # Ideal Density at capacity
    KJ = 190  # Facility-wide jam density
    L = [2640,2640,2640]  # Length of each segment
    L = [el_l/5280.0 for el_l in L]
    SC = facility_data["SC"]  # Segment capacity of segment i in interval p
    mainline_demand = [4000,4000]
    N = facility_data["NL"]  # Number of open lanes in segment i in interval p
    WS = lambda i, p: SC[i][p]/(N[i][p] * (KJ-KC))  # Wave speed for segment i in interval p
    WTT = lambda i, p: int(round(Th * (L[i]/5280.0/WS(i, p))))  # Wave travel time
    ONRD = facility_data["ONRD"]  # Demand flow rate for ONR at node i in interval p
    ONRCv = facility_data["ONRC"]
    ONRC = lambda i, t, p: ONRCv[i][p]  # Geometric capacity of ONR at node i in period t in interval p
    RM = facility_data["RM"]  # Ramp metering rate of node i during interval p (veh/h)
    OFRD = facility_data["OFRD"]  # Demand flow rate for OFR at node i in interval p
    SD = compute_segment_demand(NS, mainline_demand, ONRD, OFRD) # Segment demand for segment i in time interval p

elif example_problem is 3:
    # Simple Test Case 3
    NS = 3  # number of segments
    Stilde = [el for el in xrange(NS)]
    Ftilde = []  # List of OFR segments
    Ntilde = [1]  # List of ONR segments
    Wtilde = []   # List of Weave segments
    P = 2  # number of time intervals (periods) in the analysis period
    Ptilde = [el for el in xrange(P)]  # List of time intervals
    S = 4 * 15  # Number of time steps in a single interval (each step is 15 seconds)
    Ttilde = [el for el in xrange(S)]  # List of time steps
    Th = 240  # Number of time steps in 1 hour
    alpha = 5  # %

    facility_data = read_facility_data_from_file("simple_test_case_3.csv", NS, P)

    # Constants
    KC = 45  # Ideal Density at capacity
    KJ = 190  # Facility-wide jam density
    L = [2640,2640,2640]  # Length of each segment
    L = [el_l/5280.0 for el_l in L]
    SC = facility_data["SC"]  # Segment capacity of segment i in interval p
    mainline_demand = [4000,4000]
    N = facility_data["NL"]  # Number of open lanes in segment i in interval p
    WS = lambda i, p: SC[i][p]/(N[i][p] * (KJ-KC))  # Wave speed for segment i in interval p
    WTT = lambda i, p: int(round(Th * (L[i]/5280.0/WS(i, p))))  # Wave travel time
    ONRD = facility_data["ONRD"]  # Demand flow rate for ONR at node i in interval p
    ONRCv = facility_data["ONRC"]
    ONRC = lambda i, t, p: ONRCv[i][p]  # Geometric capacity of ONR at node i in period t in interval p
    RM = facility_data["RM"]  # Ramp metering rate of node i during interval p (veh/h)
    OFRD = facility_data["OFRD"]  # Demand flow rate for OFR at node i in interval p
    SD = compute_segment_demand(NS, mainline_demand, ONRD, OFRD) # Segment demand for segment i in time interval p

elif example_problem is 4:
    # Simple Test Case 4
    NS = 5  # number of segments
    Stilde = [el for el in xrange(NS)]
    Ftilde = [3]  # List of OFR segments
    Ntilde = [1]  # List of ONR segments
    Wtilde = []   # List of Weave segments
    P = 4  # number of time intervals (periods) in the analysis period
    Ptilde = [el for el in xrange(P)]  # List of time intervals
    S = 4 * 15  # Number of time steps in a single interval (each step is 15 seconds)
    Ttilde = [el for el in xrange(S)]  # List of time steps
    Th = 240  # Number of time steps in 1 hour
    alpha = 5  # %

    facility_data = read_facility_data_from_file("simple_test_case_4.csv", NS, P)

    # Constants
    KC = 45  # Ideal Density at capacity
    KJ = 190  # Facility-wide jam density
    L = [2640,2640,2640,2640,2640]  # Length of each segment
    L = [el_l/5280.0 for el_l in L]
    SC = facility_data["SC"]  # Segment capacity of segment i in interval p
    mainline_demand = [4000,4000,4000,4000]
    N = facility_data["NL"]  # Number of open lanes in segment i in interval p
    WS = lambda i, p: SC[i][p]/(N[i][p] * (KJ-KC))  # Wave speed for segment i in interval p
    WTT = lambda i, p: int(round(Th * (L[i]/5280.0/WS(i, p))))  # Wave travel time
    ONRD = facility_data["ONRD"]  # Demand flow rate for ONR at node i in interval p
    ONRCv = facility_data["ONRC"]
    ONRC = lambda i, t, p: ONRCv[i][p]  # Geometric capacity of ONR at node i in period t in interval p
    RM = facility_data["RM"]  # Ramp metering rate of node i during interval p (veh/h)
    OFRD = facility_data["OFRD"]  # Demand flow rate for OFR at node i in interval p
    SD = compute_segment_demand(NS, mainline_demand, ONRD, OFRD) # Segment demand for segment i in time interval p

elif example_problem is 5:
    # Simple Test Case 5
    NS = 4  # number of segments
    Stilde = [el for el in xrange(NS)]
    Ftilde = [2]  # List of OFR segments
    Ntilde = [1]  # List of ONR segments
    Wtilde = []   # List of Weave segments
    P = 2  # number of time intervals (periods) in the analysis period
    Ptilde = [el for el in xrange(P)]  # List of time intervals
    S = 4 * 15  # Number of time steps in a single interval (each step is 15 seconds)
    Ttilde = [el for el in xrange(S)]  # List of time steps
    Th = 240  # Number of time steps in 1 hour
    alpha = 5  # %

    facility_data = read_facility_data_from_file("simple_test_case_5.csv", NS, P)

    # Constants
    KC = 45  # Ideal Density at capacity
    KJ = 190  # Facility-wide jam density
    L = [2640,2640,2640,2640]  # Length of each segment
    L = [el_l/5280.0 for el_l in L]
    SC = facility_data["SC"]  # Segment capacity of segment i in interval p
    mainline_demand = [6000,6000]
    N = facility_data["NL"]  # Number of open lanes in segment i in interval p
    WS = lambda i, p: SC[i][p]/(N[i][p] * (KJ-KC))  # Wave speed for segment i in interval p
    WTT = lambda i, p: int(round(Th * (L[i]/5280.0/WS(i, p))))  # Wave travel time
    ONRD = facility_data["ONRD"]  # Demand flow rate for ONR at node i in interval p
    ONRCv = facility_data["ONRC"]
    ONRC = lambda i, t, p: ONRCv[i][p]  # Geometric capacity of ONR at node i in period t in interval p
    RM = facility_data["RM"]  # Ramp metering rate of node i during interval p (veh/h)
    OFRD = facility_data["OFRD"]  # Demand flow rate for OFR at node i in interval p
    SD = compute_segment_demand(NS, mainline_demand, ONRD, OFRD) # Segment demand for segment i in time interval p

elif example_problem is 6:
    # Simple Test Case 5
    NS = 4  # number of segments
    Stilde = [el for el in xrange(NS)]
    Ftilde = [2]  # List of OFR segments
    Ntilde = [1]  # List of ONR segments
    Wtilde = []   # List of Weave segments
    P = 4  # number of time intervals (periods) in the analysis period
    Ptilde = [el for el in xrange(P)]  # List of time intervals
    S = 4 * 15  # Number of time steps in a single interval (each step is 15 seconds)
    Ttilde = [el for el in xrange(S)]  # List of time steps
    Th = 240  # Number of time steps in 1 hour
    alpha = 5  # %

    facility_data = read_facility_data_from_file("simple_test_case_6.csv", NS, P)

    # Constants
    KC = 45  # Ideal Density at capacity
    KJ = 190  # Facility-wide jam density
    L = [2640,2640,2640,2640]  # Length of each segment
    L = [el_l/5280.0 for el_l in L]
    SC = facility_data["SC"]  # Segment capacity of segment i in interval p
    mainline_demand = [6000,6000, 6000, 6000]
    N = facility_data["NL"]  # Number of open lanes in segment i in interval p
    WS = lambda i, p: SC[i][p]/(N[i][p] * (KJ-KC))  # Wave speed for segment i in interval p
    WTT = lambda i, p: int(round(Th * (L[i]/5280.0/WS(i, p))))  # Wave travel time
    ONRD = facility_data["ONRD"]  # Demand flow rate for ONR at node i in interval p
    ONRCv = facility_data["ONRC"]
    ONRC = lambda i, t, p: ONRCv[i][p]  # Geometric capacity of ONR at node i in period t in interval p
    RM = facility_data["RM"]  # Ramp metering rate of node i during interval p (veh/h)
    OFRD = facility_data["OFRD"]  # Demand flow rate for OFR at node i in interval p
    SD = compute_segment_demand(NS, mainline_demand, ONRD, OFRD) # Segment demand for segment i in time interval p

elif example_problem is 7:
    # Simple Test Case 5
    NS = 4  # number of segments
    Stilde = [el for el in xrange(NS)]
    Ftilde = [2]  # List of OFR segments
    Ntilde = [1]  # List of ONR segments
    Wtilde = []   # List of Weave segments
    P = 4  # number of time intervals (periods) in the analysis period
    Ptilde = [el for el in xrange(P)]  # List of time intervals
    S = 4 * 15  # Number of time steps in a single interval (each step is 15 seconds)
    Ttilde = [el for el in xrange(S)]  # List of time steps
    Th = 240  # Number of time steps in 1 hour
    alpha = 5  # %

    facility_data = read_facility_data_from_file("simple_test_case_7.csv", NS, P)

    # Constants
    KC = 45  # Ideal Density at capacity
    KJ = 190  # Facility-wide jam density
    L = [2640,2640,2640,2640]  # Length of each segment
    L = [el_l/5280.0 for el_l in L]
    SC = facility_data["SC"]  # Segment capacity of segment i in interval p
    mainline_demand = [6000,6000, 6000, 6000]
    N = facility_data["NL"]  # Number of open lanes in segment i in interval p
    WS = lambda i, p: SC[i][p]/(N[i][p] * (KJ-KC))  # Wave speed for segment i in interval p
    WTT = lambda i, p: int(round(Th * (L[i]/5280.0/WS(i, p))))  # Wave travel time
    ONRD = facility_data["ONRD"]  # Demand flow rate for ONR at node i in interval p
    ONRCv = facility_data["ONRC"]
    ONRC = lambda i, t, p: ONRCv[i][p]  # Geometric capacity of ONR at node i in period t in interval p
    RM = facility_data["RM"]  # Ramp metering rate of node i during interval p (veh/h)
    OFRD = facility_data["OFRD"]  # Demand flow rate for OFR at node i in interval p
    SD = compute_segment_demand(NS, mainline_demand, ONRD, OFRD) # Segment demand for segment i in time interval p

elif example_problem is 8:
    # Simple Test Case 5
    NS = 5  # number of segments
    Stilde = [el for el in xrange(NS)]
    Ftilde = [3]  # List of OFR segments
    Ntilde = [1]  # List of ONR segments
    Wtilde = []   # List of Weave segments
    P = 4  # number of time intervals (periods) in the analysis period
    Ptilde = [el for el in xrange(P)]  # List of time intervals
    S = 4 * 15  # Number of time steps in a single interval (each step is 15 seconds)
    Ttilde = [el for el in xrange(S)]  # List of time steps
    Th = 240  # Number of time steps in 1 hour
    alpha = 5  # %

    facility_data = read_facility_data_from_file("simple_test_case_8.csv", NS, P)

    # Constants
    KC = 45  # Ideal Density at capacity
    KJ = 190  # Facility-wide jam density
    L = [2640,2640,2640, 2640,2640]  # Length of each segment
    L = [el_l/5280.0 for el_l in L]
    SC = facility_data["SC"]  # Segment capacity of segment i in interval p
    mainline_demand = [6000,6000,6000,6000]
    N = facility_data["NL"]  # Number of open lanes in segment i in interval p
    WS = lambda i, p: SC[i][p]/(N[i][p] * (KJ-KC))  # Wave speed for segment i in interval p
    WTT = lambda i, p: int(round(Th * (L[i]/5280.0/WS(i, p))))  # Wave travel time
    ONRD = facility_data["ONRD"]  # Demand flow rate for ONR at node i in interval p
    ONRCv = facility_data["ONRC"]
    ONRC = lambda i, t, p: ONRCv[i][p]  # Geometric capacity of ONR at node i in period t in interval p
    RM = facility_data["RM"]  # Ramp metering rate of node i during interval p (veh/h)
    OFRD = facility_data["OFRD"]  # Demand flow rate for OFR at node i in interval p
    SD = compute_segment_demand(NS, mainline_demand, ONRD, OFRD) # Segment demand for segment i in time interval p

elif example_problem is 9:
    # Simple Test Case 5
    NS = 5  # number of segments
    Stilde = [el for el in xrange(NS)]
    Ftilde = [3]  # List of OFR segments
    Ntilde = [1]  # List of ONR segments
    Wtilde = []   # List of Weave segments
    P = 2  # number of time intervals (periods) in the analysis period
    Ptilde = [el for el in xrange(P)]  # List of time intervals
    S = 4 * 15  # Number of time steps in a single interval (each step is 15 seconds)
    Ttilde = [el for el in xrange(S)]  # List of time steps
    Th = 240  # Number of time steps in 1 hour
    alpha = 5  # %

    facility_data = read_facility_data_from_file("simple_test_case_9.csv", NS, P)

    # Constants
    KC = 45  # Ideal Density at capacity
    KJ = 190  # Facility-wide jam density
    L = [2640,2640,2640, 2640,2640]  # Length of each segment
    L = [el_l/5280.0 for el_l in L]
    SC = facility_data["SC"]  # Segment capacity of segment i in interval p
    mainline_demand = [6000,6000]
    N = facility_data["NL"]  # Number of open lanes in segment i in interval p
    WS = lambda i, p: SC[i][p]/(N[i][p] * (KJ-KC))  # Wave speed for segment i in interval p
    WTT = lambda i, p: int(round(Th * (L[i]/5280.0/WS(i, p))))  # Wave travel time
    ONRD = facility_data["ONRD"]  # Demand flow rate for ONR at node i in interval p
    ONRCv = facility_data["ONRC"]
    ONRC = lambda i, t, p: ONRCv[i][p]  # Geometric capacity of ONR at node i in period t in interval p
    RM = facility_data["RM"]  # Ramp metering rate of node i during interval p (veh/h)
    OFRD = facility_data["OFRD"]  # Demand flow rate for OFR at node i in interval p
    SD = compute_segment_demand(NS, mainline_demand, ONRD, OFRD) # Segment demand for segment i in time interval p

elif example_problem is 10:
    # Simple Test Oversat (queue contained)
    NS = 5  # number of segments
    Stilde = [el for el in xrange(NS)]
    Ftilde = []  # List of OFR segments
    Ntilde = [3]  # List of ONR segments
    Wtilde = []   # List of Weave segments
    P = 4  # number of time intervals (periods) in the analysis period
    Ptilde = [el for el in xrange(P)]  # List of time intervals
    S = 4 * 15  # Number of time steps in a single interval (each step is 15 seconds)
    Ttilde = [el for el in xrange(S)]  # List of time steps
    Th = 240  # Number of time steps in 1 hour
    alpha = 5  # %

    facility_data = read_facility_data_from_file("sto_cq.csv", NS, P)

    # Constants
    KC = 45  # Ideal Density at capacity
    KJ = 190  # Facility-wide jam density
    L = [2640,2640,2640,2640,2640]  # Length of each segment
    L = [el_l/5280.0 for el_l in L]
    SC = facility_data["SC"]  # Segment capacity of segment i in interval p
    mainline_demand = [2000,6200,2000,2000]
    N = facility_data["NL"]  # Number of open lanes in segment i in interval p
    WS = lambda i, p: SC[i][p]/(N[i][p] * (KJ-KC))  # Wave speed for segment i in interval p
    WTT = lambda i, p: int(round(Th * (L[i]/5280.0/WS(i, p))))  # Wave travel time
    ONRD = facility_data["ONRD"]  # Demand flow rate for ONR at node i in interval p
    ONRCv = facility_data["ONRC"]
    ONRC = lambda i, t, p: ONRCv[i][p]  # Geometric capacity of ONR at node i in period t in interval p
    RM = facility_data["RM"]  # Ramp metering rate of node i during interval p (veh/h)
    OFRD = facility_data["OFRD"]  # Demand flow rate for OFR at node i in interval p
    SD = compute_segment_demand(NS, mainline_demand, ONRD, OFRD) # Segment demand for segment i in time interval p

elif example_problem is 11:
    # Simple Test Oversat (queue contained)
    NS = 5  # number of segments
    Stilde = [el for el in xrange(NS)]
    Ftilde = []  # List of OFR segments
    Ntilde = [3]  # List of ONR segments
    Wtilde = []   # List of Weave segments
    P = 4  # number of time intervals (periods) in the analysis period
    Ptilde = [el for el in xrange(P)]  # List of time intervals
    S = 4 * 15  # Number of time steps in a single interval (each step is 15 seconds)
    Ttilde = [el for el in xrange(S)]  # List of time steps
    Th = 240  # Number of time steps in 1 hour
    alpha = 5  # %

    facility_data = read_facility_data_from_file("sto_cq_nq.csv", NS, P)

    # Constants
    KC = 45  # Ideal Density at capacity
    KJ = 190  # Facility-wide jam density
    L = [2640,2640,2640,2640,2640]  # Length of each segment
    L = [el_l/5280.0 for el_l in L]
    SC = facility_data["SC"]  # Segment capacity of segment i in interval p
    mainline_demand = [2000,4000,2000,2000]
    N = facility_data["NL"]  # Number of open lanes in segment i in interval p
    WS = lambda i, p: SC[i][p]/(N[i][p] * (KJ-KC))  # Wave speed for segment i in interval p
    WTT = lambda i, p: int(round(Th * (L[i]/5280.0/WS(i, p))))  # Wave travel time
    ONRD = facility_data["ONRD"]  # Demand flow rate for ONR at node i in interval p
    ONRCv = facility_data["ONRC"]
    ONRC = lambda i, t, p: ONRCv[i][p]  # Geometric capacity of ONR at node i in period t in interval p
    RM = facility_data["RM"]  # Ramp metering rate of node i during interval p (veh/h)
    OFRD = facility_data["OFRD"]  # Demand flow rate for OFR at node i in interval p
    SD = compute_segment_demand(NS, mainline_demand, ONRD, OFRD) # Segment demand for segment i in time interval p

elif example_problem is 12:
    # Simple Test Oversat (spillback queue out of facility)
    NS = 5  # number of segments
    Stilde = [el for el in xrange(NS)]
    Ftilde = [3]  # List of OFR segments
    Ntilde = [1]  # List of ONR segments
    Wtilde = []   # List of Weave segments
    P = 4  # number of time intervals (periods) in the analysis period
    Ptilde = [el for el in xrange(P)]  # List of time intervals
    S = 4 * 15  # Number of time steps in a single interval (each step is 15 seconds)
    Ttilde = [el for el in xrange(S)]  # List of time steps
    Th = 240  # Number of time steps in 1 hour
    alpha = 5  # %

    facility_data = read_facility_data_from_file("simple_test_oversat.csv", NS, P)

    # Constants
    KC = 45  # Ideal Density at capacity
    KJ = 190  # Facility-wide jam density
    L = [2640,2640,2640,2640,2640]  # Length of each segment
    L = [el_l/5280.0 for el_l in L]
    SC = facility_data["SC"]  # Segment capacity of segment i in interval p
    mainline_demand = [2000,6200,2000,2000]
    N = facility_data["NL"]  # Number of open lanes in segment i in interval p
    WS = lambda i, p: SC[i][p]/(N[i][p] * (KJ-KC))  # Wave speed for segment i in interval p
    WTT = lambda i, p: int(round(Th * (L[i]/5280.0/WS(i, p))))  # Wave travel time
    ONRD = facility_data["ONRD"]  # Demand flow rate for ONR at node i in interval p
    ONRCv = facility_data["ONRC"]
    ONRC = lambda i, t, p: ONRCv[i][p]  # Geometric capacity of ONR at node i in period t in interval p
    RM = facility_data["RM"]  # Ramp metering rate of node i during interval p (veh/h)
    OFRD = facility_data["OFRD"]  # Demand flow rate for OFR at node i in interval p
    SD = compute_segment_demand(NS, mainline_demand, ONRD, OFRD) # Segment demand for segment i in time interval p

else:
    # GP Example 1
    NS = 11  # number of segments
    Stilde = [el for el in xrange(NS)]
    Ftilde = [3,5,9]  # List of OFR segments
    Ntilde = [1,5,7]  # List of ONR segments
    Wtilde = [5]   # List of Weave segments
    P = 5  # number of time intervals (periods) in the analysis period
    Ptilde = [el for el in xrange(P)]  # List of time intervals
    S = 4 * 15  # Number of time steps in a single interval (each step is 15 seconds)
    Ttilde = [el for el in xrange(S)]  # List of time steps
    Th = 240  # Number of time steps in 1 hour
    alpha = 5  # %

    facility_data = read_facility_data_from_file("gp_ex1_data.csv", NS, P)

    # Constants
    KC = 45  # Ideal Density at capacity
    KJ = 190  # Facility-wide jam density
    L = [5280,1500,2280,1500,5280,2640,5280,1140,360,1140,5280]  # Length of each segment
    L = [el_l/5280.0 for el_l in L]
    SC = facility_data["SC"]  # Segment capacity of segment i in interval p
    mainline_demand = [4505,4955,5255,4685,3785]
    N = facility_data["NL"]  # Number of open lanes in segment i in interval p
    WS = lambda i, p: SC[i][p]/(N[i][p] * (KJ-KC))  # Wave speed for segment i in interval p
    WTT = lambda i, p: int(round(Th * (L[i]/5280.0/WS(i, p))))  # Wave travel time
    ONRD = facility_data["ONRD"]  # Demand flow rate for ONR at node i in interval p
    ONRCv = facility_data["ONRC"]
    ONRC = lambda i, t, p: ONRCv[i][p]  # Geometric capacity of ONR at node i in period t in interval p
    RM = facility_data["RM"]  # Ramp metering rate of node i during interval p (veh/h)
    OFRD = facility_data["OFRD"]  # Demand flow rate for OFR at node i in interval p
    SD = compute_segment_demand(NS, mainline_demand, ONRD, OFRD) # Segment demand for segment i in time interval p

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

# Precomputing known values
# (1) Estimated demand (ED) and background density (KB)
EDv = compute_estimated_demand(SC, SD)
#KB = compute_background_density(ED, Ftilde, Ntilde)
KB = facility_data["KB"]

# (2) Wave Trave Time and Wave Speed


# More variable declarations
# Step 6-11 Variables
DEF_I = []
OFRF_I = []
ONRO_I = []
for el_i in xrange(NS):
    DEF_I.append([])
    OFRF_I.append([])
    ONRO_I.append([])
    for el_t in xrange(S):
        DEF_I[el_i].append([])
        OFRF_I[el_i].append([])
        ONRO_I[el_i].append([])
        for el_p in xrange(P):
            DEF_I[el_i][el_t].append([hcm.addVar(vtype=gbp.GRB.BINARY, name = "DEF_I"+str(el_i)+str(el_t)+str(el_p)+str(el)) for el in xrange(2)])
            OFRF_I[el_i][el_t].append([hcm.addVar(vtype=gbp.GRB.BINARY, name='OFRF_I'+str(el)+str(el_i)+str(el_t)+str(el_p)) for el in xrange(4)])
            ONRO_I[el_i][el_t].append([hcm.addVar(vtype=gbp.GRB.BINARY, name = "ONRO_I"+str(el_i)+str(el_t)+str(el_p)+str(el)) for el in xrange(8)])
# Step 12 variables
ONRO_A = []  # List of auxiliary variables for step 12
ONRF_I = []  # List of auxiliary variables for steps 13-15
MO1_A = []   # List of auxiliary variables for step 16
for el_i in xrange(NS):
    ONRO_A.append([])
    ONRF_I.append([])
    MO1_A.append([])
    for el_t in xrange(S):
        ONRO_A[el_i].append([])
        ONRF_I[el_i].append([])
        MO1_A[el_i].append([])
        for el_p in xrange(P):
            # Creating auxilary variables
            ONRO_A[el_i][el_t].append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS, name='ONRO_A1'+str(el_i)+str(el_t)+str(el_p)+str(el)) for el in xrange(3)])
            ONRF_I[el_i][el_t].append([hcm.addVar(vtype=gbp.GRB.BINARY, name='ONRF_A'+str(el)+str(el_i)+str(el_t)+str(el_p)) for el in xrange(2)])
            MO1_A[el_i][el_t].append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS,name='MO1_A'+str(el_i)+str(el_t)+str(el_p))])

# Step 16 variables
MO1_I = []
for el_i in xrange(NS):
    MO1_I.append([])
    for el_t in xrange(S):
        MO1_I[el_i].append([])
        for el_p in xrange(P):
            MO1_I[el_i][el_t].append([hcm.addVar(vtype=gbp.GRB.BINARY, name = "MO1_I"+str(el_i)+str(el_t)+str(el_p)+str(el)) for el in xrange(4)])

# Step 17 variables
I_UV = [] # Array to hold binary indicator variables
for el_i in xrange(NS):
    I_UV.append([])
    for el_t in xrange(S):
        I_UV[el_i].append([])
        for (el_p) in xrange(P):
            I_UV[el_i][el_t].append([hcm.addVar(vtype=gbp.GRB.BINARY,
                                                    name = "I_UV"+str(var_id)+str(el_i)+str(el_t)+str(el_p))for var_id in xrange(2)])
# Steps 19 variables
MO3_A = [] # 4D array holding Auxiliary variables for step 19
MO3_I = [] # 4D array holding indicator variables for step 19
for el_i in xrange(NS):
    MO3_A.append([])
    MO3_I.append([])
    for el_t in xrange(S):
        MO3_A[el_i].append([])
        MO3_I[el_i].append([])
        for el_p in xrange(P):
            # Creating auxiliary variables
            MO3_A[el_i][el_t].append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS,
                                                      name='MO3_A'+str(el)+str(el_i)+str(el_t)+str(el_p)) for el in xrange(4)])
            # Creating Binary Indicator Variables
            MO3_I[el_i][el_t].append([hcm.addVar(vtype=gbp.GRB.BINARY,
                                                      name='MO3_I'+str(el)+str(el_i)+str(el_t)+str(el_p)) for el in xrange(8)])

# Step 22 variables
MF_A = [] # 4D array holding Auxiliary variables for step 19
MF_I = [] # 4D array holding indicator variables for step 19
for el_i in xrange(NS):
    MF_A.append([])
    MF_I.append([])
    for el_t in xrange(S):
        MF_A[el_i].append([])
        MF_I[el_i].append([])
        for el_p in xrange(P):
            MF_A[el_i][el_t].append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS,
                                                name='MF_A'+str(el)+str(el_i)+str(el_t)+str(el_p)) for el in xrange(4)])
            MF_I[el_i][el_t].append([hcm.addVar(vtype=gbp.GRB.BINARY,
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

#Step 2: initialize the Freeway Facility
##### Need to calculate KB from Undersat
# Updateing # of vehicles - note t goes from 0 to S (i.e. S+1 steps) for NV, with 0 being  "before" interval p starts.
for el_i in xrange(NS):
    for el_p in xrange(P):  # Note that the lambda function on UV accounts for the case p = -1 (UV = 0 in that case)
        hcm.addConstr(NV(el_i, -1, el_p) == KB[el_i][el_p]*L[el_i] + UV(el_i, S-1, el_p-1), name='NV_E'+str(el_i)+str(0)+str(el_p))
#hcm.update()
print("step 2 done")


for el_i in xrange(NS):
    for el_t in xrange(S):
        for el_p in xrange(P):
            # Constraint determining number of vehicles on the segment
            hcm.addConstr(NV(el_i, el_t, el_p) == NV(el_i, el_t-1, el_p) + MF(el_i, el_t, el_p)
                        + ONRF(el_i, el_t, el_p) - MF(el_i+1, el_t, el_p) - OFRF(el_i+1 , el_t, el_p),
                        name="3.113" +str(el_i)+str(el_t)+str(el_p))

            # Constraint updating the number of unserved vehicles
            hcm.addConstr(UV(el_i, el_t, el_p) == NV(el_i, el_t, el_p) - KB[el_i][el_p]*L[el_i],
                          name = "3.114"+str(el_i)+str(el_t)+str(el_p))

# Steps 3-4: Begin "loops" of all segments, all time steps
# Steps 5-8: OFR Segment constraints
#OFRF_I = []
big_m = 10000  # TODO calculate
big_m1 = 10000  # TODO calculate
big_m2 = 10000  # TODO calculate
#big_m = 10000  # TODO calculate
big_m1_1 = 10000  # TODO calculate
big_m1_2 = 10000  # TODO calculate
#big_m2 = 10000  # TODO calculate
def_zero_tol = 0.001
for el_i in xrange(NS):
    #OFRF_I.append([])
    if el_i in Ftilde:  # Check if OFR at segment
        # Calculate possible deficit from upstream queue
        # Note el_i-1 okay because the first segment cannot be an off-ramp
        for el_t in xrange(S):
            # ASSUMED NO DEFICIT IN THE FIRST PERIOD
            hcm.addConstr(DEF[el_i][el_t][0] == 0.0, name='DEF_E'+str(el_i)+str(el_t)+str(0))
            for el_p in xrange(1,P):
                if def_const_type is 0:
                    # Updated DEF_A equations
                    a1 = 0
                    if el_t is 0:
                        a1 = sum(SD[el_i-1][0:el_p])*(1/240.0) # Add Segment demand from first to previous period
                        a1-= sum([sum([MF(el_i-1, el1, el2)*(1/240.0)+ONRF(el_i-1, el1, el2)*(1/240.0) for el1 in xrange(S)]) for el2 in xrange(el_p)]) # Subtract (MF+ONRF)
                        hcm.addConstr(DEF_A[el_i][el_t][el_p] == a1, name="DEF_TEMP_A"+str(el_i)+str(el_t)+str(el_p))
                    else:
                        hcm.addConstr(DEF_A[el_i][el_t][el_p] == DEF_A[el_i][el_t-1][el_p] + MF(el_i-1, el_t-1, el_p)*(1/240.0) + ONRF(el_i-1, el_t-1, el_p)*(1/240.0), name="DEF_TEMP_A"+str(el_i)+str(el_t)+str(el_p))
                elif def_const_type is 1:
                    #### DEPRECATED FULL DEF CALCULATION EQUATIONS ####
                    a1 = sum(SD[el_i-1][0:el_p])*(1/240.0) + sum([MF(el_i-1, el, el_p)*(1/240.0) + ONRF(el_i-1, el, el_p)*(1/240.0) for el in xrange(el_t)]) - sum([sum([MF(el_i-1, el, el2)*(1/240.0) + ONRF(el_i-1, el, el2)*(1/240.0) for el in xrange(S)]) for el2 in xrange(el_p)])
                    hcm.addConstr(DEF_A[el_i][el_t][el_p] == a1, name="DEF_TEMP_A"+str(el_i)+str(el_t)+str(el_p))
                else:
                    # Force Deficit to be 0 (debugging purposes)
                    hcm.addConstr(DEF_A[el_i][el_t][el_p] == 0.0, name='DEF_E'+str(el_i)+str(el_t)+str(el_p))

                # Setting DEF to be max of DEF_A and 0
                generate_max_constrs(hcm, DEF_I[el_i][el_t][el_p], DEF[el_i][el_t][el_p], 0, DEF_A[el_i][el_t][el_p], big_m, big_m1, big_m2, 'DEF_E', str(el_i)+str(el_t)+str(el_p), use_sos)

                # Step 7: If there is a deficit (DEF[i,t,p]>0), use OFR flow with Deficit method
                # Constraints checking if there is a deficit
                if use_sos:
                    hcm.addSOS(gbp.GRB.SOS_TYPE1, [OFRF_I[el_i][el_t][el_p][0],OFRF_I[el_i][el_t][el_p][1]])
                else:
                    hcm.addConstr(OFRF_I[el_i][el_t][el_p][0] + OFRF_I[el_i][el_t][el_p][1] == 1.0,
                              name='OFRF_IF_DEF0'+str(el_i)+str(el_t)+str(el_p))

                hcm.addConstr(DEF[el_i][el_t][el_p] - def_zero_tol <= big_m*OFRF_I[el_i][el_t][el_p][0],
                              name='OFRF_IF_DEF1'+str(el_i)+str(el_t)+str(el_p))  # OFRF_I0i,t,p = 1 iplies there is a deficit
                hcm.addConstr(def_zero_tol - DEF[el_i][el_t][el_p] <= big_m*OFRF_I[el_i][el_t][el_p][1],
                              name='OFRF_IF_DEF2'+str(el_i)+str(el_t)+str(el_p))  # OFRF_I1i,t,p = 1 iplies there is a deficit

                # Constraint that activates (or deactivates) situation 1/2 based on deficit check
                # If there is a deficit, i_2 = 0, so one of the following must hold.  If no deficit, i_2 = 1, which
                # means both of the following sets of "definition" inequalities will be inactive
                hcm.addConstr(OFRF_I[el_i][el_t][el_p][2]+OFRF_I[el_i][el_t][el_p][3] == OFRF_I[el_i][el_t][el_p][1]+1,
                              name='OFRF_IF_DEF3'+str(el_i)+str(el_t)+str(el_p))

                # Constraints to check to see if situation 1 or situation 2 is true. OFRF_I2i,t,p (i_3) = 1 implies that
                # situation 1 is used, while if OFRF_I3i,t,p (i_4) = 1 imples that situation 2 is used.
                hcm.addConstr(DEF[el_i][el_t][el_p]
                              - MF(el_i-1, el_t, el_p)
                              - ONRF(el_i-1, el_t, el_p)
                              <= big_m1*OFRF_I[el_i][el_t][el_p][2],
                              name="OFRF_IF_S1"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(MF(el_i-1, el_t, el_p)
                              + ONRF(el_i-1, el_t, el_p)
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
                hcm.addConstr(OFRF(el_i, el_t, el_p)
                              - ofr_tp1*MFv[el_i-1][el_t][el_p]
                              - ofr_tp1*ONRF(el_i-1, el_t, el_p)
                              <= big_m1_1*OFRF_I[el_i][el_t][el_p][3],
                              name='OFRF_E1_1'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(OFRF(el_i, el_t, el_p)
                              - ofr_tp1*MFv[el_i-1][el_t][el_p]
                              - ofr_tp1*ONRF(el_i-1, el_t, el_p)
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
                hcm.addConstr(OFRF(el_i, el_t, el_p)
                              - ofr_tp2_1*DEF[el_i][el_t][el_p]
                              - ofr_tp2_2*MFv[el_i-1][el_t][el_p]
                              - ofr_tp2_2*ONRF(el_i-1, el_t, el_p)
                              + ofr_tp2_2*DEF[el_i][el_t][el_p]
                              <= big_m1_2*OFRF_I[el_i][el_t][el_p][2],
                              name='OFRF_E2_1'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(OFRF(el_i, el_t, el_p)
                              - ofr_tp2_1*DEF[el_i][el_t][el_p]
                              - ofr_tp2_2*MFv[el_i-1][el_t][el_p]
                              - ofr_tp2_2*ONRF(el_i-1, el_t, el_p)
                              + ofr_tp2_2*DEF[el_i][el_t][el_p]
                              >= -1*big_m1_2*OFRF_I[el_i][el_t][el_p][2],
                              name='OFRF_E2_2'+str(el_i)+str(el_t)+str(el_p))

                # Step 8: If there is no deficit (DEF[i,t,p]=0), use OFR flow without deficit method
                ofr_tp3 = OFRD[el_i][el_p]/SD[el_i-1][el_p]
                hcm.addConstr(OFRF(el_i, el_t, el_p)
                              - ofr_tp3*MFv[el_i-1][el_t][el_p]
                              - ofr_tp3*ONRF(el_i-1, el_t, el_p)
                              <= big_m2*OFRF_I[el_i][el_t][el_p][0],
                              name='OFRF_E3_1'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(OFRF(el_i, el_t, el_p)
                              - ofr_tp3*MFv[el_i-1][el_t][el_p]
                              - ofr_tp3*ONRF(el_i-1, el_t, el_p)
                              >= -1*big_m2*OFRF_I[el_i][el_t][el_p][0],
                              name='OFRF_E3_2'+str(el_i)+str(el_t)+str(el_p))
    else:
       for el_t in xrange(S):
            for el_p in xrange(P):
                hcm.addConstr(OFRF(el_i, el_t, el_p) == 0.0, name='OFRF_E3'+str(el_i)+str(el_t)+str(el_p))


print("step 8 done")

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

# Step 10: ONR at segment?
# Step 11: Calculate ONR input
for el_i in xrange(NS):
    if el_i in Ntilde:
        for el_t in xrange(S):
            for el_p in xrange(P):
                hcm.addConstr(ONRI[el_i][el_t][el_p] ==
                              ONRD[el_i][el_p]            # ONR demand
                              + ONRQ(el_i, el_t-1, el_p), # Queued vehicles on ONR at the previous step (t-1=-1 case implemented in function def)
                              name='ONRI_E'+str(el_i)+str(el_t)+str(el_p))
                generate_min_constrs(hcm, ONRO_I[el_i][el_t][el_p][0:2],
                                     ONRO_A[el_i][el_t][el_p][0],
                                     SC[el_i][el_p],
                                     MF(el_i+1, el_t-1, el_p) + ONRF(el_i, el_t-1, el_p),
                                     10000, 10000, 10000,
                                     'ONRO_MIN1', str(el_i)+str(el_t)+str(el_p), use_sos=use_sos)
                generate_min_constrs(hcm,ONRO_I[el_i][el_t][el_p][2:4],
                                     ONRO_A[el_i][el_t][el_p][1],
                                     ONRO_A[el_i][el_t][el_p][0],
                                     MO3(el_i, el_t-1, el_p) + ONRF(el_i, el_t-1, el_p),
                                     10000, 10000, 10000,
                                     'ONRO_MIN2', str(el_i)+str(el_t)+str(el_p), use_sos=use_sos)
                generate_max_constrs(hcm, ONRO_I[el_i][el_t][el_p][4:6],
                                     ONRO_A[el_i][el_t][el_p][2],
                                     ONRO_A[el_i][el_t][el_p][1] - MI[el_i][el_t][el_p],
                                     ONRO_A[el_i][el_t][el_p][1]*(1.0/(2 * N[el_i][el_p])),
                                     10000, 10000, 10000,
                                     'ONRO_MAX1', str(el_i)+str(el_t)+str(el_p), use_sos=use_sos)
                min_of_rm_and_ramp_capacity = min(RM[el_i][el_p], ONRC(el_i, el_t, el_p))  # TODO treat RM as dv
                generate_min_constrs(hcm,ONRO_I[el_i][el_t][el_p][6:8],
                                     ONRO[el_i][el_t][el_p],
                                     ONRO_A[el_i][el_t][el_p][2],
                                     min_of_rm_and_ramp_capacity,
                                     10000, 10000, 10000,
                                     'ONRO_E', str(el_i)+str(el_t)+str(el_p), use_sos=use_sos)

                big_m = 10000  # TODO calculate
                big_m11 = 10000 # TODO calculate
                big_m12 = 1000 # TODO calculate
                big_m2 = 10000 # TODO calculate
                if use_sos:
                    hcm.addSOS(gbp.GRB.SOS_TYPE1, [ONRF_I[el_i][el_t][el_p][0],ONRF_I[el_i][el_t][el_p][1]])
                else:
                    hcm.addConstr(ONRF_I[el_i][el_t][el_p][0]+ONRF_I[el_i][el_t][el_p][1] == 1,
                              name='ONRF_A_E'+str(el_i)+str(el_t)+str(el_p))
                # Step 13: Is ONRO < ONRI?
                # ONRF_A1itp = 1 imples ONRO > ONRI
                # ONRF_A2itp = 1 imples ONRO < ONRI
                hcm.addConstr(ONRO[el_i][el_t][el_p]
                              - ONRI[el_i][el_t][el_p]
                              <= big_m*ONRF_I[el_i][el_t][el_p][0],
                              name="ONRF_IF1"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRI[el_i][el_t][el_p]
                              - ONRO[el_i][el_t][el_p]
                              <= big_m*ONRF_I[el_i][el_t][el_p][1],
                              name="ONRF_IF2"+str(el_i)+str(el_t)+str(el_p))

                # Step 14: If ONRO < ONRI,
                # ONRF = ONRO
                hcm.addConstr(ONRF(el_i, el_t, el_p)
                              - ONRO[el_i][el_t][el_p]
                              <= big_m11*ONRF_I[el_i][el_t][el_p][0],
                              name="ONRF_E1"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRF(el_i, el_t, el_p)
                              - ONRO[el_i][el_t][el_p]
                              >= -1*big_m11*ONRF_I[el_i][el_t][el_p][0],
                              name="ONRF_E2"+str(el_i)+str(el_t)+str(el_p))
                # Update number of vehs in the ramp queue
                # ONRQ = ONRQt-1 + ONRI - ONRO
                hcm.addConstr(ONRQ(el_i, el_t, el_p)
                              - ONRQ(el_i, el_t-1, el_p)
                              - ONRI[el_i][el_t][el_p]
                              + ONRO[el_i][el_t][el_p]
                              <= big_m12*ONRF_I[el_i][el_t][el_p][0],
                              name="ONRQ_E1"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRQ(el_i, el_t, el_p)
                              - ONRQ(el_i, el_t-1, el_p)
                              - ONRI[el_i][el_t][el_p]
                              + ONRO[el_i][el_t][el_p]
                              >= -1*big_m12*ONRF_I[el_i][el_t][el_p][0],
                              name="ONRQ_E2"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRQ(el_i, el_t, el_p) <= big_m12*ONRF_I[el_i][el_t][el_p][1],
                              name="ONRQ_E3"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRQ(el_i, el_t, el_p) >= -1*big_m12*ONRF_I[el_i][el_t][el_p][1],
                              name="ONRQ_E4"+str(el_i)+str(el_t)+str(el_p))

                # Step 15: If ONRI < ONRO
                # ONRF = ONRI
                hcm.addConstr(ONRF(el_i, el_t, el_p)
                              - ONRI[el_i][el_t][el_p]
                              <= big_m2*ONRF_I[el_i][el_t][el_p][1],
                              name="ONRF_E3"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRF(el_i, el_t, el_p)
                              - ONRI[el_i][el_t][el_p]
                              >= -1*big_m2*ONRF_I[el_i][el_t][el_p][1],
                              name="ONRF_E4"+str(el_i)+str(el_t)+str(el_p))
                #hcm.addConstr(ONRF(el_i, el_t, el_p) == ONRI[el_i][el_t][el_p])
                #hcm.addConstr(ONRQ(el_i,el_t,el_p) == 0.0)
    else:
        for el_t in xrange(S):
            for el_p in xrange(P):
                hcm.addConstr(ONRF(el_i,el_t,el_p) == 0.0, name='ONRF'+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr(ONRQ(el_i,el_t,el_p) == 0.0)

print("Step 15 Done")


for el_i in xrange(NS):
    for el_t in xrange(S):
        for el_p in xrange(P):
                # Step 16: Calculate Mainline Output (1)
                generate_min_constrs(hcm, MO1_I[el_i][el_t][el_p][0:2],
                                     MO1_A[el_i][el_t][el_p][0],
                                     SC[el_i][el_p] - ONRF(el_i, el_t, el_p),
                                     MO2(el_i, el_t-1, el_p),                  # TODO t = -1
                                     10000, 10000, 10000,
                                     'MO1_MIN1', str(el_i)+str(el_t)+str(el_p))
                generate_min_constrs(hcm, MO1_I[el_i][el_t][el_p][2:4],
                                     MO1(el_i, el_t, el_p),
                                     MO1_A[el_i][el_t][el_p][0],
                                     MO3(el_i, el_t-1, el_p),           # TODO t = -1
                                     10000, 10000, 10000,
                                     'MO1_MIN2', str(el_i)+str(el_t)+str(el_p))


print("step 16 done")

# Step 17: Queue present on segment?
# I_UV = [] # Array to hold binary indicator variables
# for el_i in xrange(NS):
#     I_UV.append([])
#     for el_t in xrange(S):
#         I_UV[el_i].append([])
#         for (el_p) in xrange(P):
#             I_UV[el_i][el_t].append(hcm.addVar(vtype=gbp.GRB.BINARY,
#                                                     name = "I_UV"+str(el_i)+str(el_t)+str(el_p)))
#hcm.update()
M_UV = 10000     # TODO Maximum of UV?
uv_zero_tol = 0.001
# Creating constraints
for el_i in xrange(NS):
    for el_t in xrange(S):
        for (el_p) in xrange(P):
            hcm.addConstr(UV(el_i,el_t,el_p) - uv_zero_tol <=M_UV* I_UV[el_i][el_t][el_p][0], name="I_UV0"+str(el_i)+str(el_t)+str(el_p))  # Queue Present: I_UV[el_i][el_t][el_p][0] = 1, I_UV[el_i][el_t][el_p][1] = 0
            hcm.addConstr(uv_zero_tol - UV(el_i,el_t,el_p) <= M_UV* I_UV[el_i][el_t][el_p][1], name="I_UV1"+str(el_i)+str(el_t)+str(el_p)) # Queue Not Present: I_UV[el_i][el_t][el_p][0] = 0, I_UV[el_i][el_t][el_p][1] = 1
            hcm.addConstr(I_UV[el_i][el_t][el_p][0]+I_UV[el_i][el_t][el_p][1] == 1, name="I_UVE"+str(el_i)+str(el_t)+str(el_p))
#hcm.update()
print("step 17 done")

# Step 18 Is there a front clearing queue in this time interval
front_clearing_queue_present = []
for el_i in xrange(NS):
    front_clearing_queue_present.append([])
    for el_p in xrange(P):
        front_clearing_queue_present[el_i].append(((SC[el_i][el_p] - ONRD[el_i][el_p]) > (SC[el_i][el_p-1]-ONRD[el_i][el_p-1]))  # TODO p-1
            and (SC[el_i][el_p]-ONRD[el_i][el_p] > SD[el_i][el_p]))
print("step 18 done")
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
#                   + ", " + str(DEF_A[i][t][p].X)
#                   + ", " + str(DEF[i][t][p].X)
#                   + ", " + str(UV(i,t,p).X)
#                   + ", " + str(I_UV[i][t][p][0].X)
#                   + ", " + str(I_UV[i][t][p][1].X))
# Steps 19: Calculate Mainline Output 3
# MO3_A = [] # 4D array holding Auxiliary variables for step 19
# MO3_I = [] # 4D array holding indicator variables for step 19
# for el_i in xrange(NS):
#     MO3_A.append([])
#     MO3_I.append([])
#     for el_t in xrange(S):
#         MO3_A[el_i].append([])
#         MO3_I[el_i].append([])
#         for el_p in xrange(P):
#             # Creating auxiliary variables
#             MO3_A[el_i][el_t].append([hcm.addVar(vtype=gbp.GRB.CONTINUOUS,
#                                                       name='MO3_A'+str(el)+str(el_i)+str(el_t)+str(el_p)) for el in xrange(4)])
#             # Creating Binary Indicator Variables
#             MO3_I[el_i][el_t].append([hcm.addVar(vtype=gbp.GRB.BINARY,
#                                                       name='MO3_I'+str(el)+str(el_i)+str(el_t)+str(el_p)) for el in xrange(8)])
# # Updating Model
# hcm.update()


M_MO3=[]
for el_i in xrange(NS - 1):  # TODO Check NS minus 1?
    M_MO3.append([])
    for el_t in xrange(S):
        M_MO3[el_i].append([])
        for el_p in xrange(P):
            M_MO3[el_i][el_t].append([10000 for el in xrange(16)])  # TODO Appropriate estimation for M_MO3?
# hcm.update() # Not needed because just constants, not variables

for el_i in xrange(NS - 1):  # TODO Check NS minus 1?
    for el_t in xrange(S):
        for el_p in xrange(P):
            if not front_clearing_queue_present[el_i][el_p]:
                hcm.addConstr(MO3(el_i,el_t,el_p) == SC[el_i][el_p], name="MO3_NFCQ"+str(el_i)+str(el_t)+str(el_p))
            else :
                # Minimum of MO1 and (MO2-OFRF)
                hcm.addConstr(MO1(el_i+1, el_t - WTT(el_i, el_p), el_p)
                    - (MO2(el_i+1, el_t-WTT(el_i, el_p), el_p) + OFRF(el_i+1, el_t-WTT(el_i, el_p), el_p))
                    <= M_MO3[el_i][el_t][el_p][0]*MO3_I[el_i][el_t][el_p][0], name = "3.63"+str(el_i)+str(el_t)+str(el_p))
                hcm.addConstr((MO2(el_i+1, el_t-WTT(el_i, el_p), el_p) + OFRF(el_i+1, el_t-WTT(el_i, el_p), el_p))
                    - MO1(el_i+1, el_t - WTT(el_i, el_p), el_p)
                    <= M_MO3[el_i][el_t][el_p][0]*MO3_I[el_i][el_t][el_p][1], name = "3.64"+str(el_i)+str(el_t)+str(el_p))
                # Binary indicator variable constraint
                if use_sos:
                    hcm.addSOS(gbp.GRB.SOS_TYPE1, [MO3_I[el_i][el_t][el_p][0],MO3_I[el_i][el_t][el_p][1]])
                else:
                    hcm.addConstr(MO3_I[el_i][el_t][el_p][0]+MO3_I[el_i][el_t][el_p][1] == 2 - I_UV[el_i][el_t][el_p][0],
                               name = "3.65"+str(el_i)+str(el_t)+str(el_p))
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
#                   + ", " + str(DEF_A[i][t][p].X)
#                   + ", " + str(DEF[i][t][p].X)
#                   + ", " + str(UV(i,t,p).X)
#                   + ", " + str(I_UV[i][t][p][0].X))
# Step 20: Calculate density of queue on segment
for el_i in xrange(NS):  # TODO -1?
    for el_t in xrange(S):  # Todo account for "t-1"
        for el_p in xrange(P):
            hcm.addConstr(KQ[el_i][el_t][el_p] == KJ - ((KJ-KC)/SC[el_i][el_p])*SF(el_i+1, el_t-1, el_p),
                          name="3.85"+str(el_i)+str(el_t)+str(el_p))
#hcm.update()
print("step 20 done")
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
else:
    for p in xrange(P):
        for t in xrange(S):
            for i in xrange(NS):
                varCount+=1
                print(str(varCount)
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
                      + ", " + str(I_UV[i][t][p][1].X))


# Set Lower/Upper Bounds