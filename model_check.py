# -*- coding: utf-8 -*-
from numpy import zeros
xrange = range

def extract(example_problem):
    if example_problem is 0:
        # Model Check 1
        NS = 5  # number of segments
        Stilde = [el for el in xrange(NS)]
        Ftilde = []  # List of OFR segments
        Ntilde = []  # List of ONR segments
        Wtilde = []   # List of Weave segments
        P = 4  # number of time intervals (periods) in the analysis period
        Ptilde = [el for el in xrange(P)]  # List of time intervals
        S = 5  # Number of time steps in a single interval (each step is 15 seconds)
        Ttilde = [el for el in xrange(S)]  # List of time steps
        Th = 4*S  # Number of time steps in 1 hour
        alpha = 0  # %

        facility_data = read_facility_data_from_file("model_checks/mc1_5step.csv", NS, P)

        # Constants
        KC = 45  # Ideal Density at capacity
        KJ = 190  # Facility-wide jam density
        L = [2640, 2640, 2640, 2640, 2640]  # Length of each segment
        L = [el_l/5280.0 for el_l in L]
        SC = facility_data["SC"]  # Segment capacity of segment i in interval p
        mainline_demand = [4000, 5100, 4500, 4000]
        N = facility_data["NL"]  # Number of open lanes in segment i in interval p
        WS = lambda i, p: SC[i][p]/(N[i][p] * (KJ-KC))  # Wave speed for segment i in interval p
        WTT = lambda i, p: int(round(Th * (L[i]/5280.0/WS(i, p))))  # Wave travel time
        ONRD = facility_data["ONRD"]  # Demand flow rate for ONR at node i in interval p
        ONRCv = facility_data["ONRC"]
        ONRC = lambda i, t, p: ONRCv[i][p]  # Geometric capacity of ONR at node i in period t in interval p
        RM = facility_data["RM"]  # Ramp metering rate of node i during interval p (veh/h)
        OFRD = facility_data["OFRD"]  # Demand flow rate for OFR at node i in interval p
        SD = compute_segment_demand(NS, mainline_demand, ONRD, OFRD) # Segment demand for segment i in time interval p
        V = facility_data["V"]
        return {"NS":NS,"Stilde":Stilde,"Ftilde":Ftilde,"Ntilde":Ntilde,"Wtilde":Wtilde,"P":P,"Ptilde":Ptilde,"S":S,
                "Ttilde":Ttilde,"Th":Th,"alpha":alpha,"KC":KC,"KJ":KJ,"L":L,"SC":SC,"mainline_demand":mainline_demand,
                "N":N,"WS":WS,"WTT":WTT,"ONRD":ONRD,"ONRC":ONRC,"RM":RM,"OFRD":OFRD,"SD":SD,"KB":facility_data["KB"],
                "nvuv_fname":'model_checks/mc1_5step_nvuv.csv', "V": V}
        
    elif example_problem is 1:
        # Model Check 2
        NS = 6  # number of segments
        Stilde = [el for el in xrange(NS)]
        Ftilde = [4]  # List of OFR segments
        Ntilde = []  # List of ONR segments
        Wtilde = []   # List of Weave segments
        P = 4  # number of time intervals (periods) in the analysis period
        Ptilde = [el for el in xrange(P)]  # List of time intervals
        S = 5  # Number of time steps in a single interval (each step is 15 seconds)
        Ttilde = [el for el in xrange(S)]  # List of time steps
        Th = 4*S  # Number of time steps in 1 hour
        alpha = 0  # %

        facility_data = read_facility_data_from_file("model_checks/mc2_5step.csv", NS, P)

        # Constants
        KC = 45  # Ideal Density at capacity
        KJ = 190  # Facility-wide jam density
        L = [2640, 2640, 2640, 2640, 2640, 2640]  # Length of each segment
        L = [el_l/5280.0 for el_l in L]
        SC = facility_data["SC"]  # Segment capacity of segment i in interval p
        mainline_demand = [4000, 5100, 4500, 4000]
        N = facility_data["NL"]  # Number of open lanes in segment i in interval p
        WS = lambda i, p: SC[i][p]/(N[i][p] * (KJ-KC))  # Wave speed for segment i in interval p
        WTT = lambda i, p: int(round(Th * (L[i]/5280.0/WS(i, p))))  # Wave travel time
        ONRD = facility_data["ONRD"]  # Demand flow rate for ONR at node i in interval p
        ONRCv = facility_data["ONRC"]
        ONRC = lambda i, t, p: ONRCv[i][p]  # Geometric capacity of ONR at node i in period t in interval p
        RM = facility_data["RM"]  # Ramp metering rate of node i during interval p (veh/h)
        OFRD = facility_data["OFRD"]  # Demand flow rate for OFR at node i in interval p
        SD = compute_segment_demand(NS, mainline_demand, ONRD, OFRD) # Segment demand for segment i in time interval p
        V = facility_data["V"]
        return {"NS":NS,"Stilde":Stilde,"Ftilde":Ftilde,"Ntilde":Ntilde,"Wtilde":Wtilde,"P":P,"Ptilde":Ptilde,"S":S,
                "Ttilde":Ttilde,"Th":Th,"alpha":alpha,"KC":KC,"KJ":KJ,"L":L,"SC":SC,"mainline_demand":mainline_demand,
                "N":N,"WS":WS,"WTT":WTT,"ONRD":ONRD,"ONRC":ONRC,"RM":RM,"OFRD":OFRD,"SD":SD,"KB":facility_data["KB"],
                "nvuv_fname":'model_checks/mc2_5step_nvuv.csv', "V":V}
                
    elif example_problem is 2:
        # Model Check 3
        NS = 6  # number of segments
        Stilde = [el for el in xrange(NS)]
        Ftilde = []  # List of OFR segments
        Ntilde = [4]  # List of ONR segments
        Wtilde = []   # List of Weave segments
        P = 4  # number of time intervals (periods) in the analysis period
        Ptilde = [el for el in xrange(P)]  # List of time intervals
        S = 5  # Number of time steps in a single interval (each step is 15 seconds)
        Ttilde = [el for el in xrange(S)]  # List of time steps
        Th = 4*S  # Number of time steps in 1 hour
        alpha = 0  # %

        facility_data = read_facility_data_from_file("model_checks/mc3_5step.csv", NS, P)

        # Constants
        KC = 45  # Ideal Density at capacity
        KJ = 190  # Facility-wide jam density
        L = [2640, 2640, 2640, 2640, 2640, 2640]  # Length of each segment
        L = [el_l/5280.0 for el_l in L]
        SC = facility_data["SC"]  # Segment capacity of segment i in interval p
        mainline_demand = [4000, 5100, 4500, 4000]
        N = facility_data["NL"]  # Number of open lanes in segment i in interval p
        WS = lambda i, p: SC[i][p]/(N[i][p] * (KJ-KC))  # Wave speed for segment i in interval p
        WTT = lambda i, p: int(round(Th * (L[i]/5280.0/WS(i, p))))  # Wave travel time
        ONRD = facility_data["ONRD"]  # Demand flow rate for ONR at node i in interval p
        ONRCv = facility_data["ONRC"]
        ONRC = lambda i, t, p: ONRCv[i][p]  # Geometric capacity of ONR at node i in period t in interval p
        RM = facility_data["RM"]  # Ramp metering rate of node i during interval p (veh/h)
        OFRD = facility_data["OFRD"]  # Demand flow rate for OFR at node i in interval p
        SD = compute_segment_demand(NS, mainline_demand, ONRD, OFRD) # Segment demand for segment i in time interval p
        V = facility_data["V"]
        return {"NS":NS,"Stilde":Stilde,"Ftilde":Ftilde,"Ntilde":Ntilde,"Wtilde":Wtilde,"P":P,"Ptilde":Ptilde,"S":S,
                "Ttilde":Ttilde,"Th":Th,"alpha":alpha,"KC":KC,"KJ":KJ,"L":L,"SC":SC,"mainline_demand":mainline_demand,
                "N":N,"WS":WS,"WTT":WTT,"ONRD":ONRD,"ONRC":ONRC,"RM":RM,"OFRD":OFRD,"SD":SD,"KB":facility_data["KB"],
                "nvuv_fname":'model_checks/mc3_5step_nvuv.csv', "V": V}
                
    elif example_problem is 3:
        # Model Check 4
        NS = 6  # number of segments
        Stilde = [el for el in xrange(NS)]
        Ftilde = []  # List of OFR segments
        Ntilde = [1]  # List of ONR segments
        Wtilde = []   # List of Weave segments
        P = 4  # number of time intervals (periods) in the analysis period
        Ptilde = [el for el in xrange(P)]  # List of time intervals
        S = 5  # Number of time steps in a single interval (each step is 15 seconds)
        Ttilde = [el for el in xrange(S)]  # List of time steps
        Th = 4*S  # Number of time steps in 1 hour
        alpha = 0  # %

        facility_data = read_facility_data_from_file("model_checks/mc4_5step.csv", NS, P)

        # Constants
        KC = 45  # Ideal Density at capacity
        KJ = 190  # Facility-wide jam density
        L = [2640, 2640, 2640, 2640, 2640, 2640]  # Length of each segment
        L = [el_l/5280.0 for el_l in L]
        SC = facility_data["SC"]  # Segment capacity of segment i in interval p
        mainline_demand = [4000, 4600, 4000, 3500]
        N = facility_data["NL"]  # Number of open lanes in segment i in interval p
        WS = lambda i, p: SC[i][p]/(N[i][p] * (KJ-KC))  # Wave speed for segment i in interval p
        WTT = lambda i, p: int(round(Th * (L[i]/5280.0/WS(i, p))))  # Wave travel time
        ONRD = facility_data["ONRD"]  # Demand flow rate for ONR at node i in interval p
        ONRCv = facility_data["ONRC"]
        ONRC = lambda i, t, p: ONRCv[i][p]  # Geometric capacity of ONR at node i in period t in interval p
        RM = facility_data["RM"]  # Ramp metering rate of node i during interval p (veh/h)
        OFRD = facility_data["OFRD"]  # Demand flow rate for OFR at node i in interval p
        SD = compute_segment_demand(NS, mainline_demand, ONRD, OFRD) # Segment demand for segment i in time interval p
        V = facility_data["V"]
        return {"NS":NS,"Stilde":Stilde,"Ftilde":Ftilde,"Ntilde":Ntilde,"Wtilde":Wtilde,"P":P,"Ptilde":Ptilde,"S":S,
                "Ttilde":Ttilde,"Th":Th,"alpha":alpha,"KC":KC,"KJ":KJ,"L":L,"SC":SC,"mainline_demand":mainline_demand,
                "N":N,"WS":WS,"WTT":WTT,"ONRD":ONRD,"ONRC":ONRC,"RM":RM,"OFRD":OFRD,"SD":SD,"KB":facility_data["KB"],
                "nvuv_fname":'model_checks/mc4_5step_nvuv.csv', "V": V}
                
    elif example_problem is 4:
        # Model Check 1
        NS = 5  # number of segments
        Stilde = [el for el in xrange(NS)]
        Ftilde = []  # List of OFR segments
        Ntilde = []  # List of ONR segments
        Wtilde = []   # List of Weave segments
        P = 4  # number of time intervals (periods) in the analysis period
        Ptilde = [el for el in xrange(P)]  # List of time intervals
        S = 5  # Number of time steps in a single interval (each step is 15 seconds)
        Ttilde = [el for el in xrange(S)]  # List of time steps
        Th = 4*S  # Number of time steps in 1 hour
        alpha = 0  # %

        facility_data = read_facility_data_from_file("model_checks/mc1_5step.csv", NS, P)

        # Constants
        KC = 45  # Ideal Density at capacity
        KJ = 190  # Facility-wide jam density
        L = [2640, 2640, 2640, 2640, 2640]  # Length of each segment
        L = [el_l/5280.0 for el_l in L]
        SC = facility_data["SC"]  # Segment capacity of segment i in interval p
        mainline_demand = [4000, 5100, 4500, 4000]
        N = facility_data["NL"]  # Number of open lanes in segment i in interval p
        WS = lambda i, p: SC[i][p]/(N[i][p] * (KJ-KC))  # Wave speed for segment i in interval p
        WTT = lambda i, p: int(round(Th * (L[i]/5280.0/WS(i, p))))  # Wave travel time
        ONRD = facility_data["ONRD"]  # Demand flow rate for ONR at node i in interval p
        ONRCv = facility_data["ONRC"]
        ONRC = lambda i, t, p: ONRCv[i][p]  # Geometric capacity of ONR at node i in period t in interval p
        RM = facility_data["RM"]  # Ramp metering rate of node i during interval p (veh/h)
        OFRD = facility_data["OFRD"]  # Demand flow rate for OFR at node i in interval p
        SD = compute_segment_demand(NS, mainline_demand, ONRD, OFRD) # Segment demand for segment i in time interval p
        V = facility_data["V"]
        return {"NS":NS,"Stilde":Stilde,"Ftilde":Ftilde,"Ntilde":Ntilde,"Wtilde":Wtilde,"P":P,"Ptilde":Ptilde,"S":S,
                "Ttilde":Ttilde,"Th":Th,"alpha":alpha,"KC":KC,"KJ":KJ,"L":L,"SC":SC,"mainline_demand":mainline_demand,
                "N":N,"WS":WS,"WTT":WTT,"ONRD":ONRD,"ONRC":ONRC,"RM":RM,"OFRD":OFRD,"SD":SD,"KB":facility_data["KB"],
                "nvuv_fname":'model_checks/caf_calib1_5step_nvuv.csv', "V": V}
                
def read_facility_data_from_file(fname, NS, P):
    KB = zeros((NS, P))
    SC = zeros((NS, P))
    NL = zeros((NS, P))
    ONRD = zeros((NS, P))
    ONRC = zeros((NS, P))
    RM = zeros((NS, P))
    OFRD = zeros((NS, P))
    V = zeros((NS,P))
    f = open(fname)
    f.readline()
    for line in f:
        tokens = line.split(",")
        seg = int(tokens[1])
        per = int(tokens[2])
        KB[seg, per] = float(tokens[3])
        SC[seg, per] = float(tokens[4])
        NL[seg, per] = float(tokens[5])
        ONRD[seg, per] = float(tokens[6])
        ONRC[seg, per] = float(tokens[7])
        RM[seg, per] = float(tokens[8])
        OFRD[seg, per] = float(tokens[9])
        V[seg, per] = float(tokens[11])
    facility = {"KB":KB.tolist(),
                "SC":SC.tolist(),
                "NL":NL.tolist(),
                "ONRD":ONRD.tolist(),
                "ONRC":ONRC.tolist(),
                "RM":RM.tolist(),
                "OFRD":OFRD.tolist(),
                "V":V.tolist()}
    return facility

def compute_segment_demand(num_seg, mainline_demand, ONRD, OFRD):
    SD = []
    SD.append(mainline_demand)
    for seg in xrange(1, num_seg):
        SD.append([])
        for period in xrange(len(mainline_demand)):
            SD[seg].append(SD[seg-1][period] + ONRD[seg][period]- OFRD[seg-1][period])
    return SD

def compute_estimated_demand(SC, SD):
    ED = []
    for seg in xrange(len(SC)):
        ED.append([])
        for period in xrange(len(SC[0])):
            ED[seg].append(min(SC[seg][period], SD[seg][period]))
    return ED