from bs4 import BeautifulSoup  # sudo pip install BeautifulSoup4
import requests
import time

from tqdm import tqdm  #pip install tqdm
from time import sleep
import sys
site = sys.argv[1]
ssl_lab_url = 'https://www.ssllabs.com/ssltest/analyze.html?d='+site

#req  = requests.get("https://www.ssllabs.com/ssltest/analyze.html?d=drtest.test.sentinelcloud.com")
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
#table = soup.find_all('table',class_='reportTable', limit=5)[-1]
#for td in table.select("td.tableLeft"):
#  data  = td.text.split()[0]
#  print data
print (CYELLOW+"The Prohibited Cipher list is:"+CEND),
#for n in prohibited_cipher_list:
#    print CRED+n+CEND
print CRED+str(prohibited_cipher_list)+CEND
    
time.sleep(1)
print CYELLOW+"Now Bringing in the LIST of cipher gathered from SSL LABS"+CEND
for i in tqdm(range(10000)):
  sleep(0.01)
  table = soup.find_all('table',class_='reportTable', limit=5)[-1]
  data = [ str(td.text.split()[0]) for td in table.select("td.tableLeft")]
print CGREEN+str(data)+CEND

time.sleep(1)
print CYELLOW2+"Now Starting to compare if the BAD ciphers are present in the site"+CEND
print CBLINK+"------------------------------------------------------------------"+CEND 
time.sleep(1)
if list(set(prohibited_cipher_list) & set(data)):
   print CRED+"BAD CIPHER FOUND !!:"+CEND
   print CRED+str("SITE --> "+str(site)+" is vulnerable!!")+CEND
   print CYELLOW+str((list(set(prohibited_cipher_list) & set(data))))+CEND
 
else: 
   print CGREEN+"NO BAD CIPHER FOUND , We are Good !!"+CEND
   print CGREEN+str("  "+str(site)+"  is Safe!!")+CEND
