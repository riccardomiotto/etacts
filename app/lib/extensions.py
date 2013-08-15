from flask.ext.cache import Cache
from log import slogger
import file as ufile
import sys

log = slogger ('etacts-ext')

cache = Cache(config={'CACHE_TYPE': 'filesystem', 'CACHE_DEFAULT_TIMEOUT': 86400, 'CACHE_THRESHOLD': 500, 'CACHE_DIR': 'app/resources/cache'})

'''
load the tag-to-semantic_category relationships
'''

# tag - semantic type
cvocab = ufile.read_csv ('app/resources/cvocab.csv')
if cvocab is None:
    log.error ('impossible to load the controlled vocabulary - interrupting')
    sys.exit()
type2tag = {}
tag2type = {}
for tag in cvocab:
    ptag = tag[0].strip()
    tkn = tag[1].replace('[','').replace(']','').split('\',')
    if len(tkn) > 3:
        continue
    ltype = set()
    for t in tkn:
        # type-to-tag
        typ = t.replace('\'','').strip()
        ltag = type2tag.setdefault(typ, set())
        ltag.add(ptag)
        type2tag[typ] = ltag
        # tag-to-type
        ltype.add (typ)
    tag2type[ptag] = ltype
        
# tag - group
sgroup = ufile.read_file ('app/resources/semantic-groups.txt')
if sgroup is None:
    log.error ('impossible to load the semantic categories - interrupting')
    sys.exit()
group2tag = {}
group2type = {}
tag2group = {}
for sg in sgroup:
	tkn = sg.strip().split('|')
        grp = tkn[0].strip()
        typ = tkn[2].strip().lower()
        if typ not in type2tag:
            continue
        # group-to-tag
        if typ in type2tag:
            ltag = group2tag.setdefault (grp, set())
            ltag |= type2tag[typ]
            group2tag[grp] = ltag
        # group-to-type
        ltype = group2type.setdefault (grp, set())
        ltype.add (typ)
        group2type[grp] = ltype
        # tag to group
        for t in type2tag[typ]:
            lgrp = tag2group.setdefault (t, set())
            lgrp.add (grp)
            tag2group[t] = lgrp

# remove tags with groups not admittable
agroup = set (group2tag.keys())
for t in tag2group.keys():
    grp = tag2group[t]
    gtype = set()
    for g in grp:
        if g in group2type:
            gtype |= group2type[g] 
    if len(tag2type[t] & gtype) != len(tag2type[t]):
        if ('disease' not in t) and ('transplantation' not in t):
            del tag2group[t]
log.info ('using %d different tags' % len(tag2group))

'''
load/compute the semantic inverted index
'''
iidx = ufile.read_obj ('app/resources/semantic-iidx.pkl')
if iidx is None:
    idx = ufile.read_obj ('app/resources/semantic-idx.pkl')
    if idx is None:
        log.error ('impossible to load the semantic index - interrupting');
        sys.exit()
    iidx = {}
    prefix = ['inc', 'exc']
    for ct in idx:
        for t in idx[ct]:
            if t.endswith('gender'):
                continue
            if ('gender =' in t) or ('age = ' in t):
                lct = iidx.setdefault(t, set())
                lct.add (ct)
                iidx[t] = lct
                if t not in tag2group:
                    tag2group[t] = 'Others'
                continue
            ptag = t[max(0,t.find(':')+1):]
            if ptag not in tag2group:
                continue
            if max(0,t.find(':')+1) > 0:
                lct = iidx.setdefault(t, set())
                lct.add (ct)
                iidx[t] = lct
            else:
                # if tag without prefix, add as both inlusion and exclusion
                for p in prefix:
                    et = '%s:%s' % (p,t)
                    lct = iidx.setdefault(et, set())
                    lct.add (ct)
                    iidx[et] = lct
    if len(iidx) == 0:
        log.error ('not found any data - interrupting')
        sys.exit()
    ufile.write_obj ('app/resources/semantic-iidx.pkl', iidx)
    log.info ('created inverted semantic index composed of %d tags' % len(iidx))

else:
    # extend tag2group
    for t in iidx:
        pt = t[max(0,t.find(':')+1):]
        if pt not in tag2group:
            tag2group[pt] = 'Others'

            
'''
load association rules
'''
arule = ufile.read_obj ('app/resources/tags-arule.pkl')
if arule is None:
    arule = {}
rcont = 0
for r in arule:
    rcont += len(arule[r])
log.info ('loaded association rules from file: %d rules' % rcont)



'''
load ctgov detail index
'''
ctgov_idx = ufile.read_obj ('app/resources/ctgov-idx.pkl')
if ctgov_idx is None:
    ctgov_idx = {}
log.info ('loaded ctgov details from file: %d trials' % len(ctgov_idx))

