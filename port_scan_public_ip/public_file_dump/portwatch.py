#!/usr/bin/python
"""
Monitoring port changes inside VPCs, subnets, and public EIPs 
with notification to Slack and PagerDuty

"""

import sys,socket,syslog,ConfigParser,os,time
import cPickle as pickle  # we use this to persist nmap scan reports
import json
import requests
import boto3
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

slack_channel = config.get('notification','slack_channel_name')

box_name = socket.gethostname()

def notify_slack_new_host(host_list):
    if not host_list:  # do not notify slack ifno new host found`
       return
    slack_msg = ' , '.join([str(elem) for elem in host_list])
    slack.chat.post_message(slack_channel, '>>> New Host Found:  '+slack_msg+' *Found* *in* *:* '+str(box_name),username='NMAP_new_host')

def notify_slack_forbidden_port(a,b,c,d):   
    slack.chat.post_message(slack_channel,'>>> Illegal Port found open :'+a+'/'+b+' '+c+' , *on =>* '+d+' *Found* *in* *:* '+str(box_name),username='NMAP_forbidden_port')
    
def notify_slack_changed_port(a,b,c):
    # print "For %s, Port changed from %s to %s" %(key,self.old_port_dict[key],self.new_port_dict[key])
    slack.chat.post_message(slack_channel,'>>> For '+a+' Port changed from '+b+' *to ===>>* '+c+' *Found* *in* *:* '+str(box_name),username='NMAP_change_port')

    
def notify_pagerduty_forbidden_port(a,b,c,d):      ## Call this when a Forbidden port has been open up 
    headers = {
        'Authorization': 'Token token={0}'.format(API_ACCESS_KEY),
        'Content-type': 'application/json',
    }
    payload = json.dumps({
      "service_key": API_ACCESS_KEY,
     # "incident_key": "illegal/port",   ## Coment this or use a uuid because this will generate different incidents 
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
###############################################################################

def gather_public_ip():
    ACCESS_KEY = config.get('aws','access_key')
    SECRET_KEY = config.get('aws','secret_key')
    regions = regions = ['us-west-2','eu-central-1','ap-southeast-1']
#    regions = config.get('aws','region').split(',')
    all_EIP = []
    for region in regions:
       client = boto3.client('ec2',aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY,region_name=region,)
       addresses_dict = client.describe_addresses()
       with open('/tmp/portdump_list', 'a') as f:
         for eip_dict in addresses_dict['Addresses']:
           if 'PrivateIpAddress' in eip_dict:
              print eip_dict['PublicIp']
              f.write(eip_dict['PublicIp']+'\n')
    return 
#################################################################################################


class Report(object):
    """Object for analyzing scan results and and identiying new hosts and ports"""

    def __init__(self,report):
        self.prev_report = None 
        self.report = report
        self.prev_hosts = set()
        self.curr_hosts = set()
        self.new_port_dict = {}       # Dictionary to store the new ports from curr_host
        self.old_port_dict = {}       # Dictionary to store the old ports from old_host
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
            
            for s in self.prev_report.hosts:
                self.old_port_dict[s.address] = set()
                for x in s.get_open_ports():
                    self.old_port_dict[s.address].add(x)                   
                
            for s in self.report.hosts:
                self.new_port_dict[s.address] = set()
                for x in s.get_open_ports():
                   self.new_port_dict[s.address].add(x)
                     
            print "The following Host/ports were available in old scan : !!"
            print `self.old_port_dict`
            print "--------------------------------------------------------"
            print "The following Host/ports have been added in new scan:  !!"
            print `self.new_port_dict`  
            
            ##
            
            for h in self.old_port_dict.keys(): 
                 self.results_ports_dict[h] = self.new_port_dict[h]- self.old_port_dict[h]
                 print "Result Change: for",h ,"->",self.results_ports_dict[h]       
            ################### The following code is intensive  ###################
                   
            print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
            diff_key=[key for key in self.old_port_dict if self.old_port_dict[key]!=self.new_port_dict[key]]
            for key in diff_key:
                 print "For %s, Port changed from %s to %s" %(key,self.old_port_dict[key],self.new_port_dict[key])
                 notify_slack_changed_port(str(key),str(self.old_port_dict[key]),str(self.new_port_dict[key]))          ####
                                
      except Exception as l:
             print l 
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
              
           # val = config.get('ports', 'scan_range')
            val_known = config.get('ports','known')

           # safe_port = range(*map(int, val.split(',')))
            known_ports = map(int, val_known.split(','))

            print("  PORT     STATE         SERVICE")

            for serv in host.services:
                if serv.port  in (known_ports):
                  print ('Illegal Port open :'+str(serv.port) +'/'+str(serv.protocol)+' '+str(serv.service)+', on host=> '+str(host))
                  
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
     
    def run(self, targets="" ,options="-Pn -iL /tmp/portdump_list -p 22,5061,8080,443,80,8987,3306,3389 "):
        #start a new nmap scan on localhost with some specific options

        syslog.syslog("Scan started")
        parsed = None
        nmproc = NmapProcess(targets,options)
        rc = nmproc.run()
#####################################################################################################
        nmproc.run_background()
        while nmproc.is_running():
            print("Nmap Scan running: ETC: {0} DONE: {1}%".format(nmproc.etc,nmproc.progress))
            time.sleep(2)
        print("rc: {0} output: {1}".format(nmproc.rc, nmproc.summary))

#####################################################################################################
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
        net_range = gather_public_ip()  #config.get('sources','networks')
        r = s.run()#(net_range)
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
