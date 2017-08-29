#!/usr/bin/python
from libnmap.process import NmapProcess
from libnmap.parser import NmapParser, NmapParserException
import socket
import platform

import slack
import slack.chat
from slacker import Slacker
slack.api_token = ''


# start a new nmap scan on localhost with some specific options
def do_scan(targets, options):
    parsed = None
    nmproc = NmapProcess(targets, options)
    rc = nmproc.run()
    if rc != 0:
        print("nmap scan failed: {0}".format(nmproc.stderr))
#    print(type(nmproc.stdout))

    try:
        parsed = NmapParser.parse(nmproc.stdout)
    except NmapParserException as e:
        print("Exception raised while parsing scan: {0}".format(e.msg))
    return parsed


# print scan results from a nmap report
def print_scan(nmap_report):
    print("Starting Nmap {0} at {1}".format(nmap_report.version,nmap_report.started))
    version=nmap_report.version
    state=nmap_report.started
    for host in nmap_report.hosts:
        if len(host.hostnames):
            tmp_host = host.hostnames.pop()
        else:
            tmp_host = host.address
        print("Nmap scan report for {0} ({1})".format(tmp_host,host.address))
        print("Host is {0}.".format(host.status))

        safe_port = range(1,10000)
        print("  PORT     STATE         SERVICE")
        hostname=socket.gethostname()
        os_platform=platform.system()
        for serv in host.services:

            if serv.port not in safe_port:
              print "Error!!! Illegal Port open :",str(serv.port),str(serv.protocol),str(serv.service)
              slack.chat.post_message('#testbot','Illegal Port open :'+str(serv.port)+'/'+str(serv.protocol)+' '+str(serv.service)+', on host=> '+hostname+' running=> '+os_platform,username='NMAP_bot')
            else:
              pserv = "{0:>5s}/{1:3s}  {2:12s}  {3}".format(str(serv.port),serv.protocol,serv.state,serv.service)
              if len(serv.banner):
                  pserv += " ({0})".format(serv.banner)
              print(pserv)

    print(nmap_report.summary)
if __name__ == "__main__":
       report = do_scan("127.0.0.1", "--open -A -sV")
       if report:
         print_scan(report)
       else:
         print("No results returned")

