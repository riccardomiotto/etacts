'''
set of function to interact with ClinicalTrials.gov
'''

from app import app
from web import download_web_data
from xml.etree import ElementTree
from extensions import cache
import oformat as of
import urllib


# global ctgov search
def get_initial_nct (txt):
    txt = of.format_search_terms (txt)
    url = 'http://clinicaltrials.gov/search?term=%s&displayxml=true' % txt
    return get_initial_nct_from_url (url)


# global ctgov search from url
@cache.memoize(604800)
def get_initial_nct_from_url (url):
    # num. of studies available
    n = get_nct_number('%s&count=0' % url)
    if n == 0:
        return []
    # get the list of clinical studies
    xmltree = ElementTree.fromstring (download_web_data('%s&count=%d' % (url, n)))
    lnct = xmltree.findall ('clinical_study')
    rnct = []
    i = 1
    for ct in lnct:
        ids = ct.find ('nct_id')
        if ids is None:
            continue
        rnct.append ('%s;%d' % (ids.text,i))
        i += 1
    return rnct


# get result number
def get_nct_number (url):
    xml = download_web_data(url)
    if xml is None:
        return 0
    xmltree = ElementTree.fromstring (xml)
    nnct = xmltree.get ('count')
    return int(nnct)


# parse clinical trial details
def parse_xml_nct (ct):
    ids = ct.find ('nct_id')
    if ids is None:
        return ids
    ids = ids.text
    rank = ct.find ('order')
    if rank is not None:
        rank = rank.text
    title = ct.find ('title')
    if title is not None:
        title = title.text
    condition = ct.find ('condition_summary')
    if condition is not None:
        condition = condition.text
    return (ids, rank, title, condition)


# ctgov search
def search (txt, npag):
    txt = of.format_search_terms (txt)
    url = 'http://clinicaltrials.gov/search?term=%s&displayxml=true' % txt
    return retrieve_trials (url, npag)


# ctgov advanced search
def advanced_search(param):
    url = form_advanced_search_url (param)
    return retrieve_trials (url, param.get('npag'))


# get advanced search url
def form_advanced_search_url (param):
    ctg_param = ''
    for r in sorted(param):
        k = urllib.quote(r,'')
        if k == 'qlabel':
            continue
        for v in param.getlist(r):
            ctg_param += "%s=%s&" % (k, urllib.quote(v, ''))
    return 'http://clinicaltrials.gov/ct2/results?%sdisplayxml=True' % ctg_param
    

# get the list of resulting clinical trials
def retrieve_trials (url, npag):
    # num. of studies available
    n = of.format_nct_number(get_nct_number('%s&count=0' % url))
    # get the list of clinical studies
    xml = download_web_data('%s&pg=%s' % (url, npag))
    if xml is None:
        return (0, [])
    xmltree = ElementTree.fromstring (xml)
    lnct = xmltree.findall ('clinical_study')
    nct = []
    for ct in lnct:
        pct = parse_xml_nct (ct)
        if pct[0] is not None:
            if pct[0] not in app.jinja_env.globals['ctgov_idx']:
                app.jinja_env.globals['ctgov_idx'][pct[0]] = (pct[2], pct[3])
            cond = of.format_condition (pct[3])
            nct.append ((pct[0], pct[1], pct[2], cond))
    return (n, nct)
