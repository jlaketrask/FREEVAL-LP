__author__ = 'jtrask'

def mst_creator(input_file_name, output_file_name):
    f1 = open(input_file_name, 'r')
    f2 = open(output_file_name, 'w')
    f1.readline() #Skipping first line
    for line in f1:
        tokens = line.split(',')
        i=tokens[0]
        p=tokens[1]
        t=tokens[2]
        f2.write('NV'+i+t+p+' '+tokens[3]+'\n')
        f2.write('ONRF'+i+t+p+' '+tokens[9]+'\n')
        f2.write('OFRF'+i+t+p+' '+tokens[10]+'\n')
        #f2.write('NV'+'\n')
        #f2.write('NV'+'\n')
    f1.close()
    f2.close()
