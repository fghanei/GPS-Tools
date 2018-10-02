import os
import shutil
import argparse

# setting up the parser
parser = argparse.ArgumentParser(description="Get travel distance our ofwaypoint file. As of now it only takes on mission file, consiss only of waypoints")
parser.add_argument("-r", "--resolution", help="The resolution that grid is intended to made at.")
args = parser.parse_args()

RESOLUTION=10.0 #default value
if args.resolution:
    RESOLUTION = float(args.resolution)

input_file = ["42.99849",
        "-78.77810",
        str(RESOLUTION),  #resolution
        "16.0",  #offset_x (should be >= resolution?)
        "12.0",  #offset_y (should be >= resolution?)
        ""]

all_summary = open("all_summary.txt", "a")
all_summary.write("AREA\t   CPLEX\t    LKHD\t     DLS\n")

for i in range(8,9): # (2,9)
    for j in range(6,11): # (i,13)
#        print "Running scripts for grid size: %dx%d"%(i,j)
        print "Running scripts for area: %d"%(j)
        shutil.copy("input_area_%d"%(j),"input")
#      inp = open("input", "w")
#       inp.write("\n".join(input_file))
#       inp.write(str(i)+"\n")
#       inp.write(str(j)+"\n")
#       for zj in range(j):
#           inp.write("0"*i + "\n")
#       inp.close()
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
        cost = [-1] * 4        
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
            while not "Total Cost" in line:
                line = lines[k]
                k+=1
            cost[index] = float(line.strip().split(':')[1].split(' ')[-1])

        print "The costs are as follows: " + str(cost)
        sum_file.close()
        all_summary.write("%4d\t%8.1f\t%8.1f\t%8.1f\n"%(j,cost[0],cost[1],cost[2]))
        all_summary.flush()
        try:
            os.rename("./new_data", "area_%d"%(j))
        except:
            pass
        
