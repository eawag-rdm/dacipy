# For the tests to work, your datacenter's actual symbol and apikey needs
# to be in environment variables DATACITE_TEST_SYMBOL and DATACITE_TEST_APIKEY,
# respectively.

from .. import dacipy as da
from os import environ
import random
import re

def test__getstream():
    dc = da.DaciAPI('SYMBOL','nopathtonythingandnoenvironmentvariable')
    thing = 'data/test.xml'
    thingtext = dc._getstream(thing).read(21)
    assert(thingtext == b"<?xml version='1.0' e")
    thing = open('data/test.xml', 'rb')
    thingtext = dc._getstream(thing).read(21)
    assert(thingtext == b"<?xml version='1.0' e")
    thing = "<?xml version='1.0' encoding="
    thingtext = dc._getstream(thing).read(21)
    assert(thingtext == b"<?xml version='1.0' e")

def test_DaciAPI():
    dc = da.DaciAPI('NOTINENV','nopathtonythingandnoenvironmentvariable')
    assert(dc.auth == ('NOTINENV','nopathtonythingandnoenvironmentvariable'))
    testkey = environ['DATACITE_TEST_APIKEY']
    testsymbol = environ['DATACITE_TEST_SYMBOL']
    environ['DATACITE_TEST_APIKEY'] = 'afakekey'
    environ['DATACITE_TEST_SYMBOL'] = 'symsymsymbol'
    dc = da.DaciAPI('DATACITE_TEST_SYMBOL', 'DATACITE_TEST_APIKEY')
    assert(dc.auth == ('symsymsymbol','afakekey'))
    environ['DATACITE_TEST_APIKEY'] = testkey
    environ['DATACITE_TEST_SYMBOL'] = testsymbol

def _changedoi():
    newdoi = '10.5072/' + str(random.sample(range(9999999999),1)[0])
    pat = re.compile(r'<identifier identifierType="DOI">(.*)</identifier>')
    with open('data/test.xml', 'r') as xmlbase:
        xml = xmlbase.read().strip()
    olddoi = re.search(pat, xml).group(1)
    newxml = re.sub(olddoi, newdoi, xml)
    with open('data/test.xml', 'w') as xmlbase:
        xmlbase.write(newxml)
    return (newxml, newdoi)

def test_metadata_create():
    dc = da.DaciAPI('DATACITE_TEST_SYMBOL','DATACITE_TEST_APIKEY')
    # test strin input
    newxml, newdoi = _changedoi()
    res = dc.metadata_create(newxml)
    assert(res.text.find(newdoi) > -1)
    # test stream input
    newxml, newdoi = _changedoi()
    with open('data/test.xml', 'r') as newxml:
        res = dc.metadata_create(newxml)
    assert(res.text.find(newdoi) > -1)
    # test filename input
    newxml, newdoi = _changedoi()
    res = dc.metadata_create('data/test.xml')
    assert(res.text.find(newdoi) > -1)
    
def test_metadata_get():
    pass

# def test_doi_create_geturl():
#     dc = da.DaciAPI('DATACITE_TEST_SYMBOL','DATACITE_TEST_APIKEY')
#     resourceurl = 'https://not.existing.test-domain.xyz/resource'
#     newxml, newdoi = _changedoi()
#     res = dc.metadata_create(newxml)
#     res = dc.doi_create(newdoi, resourceurl)
#     doiurl = dc.doi_geturl(newdoi)
#     print(newdoi)
#     assert(resourceurl == doiurl.text)
    
