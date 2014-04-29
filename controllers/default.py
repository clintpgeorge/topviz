# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

@auth.requires_login()
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Welcome to TopViz!")
    response.title = T("Category Hierarchy")
    response.subtitle = T('Whales')
    session.counter = (session.counter or 0) + 1

    filetable = TABLE(*[TR(TD(f["pageid"]), TD(f["title"])) for f in file_details])

    return dict(message=T("Welcome to TopViz!"),
                session_counter=session.counter,
                filetable=filetable)

@auth.requires_login()
def visualizepage():
    """
    Visualizes a page using a D3 bubble chart
    """
    p = None
    docid = None
    if len(request.vars) >= 2:
        p = request.vars['p']
        docid = int(request.vars['docid'])
    else:
        redirect(URL('index'))

    pageurl = wiki_url + p
    pagepath = join(request.folder, 'private', 'data', 'pages', slugify(p) + '.html')
    doc_bubble_data = {"name": "TF", "children":doc_nodes[docid]}
    # word_topics = doc_word_topics[docid]

    response.flash = T("Welcome to " + p)
    response.title = p
    response.subtitle = 'Word and Topic Distribution'

    page_html = ""
    with open(pagepath) as fp:
        page_html = fp.read()

    doc_pie_data = [{"label":lda_topic_labels[j], "value":value, "tid":j}
                    for j, value in enumerate(lda_theta[:, docid]/ np.sum(lda_theta[:, docid]))
                    if value > MIN_DISPLAY_TOPIC_PROB_VALUE]
    words_prob = []
    for t in range(0, vocab_count):
        words_prob.append([{"label":lda_topic_labels[j], "value":value, "tid":j}
                          for j, value in enumerate(lda_beta[:, t] / np.sum(lda_beta[:, t]))])

    return dict(session_counter=session.counter,
            pagetitle=p,
            page_html=page_html,
            doc_bubble_data=doc_bubble_data,
            pageurl=pageurl,
            words_prob=words_prob,
            doc_pie_data=doc_pie_data)

@auth.requires_login()
def visualizetopic():
    """
    Visualizes a topic distribution in word cloud
    """
    topic_label = None
    tid = None
    if len(request.vars) >= 2:
        topic_label = request.vars['cat']
        tid = int(request.vars['tid'])
    else:
        redirect(URL('index'))

    response.flash = T("Welcome to " + topic_label)
    response.title = topic_label
    response.subtitle = 'Topic Distribution'

    topic_wc_data = [{"text":vocabnames[j], "size":(value * 2000), "wid":j, "value":value}
                     for j, value in enumerate(lda_beta[tid, :] / np.sum(lda_beta[tid, :]))
                     if value > MIN_DISPLAY_WORD_PROB_VALUE]

    max_prob_wid = np.argmax(lda_beta[tid, :].tolist())
    max_prob_word = vocabnames[max_prob_wid];

    word_prob = []
    for t in range(0, vocab_count):
        word_prob.append([{"label":lda_topic_labels[j], "value":value, "tid":j}
                          for j, value in enumerate(lda_beta[:, t] / np.sum(lda_beta[:, t]))
                          if value > MIN_DISPLAY_TOPIC_PROB_VALUE])

    return dict(topic_wc_data=topic_wc_data, word_prob=word_prob,
                max_prob_wid=max_prob_wid, max_prob_word=max_prob_word)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())

'''
@auth.requires_login()
def indexdata():
    """
    Implements the index data page 
    """
    response.flash = T("Welcome to Index Data!")
    if request.vars.index_list:
        session.selected_project = request.vars.index_list
        redirect(URL('lucenesearch'))

    return dict(message=T("Index Data"), session_counter=session.counter)



@auth.requires_login()
def lucenesearch():
    """
    Implements the Lucene search page
    """
    response.flash = T("Welcome to Lucene Seach!")

    # if the session doesn't have an index
    if not session.selected_project:
        redirect(URL('index'))

    #if request.vars.lucene_query:
    #    session.lucene_query = request.vars.lucene_query
    #    redirect(URL('lucenesearchresults'))

    #return dict(message=T("Lucene Search"), session_counter=session.counter)

    # form = FORM(INPUT(_name='lucene_query', requires=IS_NOT_EMPTY()), INPUT(_type='submit'))
    form = SQLFORM.factory(Field('lucene_query',
                                 label='Enter query',
                                 requires=IS_NOT_EMPTY()))

    if form.process().accepted:
        session.lucene_query = form.vars.lucene_query
        redirect(URL('lucenesearchresults'))

    return dict(message=T("Lucene Search"), 
                session_counter=session.counter, 
                form=form)

@auth.requires_login()
def lucenesearchresults():
    """
    Implements the Lucene search results page
    """
    if not request.function=='lucenesearch' and not session.lucene_query:
        redirect(URL('lucenesearch'))

    response.flash = T("Welcome to Lucene Seach Results!")

    return dict(message=T("Lucene Search Results"), session_counter=session.counter)
'''