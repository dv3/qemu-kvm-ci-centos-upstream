#!/usr/bin/python
#
# 2017 Deepak Verma <dverma@redhat.com>
#
import sys, subprocess, logging, json, os
from logging import DEBUG, INFO, WARN, ERROR, CRITICAL

ARCHITECTURE = 'x86_64'

logger = logging.getLogger('automate_setup_test')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def byte_to_string(thestring):
    # python 2 has str and unicode whose parent class is basestring
    # python 3 only has str and bytes whose parent class is object
    try:
        basestring
        return thestring
    except NameError:
        return thestring.decode('utf-8')


def call_subprocess(cmd):
    try:
        child = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, shell=True)
        out, err = child.communicate()
        # python2/3 compatible
        if err:
            err = byte_to_string(err)
        if out:
            out = byte_to_string(out)
        exit_code = child.returncode

        if (int(exit_code) != 0):
            logger.error('Error: exit code: '+str(exit_code))
            logger.error(out)
            if err:
                logger.error(err)
            sys.exit(int(exit_code))
        else:
            logger.info(out)
            return exit_code, out
    except Exception as e:
        logger.error('Error in running subprocess:' + str(cmd))
        logger.error(e)
        sys.exit(1)


def main():
    cmd = ('uname -m')
    code, output = call_subprocess(cmd)
    if (int(code) != 0):
        logger.error('Error in retrieving system architecture: ' + str(cmd))
        logger.error('Exiting...')
        sys.exit(1)
    else:
        output = output.strip()
        global ARCHITECTURE
        ARCHITECTURE = str(output)
        logger.info('Architecture found:'+str(ARCHITECTURE))

    # http://mirror.centos.org/centos-7/7/os/x86_64/
    # http://mirrors.seas.harvard.edu/centos/7/os/x86_64/

    # vt_guest_os for arm and P8 are fake
    if ARCHITECTURE == 'x86_64':
        VT_GUEST_OS = 'Linux.CentOS.7.0.x86_64.i440fx'
        INSTALL_URL = 'http://mirror.centos.org/centos-7/7/os/x86_64/'
    elif arch == 'ppc64le':
        VT_GUEST_OS = 'Linux.CentOS.7.0.ppc64.pseries'
        INSTALL_URL = 'http://mirror.centos.org/altarch/7/os/ppc64le/'
    elif arch == 'aarch64':
        VT_GUEST_OS = 'Linux.CentOS.7.0.aarch64.pseries'
        INSTALL_URL = 'http://mirror.centos.org/altarch/7/os/aarch64/'

    '''
    # if we want to test Fedora-25
    if ARCHITECTURE == 'x86_64':
        VT_GUEST_OS = 'Linux.Fedora.25.x86_64.i440fx'
        INSTALL_URL = 'https://mirror.hmc.edu/fedora/linux/releases/25/Everything/x86_64/os/'
    '''
    '''
    # if we want to test RHEL 7.4
    # Please remember to add 'sg3_utils hdparm net-tools' in RHEL-7-devel.ks
    if ARCHITECTURE == 'x86_64':
        VT_GUEST_OS = 'Linux.RHEL.7.devel.x86_64.i440fx'
        INSTALL_URL = 'http://download.devel.redhat.com/released/RHEL-7/7.4/Server/x86_64/os/'
    '''

    logger.info('### qemu-kvm-upstream-2-environment ###')

    # need a bridge on your system
    # by default, the one created by libvirtd is used (virbr0)
    # so it's usually just a matter of having libvirtd running
    # systemctl status/start libvirtd.service

    cmd_install_qemu_dependency = ("yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm && "
                                   "yum -y install wget curl python-pip PyYAML tcpdump python-requests libvirt-python python-sphinx libvirt-devel gstreamer-python "
                                   "gdb gdb-gdbserver python-imaging bridge-utils git python-devel cryptsetup gcc gcc-c++ "
                                   "libvirt* p7zip python2-simplejson policycoreutils-python attr genisoimage mkisofs glibc-devel glib2-devel "
                                   "sg3_utils hdparm net-tools automake autoconf pkgconfig make SDL-devel libtool texinfo zlib zlib-devel openssl-devel && "
                                   "systemctl start libvirtd")
    logger.info('Installing Qemu & prerequisites:\n'+str(cmd_install_qemu_dependency))
    call_subprocess(cmd_install_qemu_dependency)

    cmd_build_qemu = ("git clone git://git.qemu-project.org/qemu.git && cd qemu && git submodule init && git submodule update --recursive && ./configure && make")
    logger.info('Building qemu from source:\n'+str(cmd_build_qemu))
    call_subprocess(cmd_build_qemu)

    cmd_install_avocado = ("curl https://repos-avocadoproject.rhcloud.com/static/avocado-el.repo -o /etc/yum.repos.d/avocado.repo && "
                           "yum -y install python-stevedore && "
                           "yum -y --disablerepo=epel install python-avocado-51.0 && "
                           "yum -y install avocado-plugins-vt-51.0 && "
                           "pip install stevedore --upgrade")
    logger.info('Installing Avocado and Avocado-vt 51.0:\n'+str(cmd_install_avocado))
    call_subprocess(cmd_install_avocado)

    cmd_bootstrap_avocado = ("avocado vt-bootstrap --yes-to-all")
    logger.info('Running avocado bootstrap:\n'+str(cmd_bootstrap_avocado))
    call_subprocess(cmd_bootstrap_avocado)

    '''
    # Needed if we are using a new custom Kickstart file e.g. for which PR hasn't been merged.
    logger.info('Replacing kickstart file')
    cmd_replace_kickstart = ("cp /root/*.ks /usr/share/avocado-plugins-vt/shared/unattended/ && ls /usr/share/avocado-plugins-vt/shared/unattended/")
    call_subprocess(cmd_replace_kickstart)
    '''

    '''
    # Needed if we are using a new custom configuration file e.g. for which PR hasn't been merged.
    logger.info('Replacing cfg file')
    cmd_replace_cfg = ("cp /root/*.cfg /usr/share/avocado-plugins-vt/shared/cfg/guest-os/Linux/CentOS/7.0/x86_64.cfg")
    logger.info('Replacing cfg file:\n'+ str(cmd_replace_cfg))
    call_subprocess(cmd_replace_kickstart)
    '''

    # avocado run io-github-autotest-qemu.unattended_install.cdrom.extra_cdrom_ks.default_install.aio_native
    # cdrom_cd1 = http://mirror.centos.org/centos/7/os/x86_64/images/boot.iso
    # avocado run io-github-autotest-qemu.unattended_install.url.extra_cdrom_ks.default_install.aio_native
    # url = http://mirrors.seas.harvard.edu/centos/7/os/x86_64/'

    # To view inside machine, pipe output to serial file
    # --vt-extra-params vga=none
    # then read file from another terminal
    # tail -f /root/avocado/job-results/latest/test-results/1-*/serial*

    # cmd_avocado_boot_test = ("avocado run boot")
    # logger.info('Run Avocado boot test:' + cmd_avocado_boot_test)
    # call_subprocess(cmd_avocado_boot_test)

    cmd_unattended_url_test = ("avocado run io-github-autotest-qemu.unattended_install.url.extra_cdrom_ks.default_install.aio_native "
                              "--vt-guest-os " + VT_GUEST_OS + " --vt-extra-params 'url = " + INSTALL_URL + "' 'vga=none' 'mem = 4096'")
    logger.info('Run io_unattended_install.url.extra_cdrom Avocado test:\n' + cmd_unattended_url_test)
    call_subprocess(cmd_unattended_url_test)

    #  wget http://linux.cc.lehigh.edu/centos/7/isos/x86_64/CentOS-7-x86_64-Minimal-1611.iso -P /var/lib/avocado/data/avocado-vt/isos/linux/ &&
    # cdrom_cd1 = isos/linux/CentOS-7-x86_64-Minimal-1611.iso
    '''
    # Needed if we want to run the unattended cdrom test (pass an ISO link) and not url test
    cmd_unattended_cdrom_test = ("mkdir -p /var/lib/avocado/data/avocado-vt/isos/linux/ && wget http://archive.kernel.org/centos-vault/7.1.1503/isos/x86_64/CentOS-7-x86_64-Minimal-1503-01.iso -P /var/lib/avocado/data/avocado-vt/isos/linux/ && "
                                "avocado run io-github-autotest-qemu.unattended_install.cdrom.extra_cdrom_ks.default_install.aio_native "
                              "--vt-guest-os " + VT_GUEST_OS + " --vt-extra-params 'cdrom_cd1 = isos/linux/CentOS-7-x86_64-Minimal-1503-01.iso' 'vga=none' 'mem = 4096'")
    logger.info('Run io_unattended_install.url.extra_cdrom Avocado test:\n' + cmd_unattended_cdrom_test)
    call_subprocess(cmd_unattended_cdrom_test)
    '''

    logger.info('### qemu-kvm-upstream-3-runtest ###')
    cmd_avocado_basic_test = ('avocado run $(cat basic_tests.txt) --vt-guest-os ' + VT_GUEST_OS)
    logger.info('Run Avocado basic tests:\n' + str(cmd_avocado_basic_test))
    call_subprocess(cmd_avocado_basic_test)

    if os.path.exists('/root/extended_tests.txt') and os.path.isfile('/root/extended_tests.txt'):
        with open('/root/extended_tests.txt') as f:
            test_list = f.read().splitlines()
    else:
        logger.error('Either extended_tests.txt does not exist or is not a file')
        sys.exit(1)

    for atest in test_list:
        cmd_avocado_extended_test = ("avocado run " + atest + " --vt-guest-os " + VT_GUEST_OS)
        logger.info('Run Avocado extended tests:\n'+str(cmd_avocado_extended_test))
        # call_subprocess(cmd_avocado_extended_test)
        rtn_code = subprocess.call(cmd_avocado_extended_test, shell=True)

    cmd_grep_error = ("grep 'ERROR| ERROR\|ERROR| FAIL' /root/avocado/job-results/job*/job.log")
    logger.info('Grep error from all job.log files:\n' + str(cmd_grep_error))
    call_subprocess(cmd_grep_error)

if __name__ == '__main__':
    sys.exit(main())
