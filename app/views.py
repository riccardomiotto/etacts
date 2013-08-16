from app import app
from flask import render_template, jsonify, request, session
from lib.extensions import cache
from lib.log import logger
from lib.forms import SearchForm
import lib.oformat as of
import lib.tagcloud as tcloud
import lib.ctgov as ctgov

log = logger ('etacts-view')


# home page
@app.route('/etacts')
def index ():
    # get trial number
    nnct = ctgov.get_nct_number ('http://clinicaltrials.gov/search?term=&displayxml=True&count=0')
    # search form    
    form = SearchForm()
    return render_template('index.html', form = form, nnct = of.format_nct_number(nnct))


# about page
@app.route ('/etacts/about')
def about ():
    print 'ciao'
    return render_template('about.html')


# help page
@app.route('/etacts/help')
def help_page():
    return render_template('/help/help.html')

# search definitions page
@app.route('/etacts/definitions')
def definitions_page():
    return render_template('/help/definitions.html')


# tag cloud from regular search
@app.route ('/_tag_cloud')
def tag_cloud ():
    # get parameters
    stxt = request.args.get ('stxt')
    # save the query in session
    session.clear()
    session['query'] = stxt
    session.modified = True
    # get trials and tags
    rnct = ctgov.get_initial_nct (stxt)
    nct = set ()
    for r in rnct:
        tkn = r.split(';')
        nct.add (tkn[0])
    # get tags for the first cloud
    cloud = tcloud.get_initial_cloud (nct, 20, 10)
    log.info ('%s -- first tag cloud' % (request.remote_addr))
    return jsonify (tags = cloud , nct = rnct, q = stxt, n = len(rnct))


# tag cloud from advanced search
@app.route('/_advs_tag_cloud')
def advs_tag_cloud():
    qlabel = request.args.get('qlabel')
    # save the query in session
    session.clear()
    session['query'] = qlabel
    session.modified = True
    # get trials
    url = ctgov.form_advanced_search_url (request.args)
    rnct = ctgov.get_initial_nct_from_url (url)
    nct = set ()
    for r in rnct:
        tkn = r.split(';')
        nct.add (tkn[0])
    # get randomized tags for the cloud
    cloud = tcloud.get_initial_cloud (nct, 20, 10)
    log.info ('%s -- first tag cloud' % (request.remote_addr))
    return jsonify (tags = cloud , nct = rnct, q = qlabel, n = len(rnct))


# search for clinical trials
@app.route('/_ctgov_search')
def ctgov_search ():
    stxt = request.args.get ('stxt')
    npag = request.args.get ('npag')
    (n, nct) = ctgov.search (stxt, npag)
    if (stxt is None) or (len(stxt) == 0):
        stxt = 'all'
    if npag == '1':
        log.info('%s -- ct.gov-search: q("%s") - res(%s trials)' % (request.remote_addr, stxt, n))
    return jsonify (n=n, nct=nct, q=stxt, npag=npag)


# advanced search for clinical trials
@app.route('/_adv_search')
def ctgov_advanced_search():
    (n, nct) = ctgov.advanced_search(request.args)
    term = request.args.get('term')
    npag = request.args.get('npag')
    fq = of.format_query2print (request.args)
    if npag == '1':
        log.info('%s -- ct.gov-advanced-search: q(%s) - res(%s trials)' % (request.remote_addr, fq, n))
    return jsonify (n=n, nct=nct, q = fq, npag = npag)


# refine search
@app.route ('/_refine_search', methods=['POST'])
def refine_search ():
    tag = list(request.form['tag'].split(';'))
    rnct = of.format_ranked_nct (request.form['nct'])
    npag = int (request.form['npag'])
    tgrp = request.form['ttag']
    trole = request.form['trole']
    (snct, unct) = tcloud.get_filtered_result (tag, rnct, npag)
    log.info ('%s -- refine-search: tags(%s) | left(%d trials)' % (request.remote_addr, ';'.join(tag), len(unct)))
    ctag = []
    if len(unct) > 0:
        ctag = tcloud.get_tagcloud (unct, tag, 20, 10, tgrp, trole)
    return jsonify (n=of.format_nct_number(len(unct)), npag=npag, tags=ctag, q=session['query'], onct=request.form['nct'], nct=of.format_nct(snct))


# refine search
@app.route ('/_turn_fresult', methods=['POST'])
def turn_fresult ():
    tag = list(request.form['tag'].split(';'))
    rnct = of.format_ranked_nct(request.form['nct'])
    npag = int (request.form['npag'])
    log.info ('%s -- visiting page n. %d' % (request.remote_addr, npag))
    (snct, unct) = tcloud.get_filtered_result (tag, rnct, npag)
    return jsonify (n=of.format_nct_number(len(unct)), npag=npag, onct=request.form['nct'], nct=of.format_nct(snct))


# close the session
@app.route ('/_clean')
def clean ():
    q = session['query']
    session.clear()
    session.modified = True
    log.info ('%s -- tag cloud closed' % request.remote_addr)
    return jsonify (n=0, q=q)


# refine the tag-cloud according to the category
@app.route ('/_refine_tagcloud', methods=['POST'])
def refine_tagcloud():
    tgrp = request.form['ttag']
    tag = list(request.form['tag'].split(';'))
    rnct = of.format_ranked_nct (request.form['nct'])
    nct = tcloud.filter_by_tag (tag, rnct)
    trole = request.form['trole']
    ctag = []
    if len(nct) > 1:
        ctag = tcloud.get_tagcloud (nct, tag, 20, 10, tgrp, trole)
    return jsonify (tags=ctag, nct=request.form['nct'], tgrp=tgrp, trole=trole)





