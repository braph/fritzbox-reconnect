#!/usr/bin/python

# fritzbox-reconnect - reconnect script for fritzbox
# Copyright (C) 2015 Benjamin Abendroth
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import pexpect
import argparse
import configparser
from time import sleep
from os.path import expanduser

config = {
    'host':          '10.0.0.1',
    'username':      'root',
    'password':      'freetz',
    'ping_host':     '8.8.8.8',
    'ping_timeout':  120
}


epilog = 'Format of configuration (with default values):\n\n[config]'
for i in config.items(): epilog += "\n\t {}={}".format(*i)


argp = argparse.ArgumentParser(description='Fritzbox reconnect script', epilog=epilog,
    formatter_class=argparse.RawDescriptionHelpFormatter)
argp.add_argument('-c', '--config', metavar='FILE', help='Set the location of the config file',
    default=expanduser('~/.config/fritzbox'))


def wait_for_ping(ip, timeout):
    print("Pinging {}".format(ip))
    ping_p = pexpect.spawnu('ping', [ip])

    try:
        ping_p.expect(['[0-9]+ bytes from '], timeout)
    except pexpect.exceptions.TIMEOUT:
        raise Exception("Ping timed out")

    print("Ping successfull")
    ping_p.terminate()


class FritzboxTelnet:
    def __init__(self, ip):
        self.telnet_p = pexpect.spawnu('telnet', [ip])
        self.telnet_p.logfile_read = sys.stdout

    def login(self, user, password):
        choice = self.telnet_p.expect(['[pP]assword:', 'login:'], 2);

        if choice == 0:
            self.telnet_p.sendline(password)
        else:
            self.telnet_p.sendline(user)
            self.telnet_p.expect(['[pP]assword:'], 1)
            self.telnet_p.sendline(password)

        sleep(1)
        self.test_shell()

    def test_shell(self):
        try:
            self.telnet_p.sendline('echo TEST')
            self.telnet_p.expect(['TEST'], 2)
        except pexpect.exceptions.TIMEOUT:
            raise Exception("Test command failed. Invalid login?")

    def reconnect(self):
        self.telnet_p.sendline('dsld -s && dsld')

    def disable_tr064(self):
        self.telnet_p.sendline('ctlmgr_ctl w tr064 settings/enabled 0')

    def disable_tr069(self):
        self.telnet_p.sendline('ctlmgr_ctl w tr069 settings/enabled 0')

    def close(self):
        self.telnet_p.terminate()
    

args = argp.parse_args()
configp = configparser.ConfigParser()

try:
    configp.read(args.config)

    for section in configp.sections():
        if section != 'config':
            raise Exception("Unknown section: {}".format(section))

    for key in configp.options('config'):
        if key not in config:
            raise Exception("Unknown option: {}".format(key))
        elif type(config[key]) is int:
            config[key] = configp.getint('config', key)
        else:
            config[key] = configp.get('config', key)

except Exception as e:
    print("Config Error: {}".format(e))
    sys.exit(2)


try:
    fritz = FritzboxTelnet(config['host'])
    fritz.login(config['username'], config['password'])
    fritz.reconnect()
    sleep(6)
    wait_for_ping(config['ping_host'], config['ping_timeout'])
    fritz.disable_tr064()
    fritz.disable_tr069()
    fritz.close()
except Exception as e:
    print("Error: {}".format(e))
    sys.exit(1)
