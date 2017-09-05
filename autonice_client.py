#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import datetime
import errno
import getpass
import os.path
import time

# TODO: Implement check for existence of directory.
# TODO: Implement check that directory has the appropriate
#       rights set. NICE_DIR should be group-readable,
#       NICE_LOG should be group-writable.
# TODO: Add proper daemonization stuff

# ROOT_DIR = "/tmp/infai-autonice"

ROOT_DIR = "/home/helmert/tmp/autonice/test"
SLEEP_DURATION = 1

MIN_NICE = 0
MAX_NICE = 1000000

nice_dir = os.path.join(ROOT_DIR, "nice")
log_dir = os.path.join(ROOT_DIR, "userlog")
username = getpass.getuser()
msg_path = os.path.join(nice_dir, username)
log_path = os.path.join(log_dir, username + ".log")


def open_log():
    global log_file
    log_file = open(log_path, "a")


def log(msg):
    time_stamp = datetime.datetime.now().isoformat()
    print("[%s] %s: %s" % (time_stamp, username, msg), file=log_file)
    log_file.flush()


def warning(msg):
    log("WARNING: %s" % msg)


def error(msg):
    log("ERROR: %s" % msg)


def process_message(msg):
    log("processing message: %r" % msg)
    # TODO: Do something useful.


def read_message():
    try:
        with open(msg_path, "r") as msg_file:
            msg_text = msg_file.read()
    except IOError as e:
        if e.errno == errno.ENOENT:
            return (warning, "message file not found")
        else:
            return (error, "error reading message file: %r" % e)
    if msg_text.endswith("\n"):
        if msg_text.count("\n") >= 2:
            return (error, "message has multiple lines: %r" % msg_text)
        else:
            return parse_message(msg_text.rstrip("\n"))
    else:
        return (warning, "ignoring incomplete message: %r" % msg_text)


def parse_message(msg_text):
    try:
        msg = int(msg_text)
    except ValueError:
        return (error, "malformed message: %r" % msg_text)
    if msg < MIN_NICE or msg > MAX_NICE:
        return (error, "nice value out of range: %d" % msg)
    return (None, msg)


def remove_dupes(seq):
    last = object()
    for elem in seq:
        if elem != last:
            yield elem
            last = elem


def poll_messages():
    while True:
        yield read_message()
        # TODO: Can we do something more clever than waiting for a
        # fixed time? On local file systems, it may be possible to set
        # up a notification mechanism, but not sure if will end up
        # using a local filesystem rather than /infai.
        time.sleep(SLEEP_DURATION)


def poll_new_messages():
    return remove_dupes(poll_messages())


def main_loop():
    for error_func, msg in poll_new_messages():
        if error_func is not None:
            error_func(msg)
        else:
            process_message(msg)


def main():
    # TODO: Do a proper daemonization: detach from shell,
    # change to an appropriate directory, set the umask, etc.
    open_log()
    log("autonice client started")
    main_loop()


if __name__ == "__main__":
    main()
