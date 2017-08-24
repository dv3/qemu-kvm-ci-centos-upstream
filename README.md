# centos-ci-scripts
Some scripts folks might find useful when working with the https://ci.centos.org/ infra

These scripts use the Duffy node management api to get a new machine to run your CI tests on.

Once allocated, ssh into the machine, git clone your test repo and begin testing.

After the tests are over, the whole log folder of jenkins is copied back to slave-ci
as a tar.gz file to analyze errors.

Current Jenkin builds can be viewed at
https://ci.centos.org/view/qemu-kvm/job/qemu-kvm-provision-avocado/

- build_python_script.py
This is the first script which has to be started. It contains the 'provisioning phase'. A machine is requested
from Duffy and than it transfers the rest of the files to it and SSHs into it and runs the second python script.

- automate_setup_test.py
This is the second script which downloads/install everything (qemu/avocado/dependencies) and once installation
over it starts:  vt-bootstrap -> unattended_install.url -> basic_tests -> extended_tests

- extended_tests.txt/basic_test.txt
These files contain the tests with the extra parameters (to make them pass ).

# Things to work on
- Not all extended tests are passing.
- Write trigger for it to run periodically by itself. 
- Extended test run individually

e.g find a command which reads the extra parameters in certain extended tests correctly

io-github-autotest-qemu.timedrift.with_pvclock.shared_ntp_date.date.with_load.default_load --vt-extra-params 'time_command=ntpdate -d -q 0.pool.ntp.org'
The following way of expanding test list is not working for ntp date test
avocado run $(cat extended_tests.txt) --vt-guest-os
