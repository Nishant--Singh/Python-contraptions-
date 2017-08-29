#!/usr/bin/python
"""
Monitoring port changes inside VPCs, subnets, and public EIPs 
with notification to Slack and PagerDuty

"""

import sys,socket,syslog,ConfigParser,os,time
import cPickle as pickle  # we use this to persist nmap scan reports
import json
import requests
import collections

from libnmap.process import NmapProcess
from libnmap.parser import NmapParser, NmapParserException



try:
    import platform
    import slack
    import slack.chat
    from slacker import Slacker
except:
    print "Slack modules must be installed for Slack notifications to work"

config = ConfigParser.ConfigParser()
config.read(sys.argv[1])
slack.api_token = config.get('notification','slack_key')
API_ACCESS_KEY = config.get('notification','pagerduty_token')

box_name = socket.gethostname()

def notify_slack_new_host(host_list):
    if not host_list:  # do not notify slack ifno new host found`
       return
    slack_msg = ''.join([str(elem) for elem in host_list])
    slack.chat.post_message('#testbot', 'New Host Found:  '+slack_msg+'Found in : '+str(box_name),username='NMAP_new_host')

def notify_slack_forbidden_port(a,b,c,d):   
    slack.chat.post_message('#testbot','Illegal Port found open :'+a+'/'+b+' '+c+' , on => '+d+' Found in :'+str(box_name),username='NMAP_forbidden_port')
    
def notify_slack_changed_port(a,b,c):
    # print "For %s, Port changed from %s to %s" %(key,self.old_port_dict[key],self.new_port_dict[key])
    slack.chat.post_message('#testbot','For '+a+' Port changed from '+b+' to ===>> '+c,username='NMAP_change_port')

    
def notify_pagerduty_forbidden_port(a,b,c,d):      ## Call this when a Forbidden port has been open up 
    headers = {
        'Authorization': 'Token token={0}'.format(API_ACCESS_KEY),
        'Content-type': 'application/json',
    }
    payload = json.dumps({
      "service_key": API_ACCESS_KEY,
      "incident_key": "illegal/port",
      "event_type": "trigger",
      "description": "A Illegle port was found open"+str(a)+"/ "+str(b)+" service "+str(c)+" on "+str(d)+" Found in "+str(box_name),
    })
    print "Sending to Pagerduty",payload
    r = requests.post(
                    'https://events.pagerduty.com/generic/2010-04-15/create_event.json',
                    headers=headers,
                    data=payload,
    )
    print "Done!"

class Report(object):
    """Object for analyzing scan results and and identiying new hosts and ports"""

    def __init__(self,report):
        self.prev_report = None 
        self.report = report
        self.prev_hosts = set()
        self.curr_hosts = set()
       # self.new_port_dict = {}       # Dictionary to store the new ports from curr_host
       # self.old_port_dict = {}       # Dictionary to store the old ports from old_host
        self.results_ports_dict = {}  # Holds the result of changed/newly added ports

    def total_hosts(self):
        """Return total host count in scan"""

        return self.report.hosts_up

    # These two methods use python sets to compare successive hosts from pickles
    def new_hosts(self):
        """Return a list of new hosts added in latest scan"""
        print self.curr_hosts - self.prev_hosts
        return self.curr_hosts - self.prev_hosts

    def lost_hosts(self):
        """Return a list of hosts that disappeared from previous scan"""
        print self.prev_hosts - self.curr_hosts 

    def new_ports(self,host):
        """Return a list of new ports for a specified host"""
        return self.results_ports_dict[host]

    def compare(self,filename):
        """Load the last saved file and compare to scan current report"""
        try:
            f = open(filename)
            self.prev_report = pickle.load(f) # NmapReport

            # sets use add instead of append
            for h in self.prev_report.hosts:
                self.prev_hosts.add(h.address)
            for h in self.report.hosts:
                self.curr_hosts.add(h.address)

            print `self.prev_hosts`
            print `self.curr_hosts`

        except Exception as e:
            print e

    def dump_all_ports(self):
        for h in self.report.hosts:
            print "Host:", h.address
            for p in h.get_open_ports():
                print "\t",p
     
    #################################################################
    def comp_ports(self,filename):
      try:
            f = open(filename)
            self.prev_report = pickle.load(f) # NmapReport
            
            self.old_port_dict = collections.defaultdict(set)
            for s in self.prev_report.hosts:
                 for x in s.get_open_ports():
                      self.old_port_dict[s.address].add(x)

            self.new_port_dict = collections.defaultdict(set)
            for s in self.report.hosts:
                 for x in s.get_open_ports():
                    self.new_port_dict[s.address].add(x)            

            hosts = sorted(set(self.old_port_dict) | set(self.new_port_dict)) 
            
            scan_same = dict()
            scan_new = dict()
            scan_del = dict()

            prev_set = set(self.prev_report.hosts)
            new_set = set(self.report.hosts)
            
            scan_same = prev_set & new_set
            scan_new = new_set - prev_set
            scan_del = prev_set - new_set

            print()
            print('-' * 10, 'Same')    
            for host in scan_same:
                print(host, ':')
                for port in self.new_port_dict[host]:
                     print(':::', port[0], '/', port[1])

            print()
            print('*' * 10, 'Added')
            for host in scan_new:
                print(host, ':')
                for port in self.new_port_dict[host]:
                      print(':::', port[0], '/', port[1])

            print()
            print('=' * 10, 'Deleted')
            for host in scan_del:
                print(host, ':')
                for port in self.old_port_dict[host]:
                       print(':::', port[0], '/', port[1])                                 
                                
      except Exception as l:
             print l 
             raise
     #################################################################
         
     # ********************************************************************* #
    def dump_raw(self):
        """Determine changes between 2 specific scans"""
        nmap_report =  self.report
        syslog.syslog("Starting Nmap {0} at {1}".format(nmap_report.version,nmap_report.started))
        version=nmap_report.version
        state=nmap_report.started
        for host in nmap_report.hosts:
            print 
            if len(host.hostnames):
                tmp_host = host.hostnames.pop()
            else:
                tmp_host = host.address
            print("Nmap scan report for {0} ({1})".format(tmp_host,host.address))
            print("Host is {0}.".format(host.status))
              
            val = config.get('ports', 'scan_range')
            safe_port = range(*map(int, val.split(',')))
            print("  PORT     STATE         SERVICE")

            for serv in host.services:
                if serv.port not in safe_port:
                  print ('Illegal Port open :'+str(serv.port)+'/'+str(serv.protocol)+' '+str(serv.service)+', on host=> '+str(host))
                  
                  notify_slack_forbidden_port(str(serv.port),str(serv.protocol),str(serv.service),str(host))     
                  ######
                  notify_pagerduty_forbidden_port(str(serv.port),str(serv.protocol),str(serv.service),str(host))
                else:
                  pserv = "{0:>5s}/{1:3s}  {2:12s}  {3}".format(str(serv.port),serv.protocol,serv.state,serv.service)
                  if len(serv.banner):
                      pserv += " ({0})".format(serv.banner)
                  print(pserv)
        print(nmap_report.summary)


class Scanner(object):
    """Container for all scan activies"""

    def __init__(self,cp):
        self.config = cp # read in ConfigParser object to get settings
        self.report = None

    def gather_targets(self):
        """Gather list of targets based on configured sources"""
        pass
    
    def run(self,targets="127.0.0.1", options="--open -p1-100 -sV"):
        """start a new nmap scan on localhost with some specific options"""

        syslog.syslog("Scan started")
        parsed = None
        nmproc = NmapProcess(targets, options)
        rc = nmproc.run()

        if rc != 0:
            syslog.syslog("nmap scan failed: {0}".format(nmproc.stderr))
        try:
            parsed = NmapParser.parse(nmproc.stdout)
            self.report = parsed
        except NmapParserException as e:
            syslog.syslog("Exception raised while parsing scan: {0}".format(e.msg))

        syslog.syslog("Scan complete")
        syslog.syslog("Scan duration: "+ str(parsed.elapsed))
        self.report = parsed
        return parsed

    def save(self):
        """Save NmapReport to pickle and rotate file"""

        scan_dir = self.config.get('system','scan_directory')
        # Check if files + directory exist and take action
        if not os.path.exists(scan_dir):
            os.mkdir(scan_dir)
       
        if os.path.exists(scan_dir + '/nmap-report.pkl'):
            print "Renaming previously saved scan results"
            os.rename(scan_dir+'/nmap-report.pkl', scan_dir+'/nmap-report-old.pkl')
        
        print "Saving new scan results"
        f = open(scan_dir+"/nmap-report.pkl","wb")
        pickle.dump(self.report,f)                  #This is pickle dump
        f.close()
        time.sleep(3)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage:\n\tportwatch.py <configfile> [clean]"
        sys.exit(-1)
    else:

        # Read
        config = ConfigParser.ConfigParser()
        config.read(sys.argv[1])

        if len(sys.argv) > 2:
            if sys.argv[2] == "clean":
                for f in ['nmap-report-old.pkl','nmap-report.pkl']:
                    try:
                        os.remove( config.get('system','scan_directory') + "/" + f )
                    except Exception as e:
                        print e

        # Configure Scanner
        s = Scanner(config)

        # Execute Scan and Generate latest report
        net_range = config.get('sources','networks')
        r = s.run(net_range)
        s.save()   # save to pickle


        report = Report(r)

        report.dump_raw()   ## change made for dump to dump_raw
        print "Hosts in scan report",report.total_hosts()
        # Read in last scan
        report.compare(config.get('system','scan_directory') + '/nmap-report-old.pkl' )
        print "New Hosts"
        report.new_hosts()
        
#        slack.api_token = config.get('notification','slack_key')
        
        notify_slack_new_host(report.new_hosts())   #Notifty Slack for any new added host

#        for h in report.result_port_dict.keys():
#           notify_slack(report.new_hosts(h))

       

        print "Lost Hosts"
        report.lost_hosts()

        report.comp_ports(config.get('system','scan_directory') + '/nmap-report-old.pkl')
        report.dump_all_ports()
            
#        print "Changes to slack :Prototype"
#        report.show_changes()
