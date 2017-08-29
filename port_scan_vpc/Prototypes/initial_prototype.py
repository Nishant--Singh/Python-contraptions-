#!/usr/bin/python
from libnmap.process import NmapProcess
from libnmap.parser import NmapParser, NmapParserException

import slack
import slack.chat
from slacker import Slacker

slack.api_token = ''
slack.chat.post_message('#testbot', 'NMAP Port Sniffer Initialized -Scanning SYD_DEVOPS_VPC- Prototype',username='NMAP_bot')
slack.chat.post_message('#testbot','===================================================================',username='NMAP_bot')
##slack.chat.post_message('#testbot','NMAP Port Sniffer -- PROTOTYPE FAILED' ,username='NMAP_bot')

# start a new nmap scan on localhost with some specific options
def do_scan(targets, options):
    parsed = None
    nmproc = NmapProcess(targets, options)
    rc = nmproc.run()
    if rc != 0:
        print("nmap scan failed: {0}".format(nmproc.stderr))
        slack.chat.post_message('#testbot','nmap scan failed: '+(nmproc.stderr),username='NMAP_bot')   ###
    print(type(nmproc.stdout))

    try:
        parsed = NmapParser.parse(nmproc.stdout)
    except NmapParserException as e:
        print("Exception raised while parsing scan: {0}".format(e.msg))
        slack.chat.post_message('#testbot','Exception raised while parsing scan: '+(e.msg),username='NMAP_bot')  ###
    return parsed


# print scan results from a nmap report
def print_scan(nmap_report):
    print("Starting Nmap {0} at {1}".format(nmap_report.version,nmap_report.started))
    version=nmap_report.version
    state=nmap_report.started
     
    slack.chat.post_message('#testbot','Starting Nmap '+str(version)+' at '+str(state),username='NMAP_bot') ##

    for host in nmap_report.hosts:
        if len(host.hostnames):
            tmp_host = host.hostnames.pop()
        else:
            tmp_host = host.address

        print("Nmap scan report for {0} ({1})".format(tmp_host,host.address))
        slack.chat.post_message('#testbot','Nmap scan report for '+(tmp_host),username='NMAP_bot') ##
        print("Host is {0}.".format(host.status))
        slack.chat.post_message('#testbot','Host is '+(host.status),username='NMAP_bot')
        
        for osmatch in host.os.osmatches: #NmapParser manipulation to detect OS and accuracy of detection.
          os = osmatch.name
          accuracy = osmatch.accuracy
          #print "Operating System Guess: ", os, "- Accuracy Detection", accuracy
          slack.chat.post_message('#testbot','Operating System : '+str(os)+', Accuracy Detection : '+str(accuracy),username='NMAP_bot')
          break

        print("  PORT     STATE         SERVICE")
        slack.chat.post_message('#testbot','PORT     STATE         SERVICE',username='NMAP_bot')

        for serv in host.services:
            pserv = "{0:>5s}/{1:3s}  {2:12s}  {3}".format(str(serv.port),serv.protocol,serv.state,serv.service)
            if len(serv.banner):
                pserv += " ({0})".format(serv.banner)
            print(pserv)
            slack.chat.post_message('#testbot',pserv,username='NMAP_bot')         
 
    print(nmap_report.summary)
    slack.chat.post_message('#testbot',nmap_report.summary,username='NMAP_bot')

if __name__ == "__main__":
    with open('/home/nsingh/Python_sniffer/SNIFF/vpc_hosts.conf') as f:
    	for ip in f.read().splitlines():
            report = do_scan(ip, "--open -A -sV -O --osscan-guess")
            if report:
               print_scan(report)
               slack.chat.post_message('#testbot',report,username='NMAP_bot')
               slack.chat.post_message('#testbot','---------------------------------------------------------',username='NMAP_bot')
            else:
              print("No results returned")
              slack.chat.post_message('#testbot','No results returned',username='NMAP_bot')
