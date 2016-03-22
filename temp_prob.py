from __future__ import division
import gurobipy as gbp
from numpy import *

# Problem data
m = 4
n = 6
c_dat = [[23, 12, 34, 25, 27, 16],
        [29, 24, 43, 35, 28, 19],
        [43, 31, 52, 36, 30, 21],
        [54, 36, 54, 46, 34, 27]]
a_dat = [15, 25, 40, 70]
b_dat = [10, 5, 7, 4]
d_dat = [45, 120, 165, 214, 64, 93]

# Creating numpy arrays to hold matrices and vectos
C = array(c_dat)    # Create 4 by 6 C matrix
a = array(a_dat)  # Create 1 by 4 a vector
b = array(b_dat)  # Create 1 by 4 b vector
d = array(d_dat)  # Create 1 by 4 d vector

# Creating Gurobi model
g = gbp.Model("problem 13")

# Adding Gurobi variables
x=[]
obj_sum = 0
for i in xrange(m):
    x.append([])
    for j in xrange(n):
        x[i].append(g.addVar(vtype=gbp.GRB.INTEGER, name='x_'+str(i)+'_'+str(j)))
        obj_sum = obj_sum + (C[i][j] * x[i][j])
g.update()

# Setting Objective
g.setObjective(obj_sum, gbp.GRB.MINIMIZE)
g.update()

# Adding Constraints
for i in xrange(m):
    constr1_sum = 0
    for j in xrange(n):
        constr1_sum = constr1_sum + x[i][j]
    g.addConstr(constr1_sum <= b[i], name='constr1_'+str(i))

for j in xrange(n):
    constr2_sum = 0
    for i in xrange(m):
        constr2_sum = constr2_sum + (a[i]*x[i][j])
    g.addConstr(constr2_sum >= d[j], name='constr2_'+str(j))

g.addConstr((3/4)*x[0][0] + x[1][0] + (3/4)*x[2][0] + 3*x[3][0] >= 2)  # 48 nodes
g.addConstr((3/4)*x[0][1] + x[1][1] + (3/4)*x[2][1] + 3*x[3][1] >= 5)  # 0 nodes
g.addConstr(x[0][2] + x[1][2] + 2*x[2][2] + 3*x[3][2] >= 7)  # 0 nodes
#g.addConstr(x[0][3] + x[1][3] + 2*x[2][3] + 3*x[3][3] >= 9)  # 24 nodes
#g.addConstr(x[0][4] + x[1][4] + 2*x[2][4] + 3*x[3][4] >= 3)  # 6 nodes


#g.addConstr(x[0][0] + x[1][0] + x[2][0] + 2*x[3][0] >= 2)  # 6 nodes
#g.addConstr(x[0][2] + x[1][2] + x[2][2] + 2*x[3][2] >= 5)  # 4 nodes

g.update()

g.optimize()
