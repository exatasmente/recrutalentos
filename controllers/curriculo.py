
table = db.curriculo
response.view_title = '%s %s' % (
    request.function.replace('_', ' ').title(),
    table._singular
)


def index():
    redirect(URL(request.controller, 'list'))


def list():
    announcement = None  # XML(response.render('announcement.html'))
    query = (table)
    items = db(query).select(orderby=~table.id).render()

    actions = [
        {'is_item_action': lambda item: True, 'url': lambda item: URL(
            'view.html', args=[item.id]), 'icon': 'search'},
        {'is_item_action': lambda item: True, 'url': lambda item: URL(
            'edit.html', args=[item.id]), 'icon': 'pencil'}
    ]

    fields = [f for f in table]
    # fields = [
    #     table.id,
    #     table.created_on, table.created_by,
    # ]

    response.view = 'template/list.%s' % request.extension
    return dict(
        item_name=table._singular,
        row_list=items,
        actions=actions,
        field_list=fields,
        announcement=announcement
    )


@auth.requires_login()
def create_step2():
    form = SQLFORM.factory(
        Field("instituicao","string",label="Instituição"),
        Field("tipo","integer",label="Formação",requires = IS_IN_SET(((1,"Superior"),(2,"Técnico"),(3,"Médio"),(4,"Fundamental"),(5,"Não se aplica")))),
        Field("curso","string",label="Curso",default="Não Se Aplica"),
        Field("situacao","integer",label="Situação", requires = IS_IN_SET(((1,"Completo"),(2,"Incompleto"),(3,"Cursando")))),
        Field("ano_inicio","date",label="Ano de Inicio",requires = IS_DATE(format=('%m/%d/%Y'))),
        Field("ano_conclusao","date",label="Ano de Conclusão",requires = IS_DATE(format=('%m/%d/%Y'))),
        hidden = dict(id_curriculo=session.data),
        buttons = [BUTTON('Voltar', _type="button", _onClick="parent.location='%s'" %URL(request.controller, 'create')),BUTTON('Avançar', _type="submit")]
    )
    
    form.vars.id_curriculo = session.data
    if form.process().accepted:
        db.formacao_academica.insert(**db.formacao_academica._filter_fields(form.vars))
        response.flash = 'Formação Acadêmica Cadastrada'
        redirect(URL(request.controller, 'create_step3'))
    elif form.errors:
        response.flash = 'Please correct the errors'

    response.view = 'template/create.html'
    return dict(item_name="Formação Acadêmica", form=form)



@auth.requires_login()
def create_step3():
    form = SQLFORM.factory(
     Field("empresa","string",label="Nome da Empresa",notnull=True),
     Field("cargo","string",label="Cargo na Empresa",notnull=True),
     Field("duracao","integer",label="Periodo (em meses)",notnull=True),
     hidden = dict(id_curriculo=session.data),
     buttons = [BUTTON('Voltar', _type="button", _onClick="parent.location='%s'" %URL(request.controller, 'create')),BUTTON('Avançar', _type="submit")]
    )
    
    form.vars.id_curriculo = session.data
    if form.process().accepted:
        db.experiencia.insert(**db.experiencia._filter_fields(form.vars))
        response.flash = 'Experiência Profissional Cadastrada'
        redirect(URL(request.controller, 'list'))
    elif form.errors:
        response.flash = 'Please correct the errors'
    response.view = 'template/create.html'
    return dict(item_name="Experiência Profissional", form=form)

@auth.requires_login()
def create():
    form = SQLFORM(table)

    if form.process().accepted:
        session.data = form.vars.id

        redirect(URL(request.controller, 'create_step2'))
    elif form.errors:
        response.flash = 'Please correct the errors'

    response.view = 'template/create.html'
    return dict(item_name=table._singular, form=form)


def view():
    item = table(table.id == request.args(0)) or redirect(URL('index'))
    form = SQLFORM(table, item, readonly=True, comments=False)

    response.view = 'template/view.%s' % request.extension
    return dict(item_name=table._singular, form=form, item=item)


@auth.requires_login()
def edit():
    # db.support_case.case_subcategory.requires = IS_IN_DB(
    #     # db, db.case_subcategory._id, db.case_category._format,
    #     db, db.case_subcategory._id, '%(case_category)s*%(title)s',
    #     # sort=True,  # orderby=db.case_subcategory.title,
    #     # cache=(cache.ram, 60)
    # )

    item = table(request.args(0)) or redirect(URL('index'))
    form = SQLFORM(table, item)

    if form.process().accepted:
        session.flash = '%s updated!' % table._singular
        redirect(URL(request.controller, 'list'))
    elif form.errors:
        response.flash = 'Please correct the errors'

    response.view = 'template/edit.html'
    return dict(item_name=table._singular, form=form)


@auth.requires_membership('admin')
def populate():
    query = table
    set = db(query)
    # rows = set.select()
    set.delete()
    from gluon.contrib.populate import populate
    populate(table, 15)
    redirect(URL('list'))


@auth.requires_membership('admin')
def update():
    query = table
    set = db(query)
    rows = set.select()

    for row in rows:
        # row.xxxx = 'yyyy'
        row.update_record()

    redirect(URL('list'))
