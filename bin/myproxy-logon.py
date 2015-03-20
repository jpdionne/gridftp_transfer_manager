#!/usr/bin/env python

import sys
sys.path = ["/root/"] + sys.path

from argparse import ArgumentParser
import keyring
from subprocess import Popen, PIPE
from getpass import getpass
from gridftp_transfer_manager import myproxy_logon


eb = keyring.backends.file.EncryptedKeyring()
keyring.set_keyring(eb)

parser = ArgumentParser(
    description="Wrapper around myproxy-logon that doesn't requires user input"
)
parser.add_argument('server', type=str)
parser.add_argument('-p', help="Ask for user/password", action="store_true")
args = parser.parse_args()

server = args.server
prev_dn = keyring.get_password(server, "dn")
user = keyring.get_password(server, "user")
password = keyring.get_password(server, "password")

if args.p or not user or not password:
    user = getpass("{0} User:".format(server))
    keyring.set_password(server, "user", user)
    password = getpass("{0}@{1} Password:".format(user, server))
    keyring.set_password(server, "password", password)

logged_in = False
for i in range(5):
    (cert, dn) = myproxy_logon(server, user, password, prev_dn)

    if prev_dn != dn:
        if prev_dn != None:
            print 'The server identify has changed: "{0}" != "{1}"'.format(dn,
                                                                           prev_dn)
        else:
            print 'The server identify is: "{0}"'.format(dn)
        answer = None
        while answer != "y":
            print "continue? (y/n): "
            answer = sys.stdin.readline()[:-1]
            if answer == 'n':
                sys.exit(1)

        keyring.set_password(server, "dn", dn)
        prev_dn = dn

    if cert == None:
        continue

    keyring.set_password(server, "certificate", cert)
    logged_in = True

if logged_in:
    print "Got it"
