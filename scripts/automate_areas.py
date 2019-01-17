import os
import shutil
import argparse

# setting up the parser
parser = argparse.ArgumentParser(description="Goes through input_area_# files and runs run.sh on them and saves results.")
parser.add_argument("-r", "--resolution", help="The resolution that grid is intended to made at.")
args = parser.parse_args()

RESOLUTION=10.0 #default value
if args.resolution:
    RESOLUTION = float(args.resolution)

all_summary = open("all_summary.txt", "a")
all_summary.write("AREA\t   CPLEX\t    LKHD\t     DLS\t     LKH\n")

for i in range(201,205):
    print "Running scripts for area: %d"%(i)
    shutil.copy("input_area_%d"%(i),"input")
    try:
        shutil.rmtree('./new_data')
    except:
        pass
    try:
        os.system("./run.sh %f > summary.txt"%(RESOLUTION));
    except:
        pass
    sum_file = open("./new_data/summary.txt", "r")
    lines = sum_file.readlines()
    cost = [-1] * 5        
    index = -1
    k=0
    while k < len(lines):
        line = lines[k]
        k+=1
        if not "mission" in line:
            continue
        if "cplex" in line:
            index=0
        elif "lkhd" in line:
            index=1
        elif "dls" in line:
            index=2
        elif "lkh" in line:
            index=3
        while not "Total Cost" in line:
            line = lines[k]
            k+=1
        cost[index] = float(line.strip().split(':')[1].split(' ')[-1])

    print "The costs are as follows: " + str(cost)
    sum_file.close()
    all_summary.write("%4d\t%8.1f\t%8.1f\t%8.1f\t%8.1f\n"%(i,cost[0],cost[1],cost[2],cost[3]))
    all_summary.flush()
    try:
        os.rename("./new_data", "area_%d"%(i))
    except:
        pass
    
