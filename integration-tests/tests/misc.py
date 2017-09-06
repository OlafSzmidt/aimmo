import signal
import requests

import os
import subprocess
import sys

import traceback
import logging
import psutil
import time
import sys
import socket

FNULL = open(os.devnull, 'w')

logging.basicConfig()
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def run_command_async(args, cwd=".", verbose=False):
    if verbose:
        p = subprocess.Popen(args, cwd=cwd)
    else:
        p = subprocess.Popen(args, cwd=cwd, stdout=FNULL, stderr=subprocess.STDOUT)
    return p


def process_tree(pid):
    parent = psutil.Process(pid)
    to_kill = [pid]
    for child in parent.children(recursive=True):
        to_kill = to_kill + process_tree(child.pid)
    return to_kill


def kill_process_tree(pid):
    try:
        LOGGER.info("Current process %s" % str(os.getpid()))
        LOGGER.info("Process tree...")
        to_kill = process_tree(pid)
        LOGGER.info("Killing processes... %s" % str(to_kill))
        for pid in to_kill:
            os.kill(pid, signal.SIGKILL)
        LOGGER.info("Waiting for processes to terminate...")
        for pid in to_kill:
            os.system("wait " + str(pid))
        LOGGER.info("Process tree killed successfully...")
    except Exception as e:
        LOGGER.warn("An exception occured while killing the process tree...")
        logging.error(traceback.format_exc())
