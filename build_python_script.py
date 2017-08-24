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
import urllib2, datetime
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
    # This file was generated on your slave.  See https://wiki.centos.org/QaWiki/CI/GettingStarted
    if os.path.exists('/home/qemu-kvm/duffy.key') and os.path.isfile('/home/qemu-kvm/duffy.key'):
            filep = open('/home/qemu-kvm/duffy.key', 'r')
            api = filep.read().strip()
    else:
        logger.error('Either Key does not exist or is not a file')
        sys.exit(1)

    ver = "7"
    count = "1"
    # tiny/small/medium
    flavor = "medium"
    arch = "x86_64"
    if args.arch:
        arch = str(args.arch)

    # git_url="https://example.com/test.git"
    # Duffy Default values: if not specified in the API call
    # flavor = small, ver = 7
    get_nodes_url = "%s/Node/get?key=%s&ver=%s&arch=%s&count=%s&flavor=%s" % (url_base, api, ver, arch, count, flavor)
    # http://admin.ci.centos.org:8080/Node/get?key=XXX&ver=7&arch=x86_64&count=1&flavor=medium

    logger.info('### qemu-kvm-upstream-1-provision ###')
    dat = {}
    try:
        dat = urllib2.urlopen(get_nodes_url).read()
    except urllib2.URLError as e:
        logger.error('Error in get_nodes_url=' + str(e.reason))
        sys.exit(1)

    b = json.loads(dat)
    logger.info('Hosts returned='+str(b))

    #
    # Reply is in the form of JSON with host ids
    # {
    #    "hosts":
    #        "n24.dusty.ci.centos.org"
    #    ],
    #    "ssid": "28c11dd0-b5d7-11e4-b2af-525400ea212d"
    #  }
    #

    for host in b['hosts']:
        # copy automation file in duffy machine
        cmd = ("scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no /home/qemu-kvm/x86_64.cfg /home/qemu-kvm/Fedora-25.ks /home/qemu-kvm/basic_tests.txt /home/qemu-kvm/extended_tests.txt /home/qemu-kvm/automate_setup_test.py root@"+host+":/root/")
        logger.info(cmd)
        rtn_code = subprocess.call(cmd, shell=True)

        # run test
        # cmd = "ssh -t -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@%s 'yum -y install git && git clone %s tests && cd tests && chmod +x ./automate_setup_test.py && ./automate_setup_test.py'" % (h, git_url)
        logger.info("SSHing into duffy machine")
        cmd = ("ssh -t -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@"+host+" 'chmod +x ./automate_setup_test.py && ./automate_setup_test.py'")
        logger.info(cmd)
        rtn_code = subprocess.call(cmd, shell=True)

        log_zip_name = os.environ.get('BUILD_TAG')
        d_date = datetime.datetime.now()
        timestamp = d_date.strftime("%Y-%m-%dT%H-%M-%S")
        log_zip_name = log_zip_name + '_'+timestamp+'.tar.gz'

        logger.info("Zip log folder in duffy machine")
        cmd = ("ssh -t -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@"+host+" 'yum -y install tar && tar -cvzf /root/"+log_zip_name+" /root/avocado/job-results/*'")
        code = subprocess.call(cmd, shell=True)

        logger.info("Copy log zip back to Jenkin slave")
        cmd = ("scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@" + host + ":/root/"+log_zip_name+" /home/qemu-kvm/")
        code = subprocess.call(cmd, shell=True)

    done_nodes_url = "%s/Node/done?key=%s&ssid=%s" % (url_base, api, b['ssid'])

    logger.info('### qemu-kvm-upstream-4-teardown ###')
    das = {}
    try:
        das = urllib2.urlopen(done_nodes_url).read()
    except urllib2.URLError as e:
        logger.error('Error in done_nodes_url=' + str(e.reason))
        sys.exit(1)

    sys.exit(rtn_code)


if __name__ == '__main__':
    sys.exit(main())
