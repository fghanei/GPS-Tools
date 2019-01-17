#!/bin/bash
LAMBDA=0.08874
GAMMA=-1.0
RES=$1

# this is the new linear model, for non linear GAMMA=-1
# LAMBDA=0.08874
# GAMMA=0.01497

# this is for older model
# LAMBDA=0.1164
# GAMMA=0.0173 

set -e
python grid_generator.py input -g -r $RES
set +e
./ub-anc-planner-cplex -r $RES -a $LAMBDA -m $GAMMA -l 3600 > planner_log_cplex.txt 
python path_graph.py mission_cplex_0.txt -a $LAMBDA -m $GAMMA -g -x cplex
./ub-anc-planner-lkhd -r $RES -a $LAMBDA -m $GAMMA -l 3600 > planner_log_lkhd.txt 
python path_graph.py mission_lkhd_0.txt -a $LAMBDA -m $GAMMA -g -x lkhd
./ub-anc-planner-dls -r $RES -a $LAMBDA -m $GAMMA -l 3600 > planner_log_dls.txt 
python path_graph.py mission_dls_0.txt -a $LAMBDA -m $GAMMA -g -x dls
./ub-anc-planner-lkh -r $RES -a $LAMBDA -m $GAMMA -l 3600 > planner_log_lkh.txt 
python path_graph.py mission_lkh_0.txt -a $LAMBDA -m $GAMMA -g -x lkh
set -e
mkdir new_data 
mv grid.png grid.txt grid_log.txt mission_* path_*.png planner_log_* path_*.txt new_data/ 
set +e
cp input new_data/
echo "********************"
echo "All parts finished !"
echo "********************"
mv summary.txt new_data/
