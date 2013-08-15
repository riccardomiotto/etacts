# functions to fomat data

from app import app
from xml.etree import ElementTree
from web import download_web_data
from log import logger
import urllib

log = logger ('etacts-oformat')

# format search terms
def format_search_terms (txt):
    if txt is None:
        return ''
    txt = txt.lower()
    txt = txt.lower().replace(' and ',' ').replace(' or ',' ')
    return urllib.quote_plus(txt)


# format clinical trial number for presentation
def format_nct_number (nnct):
    return '{:,d}'.format (int(nnct))


# build rank-nct from a string
def format_ranked_nct (nct):
    rnct = {}
    for el in nct.split(','):
        tkn = el.split(';')
        rnct[tkn[0]] = int(tkn[1])
    return rnct


# format  the condition for printing
def format_condition (cond):
     tkn = cond.split(';')
     if len(tkn) > 3:
         return '%s; %s; %s; ...' % (tkn[0].strip(), tkn[1].strip(), tkn[2].strip())
     return cond
    

# format list of trials <id, rank> for printing
def format_nct (nct):
    snct = []
    url = 'http://clinicaltrials.gov/ct2/show/%s?displayxml=true'
    for ct in nct:
        if ct[0] in app.jinja_env.globals['ctgov_idx']:
            title = app.jinja_env.globals['ctgov_idx'][ct[0]][0]
            cond = format_condition(app.jinja_env.globals['ctgov_idx'][ct[0]][1])
        else:
            xmltree = ElementTree.fromstring (download_web_data(url % ct[0]))
            title = xmltree.find ('brief_title')
            # title
            if title is None:
                title = ct[0]
            else:
                title = title.text
            # condition        
            lcond = xmltree.findall ('condition')
            cond = ''
            if lcond is not None:
                for c in lcond:
                    if c is not None:
                        cond = '%s; %s' % (cond, c.text)
                cond = cond[2:]
            app.jinja_env.globals['ctgov_idx'][ct[0]] = (title, cond)
            cond = format_condition (cond)
            log.info ('added %s to the CTGOV idx (updated to %d trials)' % (ct[0], len(app.jinja_env.globals['ctgov_idx'])))
        snct.append ((ct[0], ct[1], title, cond))
    return snct


# format the advanced query to print on screen
def format_query2print (param):
    # to determine the order of the query summarizing string
    lparam = ['term', 'recr', 'rslt', 'type', 'cond', 'intr', 'titles', 'outc', 'spons', 'lead',
              'id', 'state1', 'cntry1', 'state2', 'cntry2', 'state3', 'cntry3', 'locn', 'gndr',
              'age', 'phase', 'fund', 'safe', 'rcv_s', 'rcv_e', 'lup_s', 'lup_e']
    qstr = ''
    # first variables
    for p in lparam[:11]:
        v = param.get(p)
        if (v is None) or (len(v) == 0):
            continue
        fv = v
        # recruitment
        if (p == 'recr') and ((v == 'Open') or (v == 'Closed')):
            fv = '%s Studies' % v
        # results
        elif p == 'rslt':
            fv = 'Studies %s Results' % v 
        # type
        elif p == 'type':
            if v == 'Intr':
                fv = 'Interventional Studies'
            elif v == 'Obsr':
                fv = 'Observational Studies'
            elif v == 'PReg':
                fv = 'Observational, Patient Registry Studies'
            elif v == 'Expn':
                fv = 'Expanded Access Studies'
        qstr += fv + ' | '
    # state and contry
    added = False
    used = set()
    for i in xrange(1,4):
        s = param.get ('state%d' % i)
        c = param.get ('cntry%d' % i)
        fv = ''
        if len(c) > 0 and len(s) > 0:
            if c in s:
                fv = param.get ('fstate%d' % i)
            else:
                fv = '%s - %s' % (param.get('fstate%d' % i), param.get('fcntry%d' % i))
        elif len(c) > 0:
            fv = param.get ('fcntry%d' % i)
        elif len(s) > 0:
            fv = param.get ('fstate%d' % i)
        if (len(fv) > 0) and (fv not in used):
            used.add (fv)
            qstr += fv + ' | '
    for p in lparam[17:len(lparam)-4]:
        lv = param.getlist(p)
        if (lv is None) or (len(lv) == 0):
            continue
        stmp = ''
        for v in lv:
            fv = v.strip()
            # gender
            if (p == 'gndr') and ('male' in v.lower()):
                fv = 'Studies with %s Participants' % v
            # age
            elif p == 'age':
                if v == '0':
                    fv = 'Child'
                elif v == '1':
                    fv = 'Adult'
                elif v == '2':
                    fv = 'Senior'
            # phase
            elif p == 'phase':
                if v == '4':
                    fv = '0'
                else:
                    fv = str(int(v) + 1)
            # fund
            elif p == 'fund':
                if v == '1':
                    fv = 'Other U.S. Federal Agency'
                elif v == '2':
                    fv = 'Industry'
                elif v == '3':
                    fv = 'Other'
                else:
                    fv = 'NIH'
            # safe
            elif p == 'safe':
                fv = 'Has safety issue outcome measures'
            if len(fv.strip()) > 0:
                stmp += fv + ', '
        if p == 'phase':
            stmp = 'Phase: %s' % stmp
        if len(stmp.strip()) > 0:
            qstr += stmp[:len(stmp)-2] + ' | '
    # received date
    s = _format_query_date (param, 'received', 'rcv_s', 'rcv_e')
    if len(s) > 0:
        qstr += s + ' | '
    # last update date
    s = _format_query_date (param, 'updated', 'lup_s', 'lup_e')
    if len(s) > 0:
        qstr += s + ' | '
    if len(qstr) == 0:
        return 'all'
    return qstr[:len(qstr)-3].strip()


# format date of the advanced query
def _format_query_date (param, head, s, e):
    sd = param.get(s)
    ed = param.get(e)
    if (len(sd) > 0) and (len(ed) > 0):
        return '%s from %s to %s' % (head, sd, ed)
    if len(sd) > 0:
        return '%s on or after %s' % (head, sd)
    if len(ed) > 0:
        return '%s on or before %s' % (head, ed)
    return ''
    
    

