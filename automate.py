import os
import shutil

lines = ["42.99849",
        "-78.77810",
        "10.0",
        "10.0",
        "10.0",
        ""]

for i in range(2,9):
    for j in range(i,13):
        inp = open("input", "w")
        inp.write("\n".join(lines))
        inp.write(str(i)+"\n")
        inp.write(str(j)+"\n")
        for zj in range(j):
            inp.write("0"*i + "\n")
        inp.close()
        try:
            shutil.rmtree('./new_data')
        except:
            pass
        try:
            os.system("./run.sh > summary.txt");
        except:
            pass
        try:
            os.rename("./new_data", "%dx%d"%(i,j))
        except:
            pass
        
