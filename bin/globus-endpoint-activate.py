#!/usr/bin/env python

import sys
sys.path = ["/root/"] + sys.path
from IPython import embed

from argparse import ArgumentParser
import keyring
import sys
import os
import tempfile
from subprocess import Popen, PIPE
from getpass import getpass
from globusonline.transfer import api_client
from globusonline.transfer.api_client import x509_proxy

from gridftp_transfer_manager import myproxy_logon


class TmpFile():
    def __enter__(self):
        (self.fd, self.name) = tempfile.mkstemp()
        self.f = os.fdopen(self.fd, 'w')
        return (self.f, self.name)
    def __exit__(self, type, value, traceback):
        self.f.close()
        os.unlink(self.name)


class GlobusAPI(api_client.TransferAPIClient):
    def __init__(self, user, passwd):
        token = api_client.goauth.get_access_token(username=user,
                                                   password=passwd)
        super(self.__class__, self).__init__(user, goauth=token.token)

    def is_endpoint_activated(self, ep):
        status_code, status_message, data = self.endpoint_activation_requirements(ep)
        assert(status_code == 200)
        if data['activated']:
            sys.stderr.write('Endpoint {} is activated and will expire at {}\n'.format(ep, data["expire_time"]))
        return data['activated']

    def activate_endpoint(self, ep):
        status_code, status_message, data = self.endpoint_activation_requirements(ep)
        assert(status_code == 200)

        if data['oauth_server']:
            sys.stderr.write('WARNING: this is an oauth server, we are assuming the myproxy is at the same address\n')
            myproxy=data['oauth_server']
        else:
            myproxy=data['hostname']

        user = keyring.get_password(myproxy, "user")
        password = keyring.get_password(myproxy, "password")
        dn = keyring.get_password(myproxy, "dn")
#        cert = keyring.get_password(myproxy, "certificate")
        cert = None
        if not (user and password and dn):
            sys.stderr.write('Cannot get myproxy certificate.  Call "myproxy_logon.py {} to setup user and passwords"\n'.format(myproxy))
        if cert == None:
            sys.stderr.write('Credentials not found for {}.\nInvoking myproxy_logon...\n'.format(myproxy))
            (cert, dn) = myproxy_logon(myproxy, user, password, dn)
            if cert == None:
                sys.stderr.write('Cannot get myproxy certificate.  Try "myproxy_logon.py {}"\n'.format(myproxy))
                return

        with TmpFile() as t:
            (f, cert_path) = t
            f.write(cert)
            f.close()

            public_key = data.get_requirement_value("delegate_proxy", "public_key")
            proxy = x509_proxy.create_proxy_from_file(cert_path, public_key)

        data.set_requirement_value("delegate_proxy", "proxy_chain", proxy)

        status_code, status_message, data = self.endpoint_activate(ep, data)
        #print status_code, status_message, data
        assert(status_code == 200)

        sys.stderr.write('Endpoint {} is activated and will expire at {}\n'.format(ep, data["expire_time"]))

def main():
    eb = keyring.backends.file.EncryptedKeyring()
    keyring.set_keyring(eb)

    parser = ArgumentParser(
        description="Activate a globus endpoint and store necessary credentials for automation."
    )
    parser.add_argument('endpoint', metavar='user#endpoint', type=str, nargs='+')
    parser.add_argument('-g', nargs=1, help="globus user name", required=True)
    parser.add_argument('-p', help="Ask for password", action="store_true")
    args = parser.parse_args()

    globus_user = args.g[0]
    globus_passwd = keyring.get_password("globus", "password")
    if args.p:
        globus_passwd = getpass("{0}@globus Password:".format(globus_user))
        keyring.set_password("globus", "password", globus_passwd)

    if not globus_passwd:
        sys.stderr.write("No password set, use -p to set it\n")
        sys.exit(1)

    api = GlobusAPI(globus_user, globus_passwd)
    for ep in args.endpoint:
        if not api.is_endpoint_activated(ep):
            try:
                api.activate_endpoint(ep)
            except Exception as e:
                sys.stderr.write("Cannot activate {}\n".format(ep))
                sys.stderr.write(str(e) + '\n')

if __name__ == "__main__":
    main()
