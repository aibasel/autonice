#! /bin/bash

set -euo pipefail

# Set HIGH_NICE_VALUE high enough to counter-balance 1000 priority
# points from job age.
HIGH_NICE_VALUE=1001
LOW_NICE_VALUE=0
PARTITION="$1"
LOGFILE=~/autonice-$PARTITION.log

function get_num_cores {
    cpuinfo=$(sinfo --partition="$PARTITION" --noheader -o "%C")
    basename "$cpuinfo"
}

function my_squeue {
    squeue --partition "$PARTITION" --noheader "$@"
}

function running_jobs_for_user {
    my_squeue --states RUNNING --user "$1" | wc -l
}

function pending_users {
    my_squeue --states PENDING -o "%U" | sort -u | wc -l
}

function set_pending_jobs_nice {
    # Get jobs for the user, separated by newlines.
    # NOTE: According to "man squeue", we should use JOBARRAYID
    # instead of JOBID. But the man page doesn't seem to match the
    # actual behaviour.
    jobs_for_user=$(my_squeue --states PENDING --user "$1" -O JOBID)
    # Convert newlines to spaces.
    jobs_for_user="$(echo $jobs_for_user)"
    # Convert spaces to commas.
    jobs_for_user=${jobs_for_user// /,}
    if [ "$jobs_for_user" = "" ]; then
        echo "I have no pending jobs, so no nice values to update."
    else
        echo "Setting nice value of jobs $jobs_for_user to $2."
        scontrol update "JOBID=$jobs_for_user" "NICE=$2"
    fi
}

function update_jobs {
    USERNAME="$1"
    echo "I am $USERNAME".
    MY_CORES=$(running_jobs_for_user "$USERNAME")
    echo "I am running $MY_CORES tasks."
    echo "Hence, I assume I am using $MY_CORES cores."
    TOTAL_CORES=$(get_num_cores)
    echo "Under normal circumstances, there should be $TOTAL_CORES cores."
    PENDING_USERS=$(pending_users)
    echo "There are $PENDING_USERS users with pending jobs."

    if [ "$PENDING_USERS" = 0 ] ; then
        echo "Nobody is waiting: how lovely!"
    else
        FAIR_SHARE=$(($TOTAL_CORES / $PENDING_USERS))
        echo "My fair share is $FAIR_SHARE cores."
        if [ "$MY_CORES" -gt "$FAIR_SHARE" ]; then
            echo "I am overusing the grid! Let's be nice!"
            set_pending_jobs_nice "$USERNAME" "$HIGH_NICE_VALUE"
        else
            echo "I am not overusing the grid! No need to be nice!"
            set_pending_jobs_nice "$USERNAME" "$LOW_NICE_VALUE"
        fi
    fi
}

function main_loop {
    while true; do
        date
        update_jobs "$USERNAME"
        echo
        SLEEP_DURATION=$((RANDOM % 61 + 30))
        sleep $SLEEP_DURATION
    done
}

USERNAME=$(whoami)

if [ "$1" = "--silent" ]; then
    main_loop "$USERNAME" >> "$LOGFILE" 2>&1
else
    main_loop "$USERNAME" 2>&1 | tee -a "$LOGFILE"
fi
