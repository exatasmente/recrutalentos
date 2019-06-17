
table = db.vaga
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
        {'is_item_action': lambda item: True, 'url': lambda item: URL(request.controller, 'view', args=[item.id]), 'icon': 'search'},
        {'is_item_action': lambda item: True, 'url': lambda item: URL('edit', args=[item.id]), 'icon': 'pencil'},
        {'is_item_action': lambda item: True, 'url': lambda item: URL(request.controller,'situacao', args=[item.id]), 'icon': 'cube'}
    ]

    fields = [f for f in table]
    # fields = [
    #     table.id,
    #     table.created_on, table.created_by,
    # ]

    
    return dict(
        item_name=table._singular,
        row_list=items,
        actions=actions,
        field_list=fields,
        announcement=announcement
    )


@auth.requires_login()
def create():
    form = SQLFORM.factory(
        Field('"nome"', 'string', label='"nome"'),
        Field("form_academica","integer",label="Formação Acadêmica",notnull=True,requires = IS_IN_SET(((1,"Superior"),(2,"Técnico"),(3,"Médio"),(4,"Fundamental"),(5,"Não se aplica")))),
        Field('experiencia', 'integer', label='Experiencia Profissional (em meses)'),
        Field('localTrabalho', 'string', label='Local de Trabalho'),
        Field('horario_inicio', 'time', label='Horario de Entrada'),
        Field('horario_fim', 'time', label='Horario de Saida'),
        Field('salarioOferecido', 'float', label='Salario Oferecido'),
        Field('qtdVagas', 'integer', label='Quantidade de Vagas'),
        Field('qtdCandidatos', 'integer', label='Quantidade de Candidatos'),
        Field('responsavelVaga', 'string', label='Responsável pela Vaga'),
        Field('prazo', 'date', label='Prazo para o Processo',requires = IS_DATE(format=('%m/%d/%Y')))
    )
    form.custom.widget.experiencia.update(_placeholder="em Meses")
    if form.process().accepted:
        id = db.vaga.insert(**db.vaga._filter_fields(form.vars))
        db.processo.insert(etapa=1,idVaga=id,prazo = form.vars.prazo)
        recrutalentos_pegaCurriculos(id)
        session.flash = "Vaga Adicionada com Sucesso"
        redirect(URL(request.controller, 'list'))
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

    
@auth.requires_membership('admin')
def situacao():
    return dict(nome_processo="Auxiliar Administrativo",candidatos=[
        {"nome":"Candidato 1","pontos":"10","foto":"http://127.0.0.1:8000/recrutalentos/static/img/avatar5.png"},
        {"nome":"Candidato 2","pontos":"5","foto":"http://127.0.0.1:8000/recrutalentos/static/img/avatar5.png"},
        {"nome":"Candidato 3","pontos":"12","foto":"http://127.0.0.1:8000/recrutalentos/static/img/avatar5.png"},
        {"nome":"Candidato 4","pontos":"17","foto":"http://127.0.0.1:8000/recrutalentos/static/img/avatar5.png"},
        {"nome":"Candidato 5","pontos":"20","foto":"http://127.0.0.1:8000/recrutalentos/static/img/avatar5.png"}],
        etapas = [
            {"data":"20 Maio 2019","hora":"10:00","acoes":[{"nome":"Ver","link":""}],"nome":"Candidatos","informacoes":"Ver Lista de candidatos escolhidos pelos sistema","icone":"fa-suitcase","cor":"blue"}
            ]
        )

def recrutalentos_pegaCurriculos(id):
    #TODO
    pass

def test():
    return dict()

def etapas():
    from datetime import datetime
    cor = ""
    prazo = request.vars.prazo or " "
    descricao = request.vars.descricao or " "
    hora = "".join([str(datetime.now().time().hour),":",str(datetime.now().time().minute)])
    if request.vars.tipo == 1 : 
        cor ='bg-blue'
    else: 
        cor ='bg-green'
    return "jQuery('#timeline').append('"+str(LI(SPAN(prazo,_class=cor),_class="time-label"))+str(LI(
        I(_class="fa fa-suitcase "+cor),
        DIV(
            SPAN(
                I(_class="fa fa-clock-o"),
                " "+hora,
                _class="time"
                ),
            H3(
                A("TIPO ETAPA",_href="#"),
                _class="timeline-header"
                )
            ,
            DIV(
                descricao,
                _class="timeline-body"
            ),
            DIV(
                A(
                    "Ver",
                    _href="#",
                    _class="btn btn-primary btn-xs"
                ),
                _class="timeline-footer"
            ),
            _class="timeline-item"
            ),
        ))+"');"
     