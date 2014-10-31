import gurobipy as gbp


def generate_max_constrs(model, var1, var2, var3, M, M1, M2, label1, label2):
    temp_binary_vars = [model.addVar(vtype=gbp.GRB.BINARY, name=label1+'_I'+label2) for v in xrange(2)]
    model.update()

    # Constraints setting indicator varibles
    model.addConstr(var2 - var3 <= M*temp_binary_vars[0], name=label1+'_Max1'+label2)
    model.addConstr(var3 - var2 <= M*temp_binary_vars[1], name=label1+'_Max2'+label2)
    # Sum of indicator variables must be 1
    model.addConstr(temp_binary_vars[0]+temp_binary_vars[1] == 1, name=label1+'_Max3'+label2)
    # Constraints assigning min value
    model.addConstr(var1 - var2 <= M1*temp_binary_vars[1], name=label1+'_D1'+label2)
    model.addConstr(var2 - var1 <= M1*temp_binary_vars[1], name=label1+'_D2'+label2)
    model.addConstr(var1 - var3 <= M2*temp_binary_vars[0], name=label1+'_D3'+label2)
    model.addConstr(var3 - var1 <= M2*temp_binary_vars[0], name=label1+'_D4'+label2)
    model.update()


def generate_min_constrs(model, var1, var2, var3, M, M1, M2, label1, label2):
    temp_binary_vars = [model.addVar(vtype=gbp.GRB.BINARY, name=label1+'_I'+label2) for v in xrange(2)]
    model.update()

    # Constraints setting indicator varibles
    model.addConstr(var2 - var3 <= M*temp_binary_vars[0], name=label1+'_Max1'+label2)
    model.addConstr(var3 - var2 <= M*temp_binary_vars[1], name=label1+'_Max2'+label2)
    # Sum of indicator variables must be 1
    model.addConstr(temp_binary_vars[0]+temp_binary_vars[1] == 1, name=label1+'_Max3'+label2)
    # Constraints assigning min value
    model.addConstr(var1 - var2 <= M1*temp_binary_vars[0], name=label1+'_D1'+label2)
    model.addConstr(var2 - var1 <= M1*temp_binary_vars[0], name=label1+'_D2'+label2)
    model.addConstr(var1 - var3 <= M2*temp_binary_vars[1], name=label1+'_D3'+label2)
    model.addConstr(var3 - var1 <= M2*temp_binary_vars[1], name=label1+'_D4'+label2)
    model.update()


def sum_sum_add_t_p(var_list1, var_list2, i, t, p):
    # Sums at i, from 0 through t, from 0 through p (inclusive)
    sum = 0
    for el_p in xrange(p+1):
        for el_t in xrange(t+1):
            sum = sum + var_list1[i][el_t][el_p] + var_list2[i][el_t][el_p]
    return sum

def sum_add_t(var_list1, var_list2, i, t, p):
    # Sums at i, from 0 through t (inclusive), at p
    sum = 0
    for el_t in xrange(t+1):
        sum = sum + var_list1[i][el_t][p] + var_list2[i][el_t][p]
    return sum


def test_func():
    test = gbp.Model('test')
    x = test.addVar(vtype=gbp.GRB.CONTINUOUS, name="x")
    y = test.addVar(vtype=gbp.GRB.CONTINUOUS, name="y")
    z = test.addVar(vtype=gbp.GRB.CONTINUOUS, name="z")
    test.update()
    test.setObjective(x, gbp.GRB.MAXIMIZE)
    test.update()
    test.addConstr(y == 2, name='c1')
    test.addConstr(z == 3, name='c2')
    a = [0,y,z]
    generate_max_constrs(test, x, sum(a), 1, 10, 10, 10, "c", "11")
    test.optimize()