__author__ = 'jtrask'

def mst_creator(input_file_name, output_file_name):
    f1 = open(input_file_name, 'r')
    f2 = open(output_file_name, 'w')
    f1.readline() #Skipping first line
    temp_mf = 0
    for line in f1:
        tokens = line.split(',')
        i=tokens[0]
        p=tokens[1]
        t=tokens[2]
        f2.write('NV'+i+'_'+t+'_'+p+' '+tokens[3]+'\n')
        f2.write('ONRF'+i+'_'+t+'_'+p+' '+tokens[9]+'\n')
        f2.write('OFRF'+i+'_'+t+'_'+p+' '+tokens[10]+'\n')
        # if int(p) is 2:
        #     temp_mf = float(tokens[4])
        #     f2.write('MF'+str(int(i)+1)+t+p+' '+tokens[4]+'\n')
        # elif int(p) is 3:
        #     f2.write('MF'+str(int(i)+1)+t+p+' '+temp_mf+'\n')
        # else:
        #      f2.write('MF'+str(int(i)+1)+t+p+' '+tokens[4]+'\n')
        f2.write('UV'+i+'_'+t+'_'+p+' '+tokens[12]+'\n')
        if float(tokens[12]) > 0.01:
            f2.write('I_UV0'+i+'_'+t+'_'+p+' '+str(1)+'\n')
            f2.write('I_UV1'+i+'_'+t+'_'+p+' '+str(0)+'\n')
        else:
            f2.write('I_UV0'+i+'_'+t+'_'+p+' '+str(0)+'\n')
            f2.write('I_UV1'+i+'_'+t+'_'+p+' '+str(1)+'\n')
        #f2.write('NV'+'\n')
        #f2.write('NV'+'\n')
    f1.close()
    f2.close()
