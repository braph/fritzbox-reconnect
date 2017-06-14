#!/bin/bash

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


if ! source ~/.config/fritzbox; then
    cat << EOF
Please place the config file in ~/.config/fritzbox
The configuration file will be sourced.

Format:
FRITZBOX_USER=""
FRITZBOX_PASS=""
FRITZBOX_IP=""

FRITZBOX_USER is OPTIONAL!
EOF
   exit 1
fi

if ! ping -c1 -w1 "$FRITZBOX_IP" &>/dev/null; then
    echo "Fritzbox is not reachable"
    exit 1
fi

reconnect()
{
	echo "dsld -s && dsld";
	sleep 10;

	while ! ping -c1 -w1 8.8.8.8 &>/dev/null; do
		sleep 1;
	done
}

disable_tr069()
{
   echo "ctlmgr_ctl w tr064 settings/enabled 0";
   sleep 1;

   echo "ctlmgr_ctl w tr069 settings/enabled 0";
   sleep 1;
}

fb_login()
{
    if [[ -n "$FRITZBOX_USER" ]] ; then
        echo "$FRITZBOX_USER"
        sleep 1
    fi

	echo "$FRITZBOX_PASS";
   sleep 1;
}

(
	sleep 1;

   fb_login;
   reconnect;
   disable_tr069;

	echo "exit";
) | telnet "$FRITZBOX_IP"
