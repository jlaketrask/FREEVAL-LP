from __future__ import division
from pylab import *

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

def compute_background_density(ED, Ftilde, Ntilde, Wtilde):
    KB = []
    for i in xrange(len(ED)):
        KB.append([])
        if i in Ftilde: #OFR segment
            func_speed = func_speed_ofr
        elif i in Ntilde: #ONR segment
            func_speed = func_speed_onr
        elif i in Wtilde:
            func_speed = func_speed_w
        else:
           func_speed = func_speed_basic
        for p in xrange(len(ED[0])):
            KB[i].append(ED[i][p]/func_speed(ED[i][p],i, p))
    return KB

def read_background_density_from_file(fname, NS, P):
    KB = zeros((NS, P))
    f = open(fname)
    f.readline()
    for line in f:
        tokens = line.split(",")
        KB[int(tokens[1]), int(tokens[2])] = float(tokens[3])
    return KB.tolist()

def read_segment_capacity_from_file(fname, NS, P):
    SC = zeros((NS, P))
    f = open(fname)
    f.readline()
    for line in f:
        tokens = line.split(",")
        SC[int(tokens[1]), int(tokens[2])] = float(tokens[3])
    return SC.tolist()

def read_facility_data_from_file(fname, NS, P):
    KB = zeros((NS, P))
    SC = zeros((NS, P))
    NL = zeros((NS, P))
    ONRD = zeros((NS, P))
    ONRC = zeros((NS, P))
    RM = zeros((NS, P))
    OFRD = zeros((NS, P))
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
    facility = {"KB":KB.tolist(),
                "SC":SC.tolist(),
                "NL":NL.tolist(),
                "ONRD":ONRD.tolist(),
                "ONRC":ONRC.tolist(),
                "RM":RM.tolist(),
                "OFRD":OFRD.tolist()}
    return facility

def unified_speed_eqn(volume, ffs, base_seg_capacity=None, breakpoint=None, a=2):
    if base_seg_capacity is None:
        base_seg_capacity = 2200+10*(min(70,ffs) - 50)
    if breakpoint is None:
        breakpoint = 1000+40*(75-ffs)
    if volume <= breakpoint:
        return ffs
    else:
        return ffs - ((ffs-base_seg_capacity/45)*(volume - breakpoint)**a)/(base_seg_capacity - breakpoint)**a

def func_speed_basic(volume, seg, period):
    return unified_speed_eqn(volume)

def func_speed_ofr(volume, seg, period):
    return 65

def func_speed_onr(volume, seg, period):
    return 65

def func_speed_w(volume, seg, period):
    return 65