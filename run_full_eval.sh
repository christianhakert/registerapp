#!/bin/bash

#iterate over window sizes

echo "window_size,num_tracks,track_length,num_aps,benchmark,v1_total_shifts,v2_total_shifts,opt_total_shifts,recommended_total_shifts,v1_total_energy,v2_total_energy,opt_total_energy,recommended_total_energy,v1_total_latency,v2_total_latency,opt_total_latency,recommended_total_latency" > results.csv

rm -Rf parrun
mkdir parrun
par_id=1

parallel_process() {
    my_par_id=$1
    cd parrun/$my_par_id
    window_size=$2
    num_nanotracks=$3
    nanotrack_length=$4
    number_access_ports=$5
    file=../../$6

    echopfx="[$my_par_id]-[$window_size]-[$num_nanotracks]-[$nanotrack_length]-[$number_access_ports]-[$file]:"

    #Generate a racetrack_params.py file
    echo "execution_window = $window_size" > racetrack_params.py
    echo "N = $num_nanotracks" >> racetrack_params.py
    echo "W = $nanotrack_length" >> racetrack_params.py
    echo "nap = $number_access_ports" >> racetrack_params.py

    echo "$echopfx Running $file"

    #Do cfgtrace
    echo "$echopfx Running cfgtrace"
    python3 cfgtrace.py $file

    #Evaluate trace afterwards
    echo "$echopfx Evaluating trace"
    resline=$(python3 eval_trace.py $file)
    echo "$window_size,$num_nanotracks,$nanotrack_length,$number_access_ports,$file,$resline" > lresults.csv
    mv rtstats.csv static_rtstats.csv
    mv shiftresults.csv static_shift_results.csv

    #generate probability distribution
    python3 record_branch_probabilities.py $file
    #move away old shift results
    python3 cfgtrace.py $file

    resline=$(python3 eval_trace.py $file)
    echo "$window_size,$num_nanotracks,$nanotrack_length,$number_access_ports,prob_$file,$resline" >> lresults.csv
    mv shiftresults.csv prob_shift_results.csv
    mv rtstats.csv prob_rtstats.csv
}

export -f parallel_process

for window_size in 10 100 1000 2000;do
# for window_size in 100;do
    # echo "Window size: $window_size"
    for ntp in $(seq 0 11);do
    # for ntp in $(seq 6 6);do
        num_nanotracks=$((2**$ntp))
        # echo "Number of nanotracks: $num_nanotracks"
        nanotrack_length=$(((32*64)/$num_nanotracks))
        # echo "Nanotrack length: $nanotrack_length"

        max_num_aps=$nanotrack_length
        #min_num_aps is max of 1, nanotrack_length/64 or 64/num_nanotracks
        min_num_aps=$(($nanotrack_length/64))
        if [ $min_num_aps -lt 1 ]; then
            min_num_aps=1
        fi
        if [ $min_num_aps -lt $((64/$num_nanotracks)) ]; then
            min_num_aps=$((64/$num_nanotracks))
        fi
        
        for napp in $(seq 0 11);do
        # for napp in $(seq 0 0);do
            number_access_ports=$((2**$napp))
            if [ $number_access_ports -lt $min_num_aps ]; then
                continue
            fi

            if [ $number_access_ports -gt $max_num_aps ]; then
                continue
            fi

            # echo "Number of access ports: $number_access_ports"            

            #Go through benchmarks
            for file in binaries/*; do
            # for file in binaries/qsort_O3; do
                if [ -x $file ]; then
                    #Check if file is not .sh
                    if [[ $file != *.sh ]]; then
                        my_par_id=$par_id
                        par_id=$((par_id+1))

                        mkdir -p parrun/$my_par_id
                        cp cfgtrace.py parrun/$my_par_id/.
                        cp eval_trace.py parrun/$my_par_id/.
                        cp racetrack.py parrun/$my_par_id/.
                        cp record_branch_probabilities.py parrun/$my_par_id/.

                        echo "Launching new analysis with $file with window size $window_size, $num_nanotracks nanotracks, $nanotrack_length nanotrack length and $number_access_ports access ports"

                        sem -j 30 parallel_process $my_par_id $window_size $num_nanotracks $nanotrack_length $number_access_ports $file
                        # parallel_process $my_par_id $window_size $num_nanotracks $nanotrack_length $number_access_ports $file
                    fi
                fi
            done
        done

    done
done

sem --wait

#Collect parallel results
cat parrun/*/lresults.csv >> results.csv