#! /usr/bin/env python

from __future__ import division
from __future__ import print_function

import argparse
import collections
import datetime
import getpass
import random
import subprocess
import sys
import time

"""autonice: Periodically set nice values based on current grid usage.
Deprioritize all array tasks, and deprioritize them further if we are
overusing the grid.

Note that autonice never touches non-array jobs. The rationale for this
is that our non-array jobs tend to be high priority and only use one
core, so it is OK to always run them with high priority.
"""

# These values should be set large enough to compensate other aspects
# that go into the job priority calculation, in particular job age and
# the fair-share value of slurm.
NICE_VALUE_FAIR_USE = 1001
NICE_VALUE_OVERUSE = 2002


Usage = collections.namedtuple('Usage', ['cores', 'tasks'])


def log(*args, **kwargs):
    print(*args, file=log_file, **kwargs)


def check_call(*args, **kwargs):
    log_file.flush()
    return subprocess.check_call(*args, **kwargs)


def check_output(*args, **kwargs):
    log_file.flush()
    return subprocess.check_output(*args, **kwargs)


def run_squeue(partition, args):
    return check_output(["squeue", "--partition", partition, "--noheader"] + args)


def get_usage_for_user(partition, user):
    # %C: Number of cores requested by the job or allocated to it if already running.
    lines = run_squeue(partition, ["--states", "RUNNING", "--user", user, "-o", "%C"]).splitlines()
    return Usage(cores=sum(int(cores) for cores in lines), tasks=len(lines))


def get_num_pending_users(partition):
    return len(set(run_squeue(partition, ["--states", "PENDING", "-o", "%U"]).splitlines()))


def get_num_cores(partition):
    cmd = ["sinfo", "--partition", partition, "--noheader", "-o", "%C"]
    output = check_output(cmd)
    parts = output.split("/")
    try:
        return int(parts[-1])
    except ValueError:
        msg = "Fatal error: {cmd} returned unexpected string \"{output}\"".format(**locals())
        log(msg)
        sys.exit(msg)


def job_contains_single_task(jobarrayid):
    return jobarrayid.endswith("_[1]") or jobarrayid.endswith("_[N/A]")


def set_pending_array_jobs_nice(partition, user, nice):
    # Get jobs for the user, separated by newlines.
    # %F: Array job ID. For non-array jobs, this is the job ID.
    # %K: Job array index. For non-array jobs, this is "N/A". By default,
    #     the field size is limited to 64 bytes.
    all_jobs_string = run_squeue(
        partition, ["--states", "PENDING", "--user", user, "-o", "%F_[%K]"])
    all_jobs = [job.strip() for job in all_jobs_string.splitlines()]
    log("My pending jobs:", all_jobs)
    # Only change nice value for array jobs. Single-task jobs should
    # always run as soon as they are eligible.
    array_jobs = [job for job in all_jobs if not job_contains_single_task(job)]
    log("My pending array jobs:", array_jobs)
    if array_jobs:
        array_jobs_string = ",".join(array_jobs)
        log("Setting nice value of jobs {array_jobs_string} to {nice}.".format(**locals()))
        check_call(
            ["scontrol", "update", "jobid={}".format(array_jobs_string), "nice={}".format(nice)])
    else:
        log("I have no pending array jobs, so no nice values to update.")


def update_jobs(partition, total_cores, user):
    log("I am {user}".format(**locals()))
    my_usage = get_usage_for_user(partition, user)
    log("I am running {0.tasks} tasks on {0.cores} cores.".format(my_usage))
    log("Under normal circumstances, there should be {total_cores} cores.".format(**locals()))
    num_pending_users = get_num_pending_users(partition)
    log("There are {num_pending_users} users with pending jobs.".format(**locals()))

    if num_pending_users == 0:
        log("Nobody is waiting: how lovely!")
    else:
        fair_share = total_cores // num_pending_users
        log("My fair share is {fair_share} cores.".format(**locals()))
        if my_usage.cores > fair_share:
            log("I am overusing the grid! Let's be nice!")
            nice = NICE_VALUE_OVERUSE
        else:
            log("I am not overusing the grid! No need to be nice!")
            nice = NICE_VALUE_FAIR_USE
        set_pending_array_jobs_nice(partition, user, nice)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("partition", choices=["infai_1", "infai_2"])
    parser.add_argument("--log-file", type=argparse.FileType("a"),
                        default=sys.stdout)
    return parser.parse_args()


def main():
    user = getpass.getuser()
    args = parse_args()
    global log_file
    log_file = args.log_file
    total_cores = get_num_cores(args.partition)
    while True:
        log(datetime.datetime.now())
        try:
            update_jobs(args.partition, total_cores, user)
        except subprocess.CalledProcessError as err:
            # Log error and continue.
            log("Error: {err}".format(**locals()))
        log()
        log_file.flush()
        time.sleep(random.randint(30, 90))


if __name__ == "__main__":
    main()
