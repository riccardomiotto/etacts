'''
set of functions to handle the tag cloud
'''

from app import app
from log import logger
from flask import request
import random, math

log = logger ('etacts-oformat')


# inverted idx with the documents returned by the initial query
def get_tags_by_frequency (nct, tgrp, trole):
    tags = {}
    mgrp = map_group (tgrp)
    osum = 0
    for t in app.jinja_env.globals['iidx']:
        if (max(0,t.find(':')+1) == 0) and (trole == 'exc'):
            continue
        if ' age = ' in t:
            continue
        if (max(0,t.find(':')+1) > 0) and (not t.startswith(trole)):
            continue
        pt = clean_tag (t)
        if pt not in app.jinja_env.globals['tag2group']:
            continue
        g = app.jinja_env.globals['tag2group'][pt]
        if (mgrp != 'all') and (mgrp not in g):
            continue
        ct = nct & app.jinja_env.globals['iidx'][t]
        if (len(ct) == 0) or (len(ct) == len(nct)):
            continue
        tags[t] = len(ct)
        osum += len(ct)    
    return [(k, 50 * v/float(osum)) for k,v in reversed(sorted(tags.iteritems(), key = lambda x:x[1]))]


# filter search results by tags
def filter_by_tag (tag, nct):
    unct = set(nct.keys())
    for t in tag:
        if t not in app.jinja_env.globals['iidx']:
            continue
        unct &= app.jinja_env.globals['iidx'][t]
        # if ('gender =' in t) or ('age =' in t) or (max(0,t.find(':')+1) == 0):
        #    continue
        # tag context
        # prefix = t[:3]
        # ctag = t[4:]
        # work with the other prefix
        # if prefix == 'inc':
        #    npfx = 'exc'
        # else:
        #     npfx = 'inc'
        # tnew = '%s:%s' % (npfx, ctag)
        # if tnew not in app.jinja_env.globals['iidx']:
        #    continue
        # if len(unct - app.jinja_env.globals['iidx'][tnew]) > 0:
        #    unct -= app.jinja_env.globals['iidx'][tnew]
    return unct


# refine search results by tag
def get_filtered_result (tag, rnct, npag):
    unct = filter_by_tag (tag, rnct)
    # sort by original rank
    snct = []
    for nct in unct:
        snct.append ((nct, rnct[nct]))
    snct.sort(key=lambda x: x[1])
    # select data to visualize
    first = 20 * (npag - 1)
    last = (20 * npag)
    if last > len(snct):
        last = len(snct)
    snct = snct[first:last]
    return (snct, unct)


# get tag for the updated cloud
def get_tagcloud (nct, tag, ntag, nrand, tgrp, trole):
    ftags = get_tags_by_frequency (nct, tgrp, trole)
    admittable = set([t[0] for t in ftags])
    used = get_used_tags (tag)
    admittable -= used
    used = set([clean_tag(u) for u in used])
    cloud = []
    ltag = tag
    while len(ltag) > 0:
        tp = tuple(sorted(ltag))
        if tp in app.jinja_env.globals['arule']:
            for t in app.jinja_env.globals['arule'][tp]:
                if not tag_validity (t[0], admittable, used, nct):
                    continue
                cloud.append ((t[0], t[1]*10*len(ltag)))
                admittable -= set([t[0]])
                used.add (clean_tag(t[0]))
        if len(cloud) >= ntag:
            log.info ('%s -- tag-cloud: %d tags with arule' % (request.remote_addr, len(cloud)))
            if len(cloud) >= (ntag + nrand):
                return random_tags (cloud, ntag, nrand)
            return cloud[:ntag]
        ltag.pop()
    log.info ('%s -- tag-cloud: %d tags with arule' % (request.remote_addr, len(cloud)))
    for t in ftags:
        if not tag_validity (t[0], admittable, used, nct):
            continue
        cloud.append ((t[0], t[1]))
    if len(cloud) >= ntag:
        if len(cloud) >= (ntag + nrand):
            return random_tags (cloud, ntag, nrand)
        return cloud[:ntag]
    return cloud


# check if the tag for the cloud filter the results
def is_tag_filtering (nct, tag):
    lfilt = len(nct & app.jinja_env.globals['iidx'][tag])
    if (lfilt == len(nct)):
        log.info ('%s -- tag "%s" not discriminative' % request.remoted_addr)
        return False
    if (lfilt == 0):
        print '000 - ' + tag
        return False
    return True


# extract random tags for the cloud
def random_tags (cloud, ntag, nrand):
    half = int(math.floor (ntag/2))
    tfirst = cloud[:half]
    tlast = cloud[half:(ntag+nrand)]
    random.shuffle (tlast)
    rcloud = tfirst + tlast
    return rcloud[:ntag]


# map group to extended version
def map_group (grp):
    if (grp is None) or (grp == 'all'):
        return 'all'
    if grp == 'disorders':
        return 'Disorders'
    if grp == 'lab':
        return 'Laboratory and Tests'
    if grp == 'procedures':
        return 'Procedures'
    if grp == 'drugs':
        return 'Chemical and Drugs'
    if grp == 'others':
        return 'Others'
    return 'all'


# remove prefix and negation from the tag
def clean_tag (t):
    pt = t[max(0,t.find(':')+1):]
    if pt.startswith('NOT '):
        pt = pt[4:]
    return pt


# get extended used tags
def get_used_tags (tags):
    used = set ()
    for t in tags:
        if ('age = ' in t) or ('gender =' in t):
            used.add (t)
            continue
        pt = clean_tag (t)
        # save all combinations
        used.add ('inc:' + pt)
        used.add ('inc:NOT ' + pt)
        used.add ('exc:' + pt)
        used.add ('inc:NOT ' + pt)
    return used


# check tag validity
def tag_validity (t, admittable, used, nct):
    if t not in admittable:
        return False
    if not is_tag_filtering (nct, t):
        return False
    if is_substring (t, used):
        return False
    return True


# check if tag is ax exact substring of one already used
def is_substring (t, used):
    pt = clean_tag(t).split()
    for u in used:
        lu = u.split()
        if any((pt== lu[i:i+len(pt)]) for i in xrange(len(lu)-len(pt)+1)):
            return True
    return False


# first tag cloud
def get_initial_cloud (nct, ntag, nrand):
    cloud = []
    if len(nct) > 0:
        cloud = get_tags_by_frequency (nct, 'all', 'inc')
        if len(cloud) >= (ntag + nrand):
            cloud = random_tags (cloud, ntag, nrand)
        elif len(cloud) > ntag:
            cloud = cloud[:ntag]
    return cloud
        




