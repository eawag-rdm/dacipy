# _*_ coding: utf-8 _*_
''' dacipy

Command line client for the DataCite MDS - API:
https://support.datacite.org/v1.1/reference

Usage: dacipy doi_geturl [-t] [-u SYMBOL] [-a APIKEY] DOI
       dacipy doi_create [-t] [-u SYMBOL] [-a APIKEY] DOI URL
       dacipy doi_list [-t] [-u SYMBOL] [-a APIKEY] 
       dacipy meta_get [-t] [-u SYMBOL] [-a APIKEY] DOI
       dacipy meta_create [-t] [-u SYMBOL] [-a APIKEY] (XMLFILE | -)
       dacipy meta_delete [-t] [-u SYMBOL] [-a APIKEY] DOI

Options:
    -u <symbol>    The DataCite symbol used as username. Uses environment
                   variable DATACITE_SYMBOL as default unless "-t" is set,
                   in which case the default is DATACITE_TEST_SYMBOL.
    -a <apikey>    The DataCite API-key associated with <symbol>. Uses
                   environment variable DATACITE_APIKEY as default unless "-t"
                   is set, in which case the default is DATACITE_TEST_APIKEY.
    -t             Use the mds - sandbox (/mds.test.datacite.org).



'''
from sys import argv, exit 
from . import dacipy as da
from docopt import docopt
from os import environ

def _getauth(args):
    if args['-t']:
        envvars = ['DATACITE_TEST_SYMBOL', 'DATACITE_TEST_APIKEY']
    else:
        envvars = ['DATACITE_SYMBOL', 'DATACITE_APIKEY']
    try:
        envsym = environ[envvars[0]]
    except KeyError:
        envsym = None
    try:
        envapikey = environ[envvars[1]]
    except KeyError:
        envapikey = None
        
    res = [args['-u'] or envsym, args['-a'] or envapikey]
    if any([x is None for x in res]):
        exit("Incomplete authentification information:\n"
             + "SYMBOL: {}\n".format(res[0])
             + "APIKEY: {}\n".format(res[1]))
    return res

def main():
    if args['doi_geturl']:
        res = dc.doi_geturl(doi)
        print(res.content)
        return
    if args['doi_create']:
        res = dc.doi_create(doi, url)
        print(res.content)
        return
    if args['doi_list']:
        res = dc.doi_list()
        print(res.content)
        return
    if args['meta_get']:
        res = dc.metadat_get(doi)
        print(res.content)
        return
    if args['meta_create']:
        res = dc.metadata_create(xml)
        print(res.content)
        return
    if args['meta_delete']:
        res = dc.metadata_delete(doi)
        print(res.content)
        return

args = docopt(__doc__, argv=argv[1:], help=True)
doi = args['DOI']
url = args['URL']
dc = da.DaciAPI(*_getauth(args), test=args['-t'])
main()
# res = _getauth(args)
# print(dc.auth)
# print(dc.host)

