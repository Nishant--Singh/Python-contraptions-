import requests
import json

list_mtcagent=requests.get('http://p-consul-server-1.use1.systeminsights.com:8500/v1/health/checks/mtcagent')
#print type(list_mtcagent)[

alive_agents=[]
for dicts in list_mtcagent.json():
    #print type(dicts)
    if dicts['Status'] == "passing":
        #print dicts['ServiceTags'][0]+'-'+dicts['ServiceTags'][1]
        alive_agents.append(dicts['ServiceTags'][0]+'-'+dicts['ServiceTags'][1])

print alive_agents
print "-----------------------"

list_mtc_collector=requests.get('http://p-consul-server-1.use1.systeminsights.com:8500/v1/health/checks/mtcagent-collector')

alive_collectors=[]
for collector in list_mtc_collector.json():
    if collector['Status'] == "passing":
        alive_collectors.append(collector['ServiceTags'][0])

    for agents in alive_agents:
        if  agents==collector["ServiceTags"][0] and collector['Status'] == "passing":
            print "Everything is Good with: "+agents
        elif agents==collector["ServiceTags"][0] and collector['Status'] == "critical":
            print "Bad-agents: "+agents
        else:
            pass

# print "Alive Agents with No Collectors ", set(alive_agents) - set(alive_collectors)

final = set()
final = set(alive_agents) - set(alive_collectors)

##print (str(final))

clean_final_list = map(str,final)


print clean_final_list

## str(final)[3:].encode('utf8'),

payload = {"text": "*Alive Agents with No Active Collectors ->*"+str(clean_final_list),"username": "Agent-Collector Bot"}

#print payload
post_to_channel=requests.post("https://hooks.slack.com/services/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",data=json.dumps(payload))
print "done"


