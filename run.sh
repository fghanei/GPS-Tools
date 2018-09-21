#!/bin/bash
LAMBDA=0.1164
GAMMA=0.0173

set -e
python grid_generator.py input -g 
./ub-anc-planner-cplex -r 10 -a $LAMBDA -m $GAMMA -l 3600 > planner_log_cplex.txt 
python path_graph.py mission_cplex_0.txt -a $LAMBDA -m $GAMMA -g -x cplex
./ub-anc-planner-lkhd -r 10 -a $LAMBDA -m $GAMMA -l 3600 > planner_log_lkhd.txt 
python path_graph.py mission_lkhd_0.txt -a $LAMBDA -m $GAMMA -g -x lkhd
./ub-anc-planner-dls -r 10 -a $LAMBDA -m $GAMMA -l 3600 > planner_log_dls.txt 
python path_graph.py mission_dls_0.txt -a $LAMBDA -m $GAMMA -g -x dls
mkdir new_data 
mv grid.png grid.txt grid_log.txt mission_* path_*.png planner_log_* path_*.txt new_data/ 
cp input new_data/
echo "********************"
echo "All parts finished !"
echo "********************"
mv summary.txt new_data/
