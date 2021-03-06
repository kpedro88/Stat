#!/bin/bash

for MU in 0; do
	for SIGMA in 0 1 2 3 4; do
		NAME=gaus_m${MU}_s${SIGMA}
		echo "Signal: $NAME"
		combine -M FitDiagnostics dijet_combine_${NAME}.txt --robustFit=1 --setRobustFitTolerance=1. -t 300 --toysFrequentist --saveToys --expectSignal 0.0 --rMin -80 --rMax 80 -n bias_$NAME
	done
done
