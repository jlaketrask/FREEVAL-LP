# -*- coding: utf-8 -*-
#from numpy import zeros
xrange = range

def zeros(shape):
    return [[0 for el in xrange(shape[1])] for el2 in xrange(shape[0])]

#import matplotlib.pyplot as plt
#from numpy import argsort
#kq=[]
#sf=[]
#kbar=[]
#asf=[]
#f=open('temp.csv', 'r')
#f.readline()
#for line in f:
#    tokens = line.split(',')
#    kq.append(float(tokens[0]))
#    sf.append(float(tokens[1]))
#    kbar.append(float(tokens[2]))
#    asf.append(float(tokens[3]))
#    
#kq_sorter = argsort(kq)
#kbar_sorter = argsort(kbar)
#xk1 = [kq[el] for el in kq_sorter]
#ysf1 = [sf[el] for el in kq_sorter]
#xk2 = [kbar[el] for el in kbar_sorter]
#ysf2 = [asf[el] for el in kbar_sorter]
#x3 = [el for el in range(0,361)]
#x3.reverse()
#y3 = [190*3-(145*3*el)/360 for el in x3]
#x4 = [el for el in range(55,281)]
#y4 = [(190*3-el)*(360/(145*3)) for el in x4]
#fig = plt.figure(1)
#plt.plot(xk1, ysf1, figure=fig, label='SF (KQ)')
#plt.plot(xk2, ysf2, figure=fig, label='ASF (KBar)')
#plt.plot(x3, y3, figure=fig, label = 'True F-D Line')
#plt.plot(x4, y4, figure=fig, label = 'True ASF Line')
#plt.title('Flow Density Graph')
#plt.xlabel('Density')
#plt.ylabel('Flow')
#plt.legend()
#plt.grid(True)
#plt.savefig('fdc_mc5.png')
#plt.show()



def extract(example_problem):
    if example_problem is 0:
        # Model Check 1
        facility = Facility('model_checks/model_check1.txt', 5)
        facility.fill_outputs('model_checks/mc1_5step.csv')
        facility.fill_nvuv('model_checks/mc1_5step_nvuv.csv', True)
        return facility
        
    elif example_problem is 1:
        # Model Check 2 (off-ramp)
        facility = Facility('model_checks/model_check2.txt', 5)
        facility.fill_outputs('model_checks/mc2_5step.csv')
        facility.fill_nvuv('model_checks/mc2_5step_nvuv.csv', True)
        return facility
                
    elif example_problem is 2:
        # Model Check 3 (on-ramp 1)
        facility = Facility('model_checks/model_check3.txt', 5)
        facility.fill_outputs('model_checks/mc3_5step.csv')
        facility.fill_nvuv('model_checks/mc3_5step_nvuv.csv', True)
        return facility
                
    elif example_problem is 3:
        # Model Check 4 (on-ramp 2)
        facility = Facility('model_checks/model_check4.txt', 5)
        facility.fill_outputs('model_checks/mc4_5step.csv')
        facility.fill_nvuv('model_checks/mc4_5step_nvuv.csv', True)
        return facility
        
    elif example_problem is 4:
        # Model Check 5 (MO2 test - Queue Spillback)
        facility = Facility('model_checks/model_check5.txt', 5)
        facility.fill_outputs('model_checks/mc5_5step.csv')
        facility.fill_nvuv('model_checks/mc5_5step_nvuv.csv', True)
        return facility
                
    elif example_problem is 5:
        # Model Check 1 with CAF of 0.98 at segment 3
        facility = Facility('model_checks/model_check1.txt', 5)
        facility.fill_outputs('model_checks/mc1_5step.csv')
        facility.fill_nvuv('model_checks/caf_calib1_5step_nvuv.csv', True)
        return facility
    
    elif example_problem is 6:
        # Modified GPEX1 with 60 step resolution
        facility = Facility('model_checks/gpex2_mod_full.txt', 60)
        facility.fill_outputs('model_checks/gpex2_full.csv')
        facility.fill_nvuv('model_checks/gpex2_full_nvuv.csv', True)
        return facility
        
    elif example_problem is 7:
        # Modified I-40 example with 60 step resolution
        facility = Facility('model_checks/i40_mod_full.txt', 60)
        facility.fill_outputs('model_checks/i40_full.csv')
        facility.fill_nvuv('model_checks/i40_mod_full_nvuv.csv', True)
        return facility
                
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
                
    
class Facility:
    def __init__(self, fname, num_steps):
        self.KC = 45  # Ideal Density at capacity
        f = open(fname, 'r')
        f.readline()            # <001> Project Name
        self.name=f.readline()  # (Actual project name)
        f.readline()            # <002> Study Period Start Time
        tokens = f.readline().split(':')
        self.start_hour = int(tokens[0])
        self.start_min = int(tokens[1])
        f.readline()            # <003> Study Period End Time
        tokens = f.readline().split(':')
        self.end_hour = int(tokens[0])
        self.end_min = int(tokens[1])
        self.P = int((self.end_hour-self.start_hour)*4 + (self.end_min-self.start_min)/15)
        self.S = num_steps
        self.Th = 4*self.S     # Number of time steps in 1 hour
        f.readline()            # <004> Number of segments
        self.NS = int(f.readline())
        f.readline()            # <005> Free Flow Speed Known?
        self.ffs_known = True
        if f.readline() == 'false':
            self.ffs_known = False
        f.readline()            # <007> Managed Lane Used?
        self.has_ML = False
        if f.readline() == 'true':
            self.has_ML = True
        f.readline()            # <008> Capacity Drop (%)
        self.alpha = int(f.readline())
        f.readline()            # <009> Jam Density (pc/mi/ln)
        self.KJ = float(f.readline())
        f.readline()            # <010> Seed Demand Data
        self.seed_demand_date = f.readline()
        f.readline()            # <011> GP Segment Vehicle Occupancy
        self.gp_seg_veh_occ = float(f.readline())
        f.readline()            # <012> ML Segment Vehicle Occupancy
        self.ml_seg_veh_occ = float(f.readline())
        f.readline()            # <013> Urban(=1)/Rural(=2) Type
        self.facility_type = int(f.readline())
        f.readline()            # <101> General Purpose Segment Type (Basic = 0, ONR = 1, OFR = 2, Overlap = 3, Weaving = 4, Access = 8)
        f.readline()
        tokens = f.readline().strip().split()
        self.Ftilde = []  # List of OFR segments
        self.Ntilde = []  # List of ONR segments
        self.Wtilde = []  # List of Weave segments
        for seg in xrange(len(tokens)):
            if int(tokens[seg]) == 1:
                self.Ntilde.append(seg)
            elif int(tokens[seg]) == 2:
                self.Ftilde.append(seg)
            elif int(tokens[seg]) == 4:
                self.Ntilde.append(seg)
                self.Ftilde.append(seg)

        f.readline()            # <102> Segment Length (ft)
        f.readline()
        tokens_L = f.readline().strip().split()
        f.readline()            # <103> Lane Width (ft)
        f.readline()
        tokens_LW = f.readline().strip().split()
        f.readline()            # <104> Lateral Clearance (ft)
        f.readline()
        tokens_LC = f.readline().strip().split()
        f.readline()            # <105> Terrain (Level = 1, Rolling = 3, Varying = 4)
        f.readline()
        tokens_T = f.readline().strip().split()
        f.readline()            # <106> Truck-PC Equivalent (ET)
        f.readline()
        tokens_TPCE = f.readline().strip().split()
        self.L_ft = [] # List of segment lengths
        self.L_mi = []
        self.lane_width = [] # List of segment lane widths (ft)
        self.lat_clearance = [] # List of segment lateral clearances (ft)
        self.terrain = [] # List of segment terrain types
        self.truck_pc_equiv = [] # List of segment truck-pc equivalents
        for seg in xrange(len(tokens_L)):
            self.L_ft.append(int(tokens_L[seg]))
            self.L_mi.append(self.L_ft[seg]/5280.0)
            self.lane_width.append(int(tokens_LW[seg]))
            self.lat_clearance.append(int(tokens_LC[seg]))
            self.terrain.append(int(tokens_T[seg]))
            self.truck_pc_equiv.append(float(tokens_TPCE[seg]))
            
        # Initializing input matrices
        self.NL = zeros((self.NS, self.P))
        self.ffs = zeros((self.NS, self.P))
        self.mainline_demand = []
        self.sut_pct = zeros((self.NS, self.P))
        self.tt_pct = zeros((self.NS, self.P))
        self.seed_CAF = zeros((self.NS, self.P))
        self.seed_OAF = zeros((self.NS, self.P))
        self.seed_DAF = zeros((self.NS, self.P))
        self.seed_SAF = zeros((self.NS, self.P))
        self.seed_DPCAF = zeros((self.NS, self.P))
        self.seed_DPSAF = zeros((self.NS, self.P))
        
        f.readline()            # <108> # of Lanes: Mainline
        f.readline()
        for per in xrange(self.P):
            tokens = f.readline().strip().split()
            for seg in xrange(self.NS):
                self.NL[seg][per] = int(tokens[seg+1])
        f.readline()            # <109> Free Flow Speed (mph)
        f.readline()
        for per in xrange(self.P):
            tokens = f.readline().strip().split()
            for seg in xrange(self.NS):
                self.ffs[seg][per] = int(tokens[seg+1])
        f.readline()            # <110> Mainline Dem. (vph)
        f.readline()
        for per in xrange(self.P):
            tokens = f.readline().strip().split()
            self.mainline_demand.append(int(tokens[1]))
        f.readline()            # <111> Single Unit Truck and Bus (%) 
        f.readline()
        for per in xrange(self.P):
            tokens = f.readline().strip().split()
            for seg in xrange(self.NS):
                self.sut_pct[seg][per] = float(tokens[seg+1])
        f.readline()            # <112> Tractor Trailer (%)
        f.readline()
        for per in xrange(self.P):
            tokens = f.readline().strip().split()
            for seg in xrange(self.NS):
                self.tt_pct[seg][per] = float(tokens[seg+1])
        f.readline()            # <113> Seed Capacity Adj. Fac. 
        f.readline()
        for per in xrange(self.P):
            tokens = f.readline().strip().split()
            for seg in xrange(self.NS):
                self.seed_CAF[seg][per] = float(tokens[seg+1])
        f.readline()            # <114> Seed Entering Dem. Adj. Fac. 
        f.readline()
        for per in xrange(self.P):
            tokens = f.readline().strip().split()
            for seg in xrange(self.NS):
                self.seed_OAF[seg][per] = float(tokens[seg+1])
        f.readline()            # <115> Seed Exit Dem. Adj. Fac.
        f.readline()
        for per in xrange(self.P):
            tokens = f.readline().strip().split()
            for seg in xrange(self.NS):
                self.seed_DAF[seg][per] = float(tokens[seg+1])
        f.readline()            # <116> Seed Free Flow Speed Adj. Fac.
        f.readline()
        for per in xrange(self.P):
            tokens = f.readline().strip().split()
            for seg in xrange(self.NS):
                self.seed_SAF[seg][per] = float(tokens[seg+1])
        f.readline()            # <134> Seed Driver Population Capacity Adj. Fac.
        f.readline()
        for per in xrange(self.P):
            tokens = f.readline().strip().split()
            for seg in xrange(self.NS):
                self.seed_DPCAF[seg][per] = float(tokens[seg+1])        
        f.readline()            # <135> Seed Driver Population Free Flow Speed Adj. Fac.
        f.readline()
        for per in xrange(self.P):
            tokens = f.readline().strip().split()
            for seg in xrange(self.NS):
                self.seed_DPSAF[seg][per] = float(tokens[seg+1])
                

        # Initialzing ONR Inputs
        self.onr_nl = zeros((self.NS, self.P))
        self.onr_ffs = zeros((self.NS, self.P))
        self.ONRD = zeros((self.NS, self.P))
        self.RM = zeros((self.NS, self.P))                
        f.readline()            # <118> Acc/Dec Lane Length (ft)
        f.readline()
        tokens = f.readline().strip().split()
        self.acc_dec_lane_len = [int(val) if val != 'N/A' else -1  for val in tokens]
        f.readline()            # <117> ONR Side (Right = 0, Left = 1)
        f.readline()
        tokens = f.readline().strip().split()
        self.onr_side = [int(val) if val != 'N/A' else -1  for val in tokens]
        f.readline()            # <119> # Lanes: ONR
        f.readline()
        for per in xrange(self.P):
            tokens = f.readline().strip().split()
            for seg in xrange(self.NS):
                self.onr_nl[seg][per] = int(tokens[seg+1]) if tokens[seg+1] != 'N/A' else 0
        f.readline()            # <120> ONR Free Flow Speed (mph)
        f.readline()
        for per in xrange(self.P):
            tokens = f.readline().strip().split()
            for seg in xrange(self.NS):
                self.onr_ffs[seg][per] = int(tokens[seg+1]) if tokens[seg+1] != 'N/A' else 0
        f.readline()            # <121> ONR/Entering Dem. (vph)
        f.readline()
        for per in xrange(self.P):
            tokens = f.readline().strip().split()
            for seg in xrange(self.NS):
                self.ONRD[seg][per] = int(tokens[seg+1]) if tokens[seg+1] != 'N/A' else 0
        f.readline()            # <122> ONR Metering Rate (vph)
        f.readline()
        for per in xrange(self.P):
            tokens = f.readline().strip().split()
            for seg in xrange(self.NS):
                self.RM[seg][per] = int(tokens[seg+1]) if tokens[seg+1] != 'N/A' else 2400
                
        # Initialzing OFR Inputs
        self.ofr_nl = zeros((self.NS, self.P))
        self.ofr_ffs = zeros((self.NS, self.P))
        self.OFRD = zeros((self.NS, self.P))            
        f.readline()            # <123> OFR Side (Right = 0, Left = 1)
        f.readline()
        tokens = f.readline().strip().split()
        self.ofr_side = [int(val) if val != 'N/A' else -1 for val in tokens]
        f.readline()            # <124> # Lanes: OFR
        f.readline()
        for per in xrange(self.P):
            tokens = f.readline().strip().split()
            for seg in xrange(self.NS):
                self.ofr_nl[seg][per] = int(tokens[seg+1]) if tokens[seg+1] != 'N/A' else 0
        f.readline()            # <125> OFR Free Flow Speed (mph)
        f.readline()
        for per in xrange(self.P):
            tokens = f.readline().strip().split()
            for seg in xrange(self.NS):
                self.ofr_ffs[seg][per] = int(tokens[seg+1]) if tokens[seg+1] != 'N/A' else 0
        f.readline()            # <126> OFR/Exiting Dem. (vph)
        f.readline()
        for per in xrange(self.P):
            tokens = f.readline().strip().split()
            for seg in xrange(self.NS):
                self.OFRD[seg][per] = int(tokens[seg+1]) if tokens[seg+1] != 'N/A' else 0
          
        # Initialzing Weave Inputs
        self.rtr_demand = zeros((self.NS, self.P))
        f.readline()            # <127> Weave Segment Ls (ft)
        f.readline()
        tokens = f.readline().strip().split()
        self.weave_Ls = [int(val) if val!='N/A' else -1 for val in tokens]
        f.readline()            # <128> Weave Segment LCRF
        f.readline()
        tokens = f.readline().strip().split()
        self.weave_LCRF = [int(val) if val!='N/A' else -1 for val in tokens]
        f.readline()            # <129> Weave Segment LCFR
        f.readline()
        tokens = f.readline().strip().split()
        self.weave_LCFR = [int(val) if val!='N/A' else -1 for val in tokens]
        f.readline()            # <130> Weave Segment LCRR
        f.readline()
        tokens = f.readline().strip().split()
        self.weave_RR = [int(val) if val!='N/A' else -1 for val in tokens]
        f.readline()            # <131> Weave Segment NW
        f.readline()
        tokens = f.readline().strip().split()
        self.weave_NW = [int(val) if val != 'N/A' else -1 for val in tokens]
        f.readline()            # <132> Ramp to Ramp Dem. (vph)
        f.readline()
        for per in xrange(self.P):
            tokens = f.readline().strip().split()
            for seg in xrange(self.NS):
                self.rtr_demand[seg][per] = int(tokens[seg+1]) if tokens[seg+1] != 'N/A' else 0
        
        self.rm_used = zeros((self.NS, self.P))
        f.readline()            # <133> Ramp Metering Used?
        f.readline()
        for per in xrange(self.P):
            tokens = f.readline().strip().split()
            for seg in xrange(self.NS):
                self.rm_used[seg][per] = int(tokens[seg+1]) if tokens[seg+1] != 'N/A' else 2400
                
        f.close()

        # Initializing other facility matrices
        self.KB = zeros((self.NS, self.P))
        self.SC = zeros((self.NS, self.P))
        self.ONRC = zeros((self.NS, self.P))
        self.V = zeros((self.NS, self.P))
        self.SD = zeros((self.NS, self.P))
        self.ED = zeros((self.NS, self.P))
        self.fNV = []
        self.fUV = []
        self.fSF = []
        self.Vhr = []
        self.__compute_segment_demand()
        
        
    def fill_outputs(self, fname):
        f = open(fname, 'r')
        f.readline()
        for line in f:
            tokens = line.split(",")
            seg = int(tokens[1])
            per = int(tokens[2])
            self.KB[seg, per] = float(tokens[3])
            self.SC[seg, per] = float(tokens[4])
            # NL[seg, per] = float(tokens[5])
            # ONRD[seg, per] = float(tokens[6])
            self.ONRC[seg, per] = float(tokens[7])
            # RM[seg, per] = float(tokens[8])
            # OFRD[seg, per] = float(tokens[9])
            self.V[seg, per] = float(tokens[11])
        f.close()
        self.__compute_estimated_demand()
        
    def fill_nvuv(self, fname, compute_Vhr):
        self.fNV = zeros((self.NS, self.S, self.P))
        self.fUV = zeros((self.NS, self.S, self.P))
        self.fSF = zeros((self.NS, self.S, self.P))
        self.Vhr = zeros((self.NS, self.S, self.P))
        f = open(fname, 'r')
        f.readline()
        for line in f:
            tokens = line.split(',')
            seg = int(tokens[0])
            per = int(tokens[1])
            step = int(tokens[2])
            self.fNV[seg][step][per] = float(tokens[3])
            self.fUV[seg][step][per] = float(tokens[12])
            self.fSF[seg][step][per] = float(tokens[13])
            self.Vhr[seg][step][per] = float(tokens[13])*self.L_mi[seg]*self.Th/float(tokens[3])
        f.close()
        
    def WS(self, i, p):
        return self.SC[i][p]/(self.NL[i][p] * (self.KJ-self.KC))  # Wave speed for segment i in interval p
        
    def WTT(self, i, p):
        return int(round(self.Th * (self.L_mi[i]/self.WS(i, p))))  # Wave travel time
        
    def func_ONRC(self, i, t, p):
        return self.ONRC[i][p]
        
            
    def __compute_segment_demand(self):
        for seg in xrange(self.NS):
            for per in xrange(self.P):
                if seg == 0:
                    self.SD[0][per] = self.mainline_demand[per]
                else:
                    self.SD[seg][per]= self.SD[seg-1][per] + self.ONRD[seg][per]- self.OFRD[seg-1][per]
    
    def __compute_estimated_demand(self):
        for seg in xrange(self.NS):
            for per in xrange(self.P):
                self.ED[seg][per] = min(self.SC[seg][per], self.SD[seg][per])
    
        
        