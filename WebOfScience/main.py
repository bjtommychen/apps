
from wos import WokmwsSoapClient

print 'start!'
soap = WokmwsSoapClient()
results = soap.search('AU=Hallam')
print 'end!'
print results.recordsFound


