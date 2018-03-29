# _*_ coding: utf-8 _*_

# We assume the xml-input is UTF-8 encoded.
# This is Python 3, in Python 2 things might need to be fixed
# to properly deal with encoding issues.

# You have to have your passsword in the environment-variable
# DATACITE_APIKEY for the tests to run through.

import requests
from subprocess import run, PIPE, CalledProcessError
from sys import version_info, exit
import os.path
from os import environ
import logging
import io

if version_info.major != 3:
    exit('dacipy requires Python 3')

class DaciAPI:

    def __init__(self, symbol, password, test=True):
        '''Client for DataCite MDS - API

        Args:
          symbol: datacenter identifier, e.g. "EAWAG.RDM"
          password: API password for datacenter

        Both `password` and `symbol` are interpreted as environment variables
        containing the password (symbol), path to the password (symbol) in the
        `"pass" password manager <https://www.passwordstore.org/>`_, and as
        verbatim password (symbol). In that order. the first interpretation
        that works is applied.

        '''
        # read DataCite Symbol of datacenter
        try:
            symbol = os.environ[symbol]
        except KeyError:
            try:
                symbol = self._getpass(symbol)
            except CalledProcessError:
                pass
        # read Datacite API-password
        try:
            password = os.environ[password]
        except KeyError:
            try:
                password = self._getpass(password)
            except CalledProcessError:
                pass
        self.auth = (symbol, password)
        # set real- or test-host
        self.host = ('https://mds.test.datacite.org' if test
                     else 'https://mds.datacite.org')
        
    def _getpass(self, passpath):
        'Get password from "pass" password manager.'

        proc = run(['pass', passpath], stdout=PIPE, stderr=PIPE)
        proc.check_returncode()
        pw = proc.stdout.decode('utf-8').strip('\n')
        return pw

    def _getstream(self, thing):
        'Takes bytestream, filename or string and returns bytestream'
        
        try:
            thing.seek(0)
            stream = thing
        except AttributeError:
            try:
                stream = open(thing, 'rb')
            except FileNotFoundError:
                stream = io.BytesIO(thing.encode('utf-8'))
        return stream
        
    def _log(self, function, r):
        logging.error('{}: request returned {} - {}'
                            .format(function, r.status_code, r.text))
    
    def metadata_create(self, xml):
        ''' Associates a metadata-record with a doi or updates it.

        Args:
          xml: the metadata according to the `DataCite Metadata Schema 4.1 \
               <https://schema.datacite.org/meta/kernel-4.1/>`_. Can be either
               a bytestream, a filename, or a string.

        '''
        url = os.path.join(self.host, 'metadata')
        xmlstream = self._getstream(xml)
        headers={'Content-Type': 'application/xml', 'charset': 'UTF-8'}
        r = requests.post(url, data=xmlstream, headers=headers, auth=self.auth)
        xmlstream.close()
        if not r.ok:
            self._log('metadata_create', r)
        return r

    def metadata_get(self, doi):
        "Returns the metadata record associated with the <doi>."
        url = os.path.join(self.host, 'metadata', doi)
        headers = {'Accept': 'application/xml'}
        r = requests.get(url, headers=headers, auth=self.auth)
        return r
    
    def metadata_delete(self, doi):
        url = os.path.join(self.host, 'metadata', doi)
        r = requests.delete(url, auth=self.auth)
        return r

    def doi_list(self):
        url = os.path.join(self.host, 'doi')
        r = requests.get(url, auth=self.auth)
        return r

    def doi_geturl(self, doi):
        url = os.path.join(self.host, 'doi', doi) 
        r = requests.get(url, auth=self.auth)
        return r
    
    def doi_create(self, doi, resourceurl):
        url = os.path.join(self.host, 'doi', doi) 
        data = 'doi={}\nurl={}'.format(doi, resourceurl).encode('utf-8')
        r = requests.put(url, data=data,
                         headers={'Content-Type': 'text/plain',
                                  'charset': 'UTF-8'},
                         auth=self.auth)
        return r

# For the tests to work, your datacenter's actual symbol and apikey needs
# to be in environment variables DATACITE_TEST_SYMBOL and DATACITE_TEST_APIKEY,
# respectively.
    
import random
import re

def test__getstream():
    dc = DaciAPI('SYMBOL','nopathtonythingandnoenvironmentvariable')
    thing = '../tests/test.xml'
    thingtext = dc._getstream(thing).read(21)
    assert(thingtext == b"<?xml version='1.0' e")
    thing = open('../tests/test.xml', 'rb')
    thingtext = dc._getstream(thing).read(21)
    assert(thingtext == b"<?xml version='1.0' e")
    thing = "<?xml version='1.0' encoding="
    thingtext = dc._getstream(thing).read(21)
    assert(thingtext == b"<?xml version='1.0' e")

def test_DaciAPI():
    dc = DaciAPI('NOTINENV','nopathtonythingandnoenvironmentvariable')
    assert(dc.auth == ('NOTINENV','nopathtonythingandnoenvironmentvariable'))
    testkey = os.environ['DATACITE_TEST_APIKEY']
    testsymbol = os.environ['DATACITE_TEST_SYMBOL']
    os.environ['DATACITE_TEST_APIKEY'] = 'afakekey'
    os.environ['DATACITE_TEST_SYMBOL'] = 'symsymsymbol'
    dc = DaciAPI('DATACITE_TEST_SYMBOL', 'DATACITE_TEST_APIKEY')
    assert(dc.auth == ('symsymsymbol','afakekey'))
    os.environ['DATACITE_TEST_APIKEY'] = testkey
    os.environ['DATACITE_TEST_SYMBOL'] = testsymbol

def _changedoi():
    newdoi = '10.5072/' + str(random.sample(range(9999999999),1)[0])
    pat = re.compile(r'<identifier identifierType="DOI">(.*)</identifier>')
    with open('../tests/test.xml', 'r') as xmlbase:
        xml = xmlbase.read().strip()
    olddoi = re.search(pat, xml).group(1)
    newxml = re.sub(olddoi, newdoi, xml)
    with open('../tests/test.xml', 'w') as xmlbase:
        xmlbase.write(newxml)
    return (newxml, newdoi)

def test_metadata_create():
    dc = DaciAPI('DATACITE_TEST_SYMBOL','DATACITE_TEST_APIKEY')
    # test strin input
    newxml, newdoi = _changedoi()
    res = dc.metadata_create(newxml)
    assert(res.text.find(newdoi) > -1)
    # test stream input
    newxml, newdoi = _changedoi()
    with open('../tests/test.xml', 'r') as newxml:
        res = dc.metadata_create(newxml)
    assert(res.text.find(newdoi) > -1)
    # test filename input
    newxml, newdoi = _changedoi()
    res = dc.metadata_create('../tests/test.xml')
    assert(res.text.find(newdoi) > -1)
    
def test_metadata_get():
    pass

def test_doi_create_geturl():
    dc = DaciAPI('DATACITE_TEST_SYMBOL','DATACITE_TEST_APIKEY')
    resourceurl = 'https://not.existing.test-domain.xyz/resource'
    newxml, newdoi = _changedoi()
    res = dc.metadata_create(newxml)
    res = dc.doi_create(newdoi, resourceurl)
    doiurl = dc.doi_geturl(newdoi)
    assert(resourceurl == doiurl.text)
    
# test_DaciAPI()
# test__getstream()
# test_metadata_create()
# test_doi_create_geturl()
