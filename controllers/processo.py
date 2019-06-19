
import recrutalentos as RC

table = db.processo
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
        {'is_item_action': lambda item: True, 'url': lambda item: URL(request.controller,'dashboard', args=[item.id]), 'icon': 'cube'}
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
        Field("nome", 'string', label="nome"),
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
        id_vaga = db.vaga.insert(**db.vaga._filter_fields(form.vars))
        id_processo = db.processo.insert(etapa=1,idVaga=id_vaga,prazo = form.vars.prazo)
        vaga = db.vaga(id_vaga)
        RC.buscaCandidatos(vaga,id_processo)
        session.flash = "Vaga Adicionada com Sucesso"
        redirect(URL(request.controller, 'list'))
    elif form.errors:
        response.flash = 'Verifique as infromações inseridas e tente novamente'

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

def candidato():
    id_candidato = request.vars['id_candidato']
    id_processo = request.vars['id_processo']
    id_etapa =request.vars['id_etapa']

    curriculo = db.curriculo(id_candidato)
    candidato = dict(foto=URL(curriculo.foto),nome=curriculo.nome,data_nascimento=curriculo.data_nascimento)

    response.view_title = "Processo: #"+id_processo+" - Candidato : #"+str(id_candidato)
    return candidato
    
@auth.requires_membership('admin')
def dashboard():
    etapa_form = SQLFORM(db.etapa)

    processo = table(table.id == request.args(0))
    
    nome_processo = db.vaga(processo.idVaga).nome
    curriculos = db.processo_curriculo(db.processo_curriculo.id_processo == request.args(0)) or redirect(URL('index'))
    
    candidatos = []
    etapas = [  RC.parse_etapa(db.etapa(etapa),processo.id) for etapa in processo.etapas]
    
    for candidato in curriculos.candidatos:
        c = db.curriculo(candidato)
        candidatos.append({"nome": c.nome,"pontos":"10","foto":"http://127.0.0.1:8000/recrutalentos/static/img/avatar5.png"})
    
    

    response.view_title = "Processo : #"+request.args(0) + " Dashboard"
    return dict(nome_processo=nome_processo,candidatos=candidatos,etapas = etapas,etapas_form= etapa_form)

def etapa():
    processo = db.processo_curriculo(db.processo_curriculo.id_processo == request.vars['id_processo'])
    id_processo = request.vars['id_processo']
    id_etapa =request.vars['id_etapa']

    etapa = db.etapa(request.vars['id_etapa'])
    nome_etapa = etapa.titulo
    candidatos = []
    
    
    for candidato in processo.candidatos:
        c = db.curriculo(candidato)
        candidatos.append({"id": c.id,"nome": c.nome,"pontos":"10","foto":"http://127.0.0.1:8000/recrutalentos/static/img/avatar5.png"})
    
    response.view_title = "Processo : #"+str(processo.id)+ " "+nome_etapa
    return dict(candidatos=candidatos,id_processo = id_processo,id_etapa=id_etapa)

def etapas():
    from datetime import datetime



    if request.vars.acao == "1":
        resp = response.render("layout_modal.html", dict(
        modal_title = "Teste",
        modal_action = ["Fechar","Salvar"],
        modal_body = P("Teste")
        ))
        
        return "jQuery('#modal').append('"+str(resp)+"');"

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
     