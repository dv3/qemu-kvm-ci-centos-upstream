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
    parser = argparse.ArgumentParser(prog='build_python_script',
                                     description='centos ci test automation')
    parser.add_argument('--a', metavar='architecture',
                        help='enter architecture: x86_64/aarch64/ppc64le',
                        action='store', dest='arch')
    args = parser.parse_args()
    # if args.arch:
    #    arch = str(args.arch)

    # This file was generated on your slave.
    # See https://wiki.centos.org/QaWiki/CI/GettingStarted
    if os.path.exists('/home/qemu-kvm/duffy.key') and
    os.path.isfile('/home/qemu-kvm/duffy.key'):
            filep = open('/home/qemu-kvm/duffy.key', 'r')
            api = filep.read().strip()
    else:
        logger.error('Either Key does not exist or is not a file')
        sys.exit(1)

    ver = "7"
    count = "1"
    # tiny/small/medium
    flavor = "medium"
    # default is x86_64
    GUEST_ARCHITECTURE = os.environ.get('GUEST_ARCHITECTURE', 'x86_64')

    '''
    if ARCHITECTURE == 'x86_64':
        VT_GUEST_OS = 'Linux.CentOS.7.0.x86_64.i440fx'
        INSTALL_URL = 'http://mirrors.seas.harvard.edu/centos/7/os/x86_64/'

    '''
    if ARCHITECTURE == 'x86_64':
        VT_GUEST_OS = 'Linux.Fedora.25.x86_64.i440fx'
        INSTALL_URL = 'https://mirror.hmc.edu/fedora/linux/releases/25/Everything/x86_64/os/'
    elif arch == 'ppc64le':
        VT_GUEST_OS = 'Linux.RHEL.7.3.ppc64.pseries'
        INSTALL_URL = 'http://download.devel.redhat.com/released/RHEL-7/7.3/Server/ppc64/os/'
    elif arch == 'aarch64':
        VT_GUEST_OS = 'RHEL.7.devel.aarch64'
        INSTALL_URL = 'http://download.devel.redhat.com/released/RHEL-7/7.3/Server/aarch64/os/'

    # Duffy Default values: if not specified in the API call
    # flavor = small, ver = 7
    get_nodes_url = ("%s/Node/get?key=%s&ver=%s&arch=%s&count=%s&flavor=%s" %
                     (url_base, api, ver, GUEST_ARCHITECTURE, count, flavor))
    # http://admin.ci.centos.org:8080/Node/get?key=XXX&ver=7&arch=x86_64&count=1&flavor=medium
    dat = {}
    try:
        dat = urllib2.urlopen(get_nodes_url).read()
    except urllib2.URLError as e:
        logger.error('Error in get_nodes_url=' + str(e.reason))
        sys.exit(1)

    #
    # Reply is in the form of JSON with host ids
    # {
    #    "hosts":
    #        "n24.dusty.ci.centos.org"
    #    ],
    #    "ssid": "28c11dd0-b5d7-11e4-b2af-525400ea212d"
    #  }
    #

    b = json.loads(dat)
    logger.info('Duffy returned='+str(b))
    for host in b['hosts']:
        os.environ['HOST_HOSTNAME'] = str(host)
        os.environ['HOST_SSID'] = str(b['ssid'])
        os.environ['ARCHITECTURE'] = str(ARCHITECTURE)
        os.environ['VT_GUEST_OS'] = str(VT_GUEST_OS)
        os.environ['INSTALL_URL'] = str(INSTALL_URL)

if __name__ == '__main__':
    sys.exit(main())
