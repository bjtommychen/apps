
from wos import *
soap = WokmwsSoapClient()
results = soap.search('AU=Hallam')
print results.recordsFound


