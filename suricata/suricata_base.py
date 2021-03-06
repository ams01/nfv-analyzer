#!/usr/bin/python3

# suricata_base.py
# Base class for a Suricata tester.
#
# @author Xiangyu Bu <bu1@purdue.edu>

import logging
import os
import subprocess
import time

from . import test_base


class SuritacaTestBase(test_base.TestBase):

    ETHTOOL_ARGS = ('tso', 'gro', 'lro', 'gso', 'rx', 'tx', 'sg')

    def __init__(self, remote_host, remote_user, local_tmpdir, remote_tmpdir, data_repo):
        super().__init__()
        self.remote_host = remote_host
        self.remote_user = remote_user
        self.local_tmpdir = local_tmpdir
        self.remote_tmpdir = remote_tmpdir
        self.data_repo = data_repo
        self.shell = self.get_remote_shell(remote_host, remote_user)

    def setup_nic(self, nic, is_local=True):
        """ Configure the NIC to use for suricata. """
        for optarg in self.ETHTOOL_ARGS:
            if is_local:
                subprocess.call(['sudo', 'ethtool', '-K', nic, optarg, 'off'])
            else:
                self.simple_call(['sudo', 'ethtool', '-K', nic, optarg, 'off'])
        if not is_local:
            self.simple_call(['sudo', 'ifconfig', nic, 'promisc'])

    def delete_tmpdir(self):
        """ Delete temporary directories on local and remote hosts. """
        logging.info('Deleting local directory "%s".', self.local_tmpdir)
        subprocess.call(['rm', '-rf', self.local_tmpdir])
        logging.info('Deleting remote directory "%s".', self.remote_tmpdir)
        self.simple_call(['rm', '-rf', self.remote_tmpdir])

    def create_tmpdir(self):
        """ Create temporary directories on local and remote hosts. """
        logging.info('Creating local directory "%s".', self.local_tmpdir)
        subprocess.call(['mkdir', '-p', self.local_tmpdir])
        logging.info('Creating remote directory "%s".', self.remote_tmpdir)
        self.simple_call(['mkdir', '-p', self.remote_tmpdir])

    def commit_dir(self):
        """ Send directories to data repository server. """
        logging.info('Committing local tmpdir.')
        self.commit_local_dir(self.local_tmpdir, self.data_repo.repo_user, self.data_repo.repo_host, self.data_repo.repo_dir)
        logging.info('Committing remote tmpdir.')
        self.commit_remote_dir(self.remote_tmpdir, self.data_repo.repo_user, self.data_repo.repo_host, self.data_repo.repo_dir)

    def wait_for_suricata(self, wait_sec=4):
        while True:
            if self.simple_call(['test', '-f', os.path.join(self.remote_tmpdir, 'eve.json')]) != 0:
                logging.info('Waiting for %d seconds for Suricata to stabilize...', wait_sec)
                time.sleep(wait_sec)
            else:
                logging.info('Suricata is ready.')
                return
