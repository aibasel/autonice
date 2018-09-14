#! /usr/bin/env python

from __future__ import division
from __future__ import print_function

import argparse
import datetime
import getpass
import random
import subprocess
import sys
import time

"""autonice: Periodically set nice values based on current grid usage.
Deprioritize all array tasks, and deprioritize them further if we are
overusing the grid.

Warning: autonice assumes that we only run single-core tasks, otherwise
its calculations are wrong.

Note that autonice never touches non-array jobs. The rationale for this
is that our non-array jobs tend to be high priority and only use one
core, so it is OK to always run them with high priority.
"""

# These values should be set large enough to compensate other aspects
# that go into the job priority calculation, in particular job age and
# the fair-share value of slurm.
NICE_VALUE_FAIR_USE = 1001
NICE_VALUE_OVERUSE = 2002


def run_squeue(partition, args):
    return subprocess.check_output(["squeue", "--partition", partition, "--noheader"] + args)


def get_num_running_jobs_for_user(partition, user):
    jobs = run_squeue(partition, ["--states", "RUNNING", "--user", user])
    return len(jobs.splitlines())


def get_num_pending_users(partition):
    return len(set(run_squeue(partition, ["--states", "PENDING", "-o", "%U"]).splitlines()))


def get_num_cores(partition):
    cmd = ["sinfo", "--partition", partition, "--noheader", "-o", "%C"]
    output = subprocess.check_output(cmd)
    parts = output.split("/")
    try:
        return int(parts[-1])
    except ValueError:
        sys.exit("Error: {cmd} returned unexpected string \"{output}\"".format(**locals()))


def job_contains_single_task(jobarrayid):
    return jobarrayid.endswith("_[1]")


def set_pending_array_jobs_nice(partition, user, nice):
    # Get jobs for the user, separated by newlines.
    # We set the field width to 100 because the default of 20 can lead
    # to truncation for very large array jobs.
    all_jobs_string = run_squeue(
        partition, ["--states", "PENDING", "--user", user, "-O", "jobarrayid:100"])
    all_jobs = [job.strip() for job in all_jobs_string.splitlines()]
    print("My pending jobs:", all_jobs)
    # Only change nice value for array jobs. Single-task jobs should
    # always run as soon as they are eligible.
    array_jobs = [job for job in all_jobs if not job_contains_single_task(job)]
    print("My pending array jobs:", array_jobs)
    if array_jobs:
        array_jobs_string = ",".join(array_jobs)
        print("Setting nice value of jobs {array_jobs_string} to {nice}.".format(**locals()))
        subprocess.check_call(
            ["scontrol", "update", "jobid={}".format(array_jobs_string), "nice={}".format(nice)])
    else:
        print("I have no pending jobs, so no nice values to update.")


def update_jobs(partition, total_cores, user):
    print("I am {user}".format(**locals()))
    my_cores = get_num_running_jobs_for_user(partition, user)
    print("I am running {my_cores} tasks.".format(**locals()))
    print("Hence, I assume I am using {my_cores} cores.".format(**locals()))
    print("Under normal circumstances, there should be {total_cores} cores.".format(**locals()))
    num_pending_users = get_num_pending_users(partition)
    print("There are {num_pending_users} users with pending jobs.".format(**locals()))

    if num_pending_users == 0:
        print("Nobody is waiting: how lovely!")
    else:
        fair_share = total_cores // num_pending_users
        print("My fair share is {fair_share} cores.".format(**locals()))
        if my_cores > fair_share:
            print("I am overusing the grid! Let's be nice!")
            nice = NICE_VALUE_OVERUSE
        else:
            print("I am not overusing the grid! No need to be nice!")
            nice = NICE_VALUE_FAIR_USE
        set_pending_array_jobs_nice(partition, user, nice)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("partition", choices=["infai_1", "infai_2"])
    return parser.parse_args()


def main():
    user = getpass.getuser()
    args = parse_args()
    total_cores = get_num_cores(args.partition)
    while True:
        print(datetime.datetime.now())
        try:
            update_jobs(args.partition, total_cores, user)
        except subprocess.CalledProcessError as err:
            # Log error and continue.
            print("Error: {err}".format(**locals()))
        print()
        time.sleep(random.randint(30, 90))


if __name__ == "__main__":
    main()
