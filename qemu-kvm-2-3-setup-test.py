#!/usr/bin/python
#
# This script uses the Duffy node management api to get fresh machines to run
# your CI tests on. Once allocated you will be able to ssh into that machine
# as the root user and setup the environ
#
# XXX: You need to add your own api key below, and also set the right cmd= line
#      needed to run the tests
#
# Please note, this is a basic script, there is no error handling and there are
# no real tests for any exceptions. Patches welcome!

#
# 2017 Deepak Verma <dverma@redhat.com>
#

# Please keep duffy.key, automate_setup_test.py besides this script

import os, sys, subprocess
import logging, json, argparse
import urllib2
from logging import DEBUG, INFO, WARN, ERROR, CRITICAL

logger = logging.getLogger('build_python_script')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

url_base = "http://admin.ci.centos.org:8080"


def main():
    HOST_HOSTNAME = os.environ.get('HOST_HOSTNAME', None)
    HOST_SSID = os.environ.get('HOST_SSID', None)
    ARCHITECTURE = os.environ.get('ARCHITECTURE', 'x86_64')
    VT_GUEST_OS = os.environ.get('VT_GUEST_OS', None)
    INSTALL_URL = os.environ.get('INSTALL_URL', None)

    git_url = 'https://github.com/dv3/qemu-kvm-ci-upstream.git'

    if not HOST_HOSTNAME:
        logger.error('HOST_HOSTNAME not set in environment')
        sys.exit(1)

    # run test
    # cmd = "ssh -t -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@%s 'yum -y install git && git clone %s tests && cd tests && chmod +x ./automate_setup_test.py && ./automate_setup_test.py'" % (h, git_url)
    logger.info("SSHing into duffy machine")
    cmd = ("ssh -t -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@"+host+" 'yum -y install git && git clone "+git_url+" && cd qemu-kvm-ci-upstream && chmod +x ./automate_setup_test.py && ./automate_setup_test.py'")
    logger.info(cmd)
    rtn_code = subprocess.call(cmd, shell=True)

    logger.info("Copy job log back from duffy machine")
    cmd = ("scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@" + host + ":/root/avocado/job-results/latest/job.log ./")
    code = subprocess.call(cmd, shell=True)

    logger.info("Copy serial output back from duffy machine")
    cmd = ("scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@" + host + ":/root/avocado/job-results/latest/test-results/1-*/serial* ./")
    code = subprocess.call(cmd, shell=True)

if __name__ == '__main__':
    sys.exit(main())
