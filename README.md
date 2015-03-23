

Globus automates transfers between gridftp endpoints.
Endpoint activation requires the user to input credentials which have an
expiration time determined by the myproxy adminstrator.

Transfers can be automated during the period of credentials validity but
requires human intervention for the renewal.

This tool uses the Globus API and the python keyring to store on the user side
the credentials and continuously reactivates the endpoints.

It is particularly useful for periodic transfers such as backups.

LIMITATIONS

Currently the tool only support endpoints that are registered to Globus as
myproxy-oauth but which has a myproxy service publicly exposed.

TODO
- Act a an oauth user to fully support myproxy-oauth activation
- Support myproxy activation through the globus API

Usage:

Set the globus user and password into the keyring and get the myproxy addresses of the two endpoints:

```
# globus-endpoint-agent.py -p -g $GLOBUSUSER $USER1#$ENDPOINT1 $USER2#$ENDPOINT2
xxx@globus Password:
Please set a password for your new keyring:
Please confirm the password:
WARNING: this is an oauth server, we are assuming the myproxy is at the same address
Cannot get myproxy certificate.  Call "myproxy-logon.py myproxy.endpoint1.example.com to setup user and passwords"
Credentials not found for myproxy.endpoint1.example.com
Invoking myproxy-logon...
Cannot activate $USER1#$ENDPOINT1
WARNING: this is an oauth server, we are assuming the myproxy is at the same address
Cannot get myproxy certificate.  Call "myproxy-logon.py myproxy.endpoint2.example.com to setup user and passwords"
Credentials not found for myproxy.endpoint2.example.com
Invoking myproxy-logon...
Cannot activate $USER2#$ENDPOINT2
```

Set the first endpoint user name and password into the keyring

```
# myproxy-logon.py myproxy.endpoint1.example.com
myproxy.endpoint1.example.com User:
Please enter password for encrypted keyring:
xxx@myproxy.endpoint1.example.com Password:
Getting trusts roots
The server identify is: "/C=US/O=Globus Consortium/OU=Globus Connect Service/CN=4a36b7f4-a55c-11e3-b3e4-22000a971261"
continue? (y/n):
y
Got it
```

Set the second endpoint user name and password into the keyring

```
# myproxy-logon.py myproxy.endpoint2.example.com
Please enter password for encrypted keyring:
The server identify is: "/C=US/O=Globus Consortium/OU=Globus Connect Service/CN=d9148064-d487-11e3-b48f-22000a971261"
continue? (y/n):
y
Got it
```

You can now launch the agent:

```
# globus-endpoint-agent.py -g $GLOBUSUSER $USER1#$ENDPOINT1 $USER2#$ENDPOINT2
Please enter password for encrypted keyring:
WARNING: this is an oauth server, we are assuming the myproxy is at the same address
Credentials not found for myproxy.endpoint1.example.com
Invoking myproxy_logon...
Endpoint $USER1#$ENDPOINT1 is activated and will expire at 2015-03-20 02:50:00+00:00
WARNING: this is an oauth server, we are assuming the myproxy is at the same address
Credentials not found for myproxy.endpoint2.example.com
Invoking myproxy_logon...
Endpoint $USER2#$ENDPOINT2 is activated and will expire at 2015-03-20 02:50:01+00:00
Sleeping...
```

