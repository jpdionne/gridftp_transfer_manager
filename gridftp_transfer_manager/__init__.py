import sys
from subprocess import Popen, PIPE
import os
import time
import fcntl

def myproxy_get_trustroots(env):
    sys.stderr.write("Getting trusts roots\n")
    p = Popen(["myproxy-get-trustroots"],
              stdin=PIPE, stdout=PIPE, stderr=PIPE, env=env)
    p.stdout.readlines()
    p.stderr.readlines()

class NoTrustRoot(Exception):
    pass

def myproxy_logon(server, user, password, dn=None):
    env = {
        "MYPROXY_SERVER": server
    }
    if dn:
        env["MYPROXY_SERVER_DN"] = dn

    for i in range(2):
        try:
            return _myproxy_logon(server, user, password, dn, env)
        except NoTrustRoot:
            myproxy_get_trustroots(env)

def _myproxy_logon(server, user, password, dn, env):
    p = Popen(["myproxy-logon", "-l", user, "-S", "-o", "-"],
              stdin=PIPE, stdout=PIPE, stderr=PIPE, env=env)

    (stdout, stderr) = p.communicate(password + '\n')
    stdout = stdout.split('\n')
    stderr = stderr.split('\n')

    if len(stdout) > 2 and \
            stdout[0] == '-----BEGIN CERTIFICATE-----' and \
            stdout[-2] == '-----END CERTIFICATE-----':
        return ("\n".join(stdout), dn)

    for l in stderr:
        if l == 'error getting trusted certificates directory':
            raise NoTrustRoot()
        parts = l.split("=")
        if parts[0] == "MYPROXY_SERVER_DN":
            val = "=".join(parts[1:])[1:-1]
            return (None, val)

    sys.stderr.write("\n".join(stdout))
    sys.stderr.write("\n".join(stderr))
    assert(False)
