import pprint
from datetime import datetime
from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup  # sudo pip install BeautifulSoup4
import requests
import time

from tqdm import tqdm  #pip install tqdm
from time import sleep
import sys

def call_ES_list_EMS():
    es = Elasticsearch()
    doc = {
    "query": {
    "bool": {
      "must": {
        "match": {
          "ansible.group_names": "ems_app"
        }
       }
     }
    },
    "_source": [
    "ansible.isv_alias",
    "ansible.EMS_URL"
    ],
    "size": 1000
    }
    es  = Elasticsearch()
    res = es.search(index="instances-i*",body=doc)
    pp = pprint.PrettyPrinter(indent=4)
    data = res['hits'] 
    list_of_urls = []
    for item in data['hits']:
        list_of_urls.append(str(item['_source']['ansible']['EMS_URL']))
    print list(set(list_of_urls))
    return list(set(list_of_urls))

def scan_cipher_ssl(list_url):
    for url in list_url:
        ssl_lab_url = 'https://www.ssllabs.com/ssltest/analyze.html?d='+url

        while True:
            req  = requests.get(ssl_lab_url)
            data = req.text
            soup = BeautifulSoup(data,"html5lib")
            #Clours
            CRED='\033[91m'
            CEND='\033[0m'
            CGREEN='\33[32m'
            CYELLOW = '\33[33m'
            CYELLOW2 = '\33[93m'
            CGREEN2  = '\33[92m'
            CBLINK    = '\33[5m'
            CBLUE   = '\33[34m'
        #
        ## List of Prohibited Cipher which should not be present ##
            prohibited_cipher_list=['TLS_DH_DSS_WITH_3DES_EDE_CBC_SHA','TLS_DH_RSA_WITH_3DES_EDE_CBC_SHA','TLS_DH_DSS_WITH_AES_128_CBC_SHA','TLS_DH_RSA_WITH_AES_128_CBC_SHA','TLS_DH_DSS_WITH_AES_256_CBC_SHA','TLS_DH_RSA_WITH_AES_256_CBC_SHA','TLS_DH_DSS_WITH_AES_128_CBC_SHA256','TLS_DH_RSA_WITH_AES_128_CBC_SHA256','    TLS_DH_DSS_WITH_AES_256_CBC_SHA256','TLS_DH_RSA_WITH_AES_256_CBC_SHA256','TLS_DH_DSS_WITH_CAMELLIA_128_CBC_SHA','TLS_DH_RSA_WITH_CAMELLIA_128_CBC_SHA','     TLS_DH_DSS_WITH_CAMELLIA_256_CBC_SHA','TLS_DH_RSA_WITH_CAMELLIA_256_CBC_SHA','TLS_DH_DSS_WITH_SEED_CBC_SHA','TLS_DH_RSA_WITH_SEED_CBC_SHA','   TLS_DH_RSA_WITH_AES_128_GCM_SHA256','TLS_DH_RSA_WITH_AES_256_GCM_SHA384','TLS_DH_DSS_WITH_AES_128_GCM_SHA256','TLS_DH_DSS_WITH_AES_256_GCM_SHA384','    TLS_ECDH_ECDSA_WITH_NULL_SHA','TLS_ECDH_ECDSA_WITH_RC4_128_SHA','TLS_ECDH_ECDSA_WITH_3DES_EDE_CBC_SHA','TLS_ECDH_ECDSA_WITH_AES_128_CBC_SHA','   TLS_ECDH_ECDSA_WITH_AES_256_CBC_SHA','TLS_ECDH_RSA_WITH_NULL_SHA','TLS_ECDH_RSA_WITH_RC4_128_SHA','TLS_ECDH_RSA_WITH_3DES_EDE_CBC_SHA','     TLS_ECDH_RSA_WITH_AES_128_CBC_SHA','TLS_ECDH_RSA_WITH_AES_256_CBC_SHA','TLS_ECDH_ECDSA_WITH_AES_128_CBC_SHA256','TLS_ECDH_ECDSA_WITH_AES_256_CBC_SHA384','     TLS_ECDH_RSA_WITH_AES_128_CBC_SHA256','TLS_ECDH_RSA_WITH_AES_128_CBC_SHA256','TLS_ECDH_ECDSA_WITH_AES_128_GCM_SHA256','TLS_ECDH_ECDSA_WITH_AES_256_GCM_SHA384','  TLS_ECDH_RSA_WITH_AES_128_GCM_SHA256','TLS_ECDH_RSA_WITH_AES_256_GCM_SHA384']

            refresh = soup.find_all('meta', attrs={'http-equiv': 'refresh'})
            print 'refresh:', refresh

            if not refresh:
               break  
                               
            wait = int(refresh[0].get('content','0').split(';')[0])
            print 'wait:', wait
            time.sleep(wait)
        #############################################################################################33
        print CYELLOW+"Now Bringing in the LIST of cipher gathered from SSL LABS for "+str(ssl_lab_url)+CEND
        table = soup.find_all('table', class_='reportTable', limit=5)
        if table:
            table = table[-1]
            data = [str(td.text.split()[0]) for td in table.select("td.tableLeft")]
            print str(data)
        else:
            print "[!] no data"

        if list(set(prohibited_cipher_list) & set(data)):
                print CRED+"BAD CIPHER FOUND !!:"+CEND
                print CRED+str("SITE --> "+str(url)+" is vulnerable!!")+CEND
                print CYELLOW+str((list(set(prohibited_cipher_list) & set(data))))+CEND
        else:
                print CGREEN+"NO BAD CIPHER FOUND , We are Good !!"+CEND
                print CGREEN+str("  "+str(url)+"  is Safe!!")+CEND

if __name__ == "__main__":
  list_url = call_ES_list_EMS()
  scan_cipher_ssl(list_url )

