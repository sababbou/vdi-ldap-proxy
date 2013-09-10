vdi-ldap-proxy
==============

This script works as a "Proxy" which remove whitespace after the comma in ldap search request (baseDn).

Client Application ---> vdi-ldap-proxy ---> LDAP Server

Installation procedure
======================
1) Install a fresh new (Debian) server

2) Install python and ldaptor library

  apt-get install python python-ldaptor
  
3) Edit vdi-proxy.py

4) Change the following lines

forward_to = ('samba4.test.dom', 389) # Target LDAP server

filthy_basedn = 'dc=test, dc=dom'     # BaseDN with the whitespace


5) python vdi-ldap-proxy.py

6) Use the proxy IP/DNS on the client application.

Thanks to :
===========
- Ricardo Pascal for his python proxy in less than 100 lines :
  http://voorloopnul.com/blog/a-python-proxy-in-less-than-100-lines-of-code/

- Ldaptor dev team / contributors for the really nice LDAP Request decoding tool
  https://github.com/antong/ldaptor
