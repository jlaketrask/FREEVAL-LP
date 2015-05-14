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
    P = 4  # number of time intervals (periods) in the analysis period
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