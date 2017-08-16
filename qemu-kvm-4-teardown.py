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

# Please keep duffy.key besides this script

import os, sys, subprocess
import logging, json, argparse
import urllib2
from logging import DEBUG, INFO, WARN, ERROR, CRITICAL

logger = logging.getLogger('qemu-kvm-4-teardown')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

url_base = "http://admin.ci.centos.org:8080"


def main():
    if os.path.exists('/home/qemu-kvm/duffy.key') and
    os.path.isfile('/home/qemu-kvm/duffy.key'):
            filep = open('/home/qemu-kvm/duffy.key', 'r')
            api = filep.read().strip()
    else:
        logger.error('Either Key does not exist or is not a file')
        sys.exit(1)

    HOST_HOSTNAME = os.environ.get('HOST_HOSTNAME', None)
    HOST_SSID = os.environ.get('HOST_SSID', None)
    ARCHITECTURE = os.environ.get('ARCHITECTURE', 'x86_64')
    VT_GUEST_OS = os.environ.get('VT_GUEST_OS', None)
    INSTALL_URL = os.environ.get('INSTALL_URL', None)

    if not HOST_SSID:
        logger.error('HOST_SSID not set as environment variable')
        sys.exit(1)

    done_nodes_url = "%s/Node/done?key=%s&ssid=%s" % (url_base, api, HOST_SSID)

    das = {}
    try:
        das = urllib2.urlopen(done_nodes_url).read()
    except urllib2.URLError as e:
        logger.error('Error in done_nodes_url=' + str(e.reason))
        sys.exit(1)

    logger.info(das)


if __name__ == '__main__':
    sys.exit(main())
