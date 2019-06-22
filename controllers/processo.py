
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
    
    
    items = db().select(db.processo.ALL, db.vaga.ALL,left=db.vaga.on(db.processo.idVaga == db.vaga.id)).render()
    
    

    actions = [
        {'is_item_action': lambda item: True, 'url': lambda item: URL(request.controller, 'view', args=[item.processo.id]), 'icon': 'search'},
        {'is_item_action': lambda item: True, 'url': lambda item: URL('edit', args=[item.processo.id]), 'icon': 'pencil'},
        {'is_item_action': lambda item: True, 'url': lambda item: URL(request.controller,'dashboard', args=[item.processo.id]), 'icon': 'cube'}
    ]

    fields = [f for f in [db.processo.id,db.vaga.nome,db.processo.prazo]]


    response.view = "template/list.html" 
    return dict(
        item_name=table._singular,
        row_list=items,
        actions=actions,
        field_list=fields,
        announcement=announcement
    )

def buscar():
    processo = table(table.id == request.args(0))
    vaga = db.vaga(processo.idVaga)
    RC.buscaCandidatos(vaga,processo.id)


@auth.requires_login()
def create():

    def add_etapa1(vaga,id_processo):
        from datetime import datetime
        data = datetime.now().date()
        
        
        vars = dict(tipo = 4, 
                    titulo = "Criar Vaga",
                    informacoes = RC.get_descricao_vaga(vaga),
                    data = data,
                    hora = "".join([str(datetime.now().time().hour),":",str(datetime.now().time().minute)]),
                    acoes = dict(link=URL("vaga",args=vaga.id),nome="Ver Vaga")
                    )
        processo = db.processo(id_processo)
        id_etapa = db.etapa.insert(**db.etapa._filter_fields(vars))
        if processo.etapas:
            processo.update_record(etapas=processo.etapas+[id_etapa])
        else:
            processo.update_record(etapas=[id_etapa])
    def add_etapa2(vaga,id_processo):
        from datetime import datetime
        data = datetime.now().date()
        
        
        vars = dict(tipo = 5, 
                    titulo = "Contato",
                    informacoes = "Entrar em contato com os candidatos",
                    data = data,
                    hora = "".join([str(datetime.now().time().hour),":",str(datetime.now().time().minute)])
                    
                    )
        processo = db.processo(id_processo)
        id_etapa = db.etapa.insert(**db.etapa._filter_fields(vars))
        if processo.etapas:
            processo.update_record(etapas=processo.etapas+[id_etapa])
        else:
            processo.update_record(etapas=[id_etapa])

    form = SQLFORM.factory(
        Field("nome", 'string', label="Nome da vaga"),
        Field("form_academica","integer",label="Formação Acadêmica",notnull=True,requires = IS_IN_SET(((1,"Superior"),(2,"Técnico"),(3,"Médio"),(4,"Fundamental"),(5,"Não se aplica")))),
        Field('experiencia', 'integer', label='Experiencia Profissional (em meses)'),
        Field('localTrabalho', 'string', label='Local de Trabalho'),
        Field('horario_inicio', 'time', label='Horario de Entrada'),
        Field('horario_fim', 'time', label='Horario de Saida'),
        Field('salarioOferecido', 'float', label='Salario Oferecido'),
        Field('qtdVagas', 'integer', label='Quantidade de Vagas'),
        Field('qtdCandidatos', 'integer', label='Quantidade de Candidatos'),
        Field('responsavelVaga', 'string', label='Responsável pela Vaga'),
        Field('prazo', 'date', label='Prazo para o Processo',requires = IS_DATE(format=('%m/%d/%Y'))),
        _id="createform"
    )
    
    form.custom.widget.experiencia.update(_placeholder="em Meses")
    if form.process().accepted:
        id_vaga = db.vaga.insert(**db.vaga._filter_fields(form.vars))
        id_processo = db.processo.insert(etapa=1,idVaga=id_vaga,prazo = form.vars.prazo)
        vaga = db.vaga(id_vaga)
        add_etapa1(vaga,id_processo)
        RC.buscaCandidatos(vaga,id_processo)
        add_etapa2(vaga,id_processo)
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
    id_etapa =request.vars['id_etapa'] or None

    curriculo = db.curriculo(id_candidato)
    formacao = ""
    formacoes = [db.formacao_academica(db.formacao_academica.id_curriculo == id_candidato)]
    print(formacoes)
    experiencias = []
    conhecimentos = []
    observacoes = []
    candidato = dict(
        foto="http://127.0.0.1:8000/recrutalentos/static/img/avatar5.png",
        nome=curriculo.nome,
        data_nascimento=curriculo.data_nascimento,
        formacoes=formacoes,
        formacao = formacao,
        experiencias= experiencias,
        conhecimentos= conhecimentos,
        observacoes=observacoes,
        objetivo = curriculo.objetivo_setor,
        endereco = " ".join(curriculo.endereco))

    response.view_title = "Processo: #"+id_processo+" - Candidato : #"+str(id_candidato)
    return candidato
    
@auth.requires_membership('admin')
def dashboard():

    def get_form_modals():        
        from datetime import datetime
        etapas_form = SQLFORM.factory(
            Field("titulo", 'string', label="Nome da etapa"),
            Field("tipo","integer",label="Tipo da etapa",notnull=True,requires = IS_IN_SET(((1,"Entrevista"),(2,"Teste"),(3,"Dinâmica")))),        
            Field('data', 'date', label='Data da etapa',requires = IS_DATE(format=('%m/%d/%Y'))),
            Field('informacoes', 'text', label='Descrição da etapa'),
            buttons = [BUTTON('Salvar', _type="submit")],
            hidden=dict(id_processo=request.args(0)),
            _action=URL('etapas'))

        etapas = dict(form=etapas_form,nome="Adicionar Etapa")
        return [etapas]
    
    
    

    processo = table(table.id == request.args(0))
    
    nome_processo = db.vaga(processo.idVaga).nome
    curriculos = db.processo_curriculo(db.processo_curriculo.id_processo == request.args(0)) or redirect(URL('index'))
    
    candidatos = []
    if processo.etapas:
        etapas = [  RC.parse_etapa(db.etapa(etapa),processo.id) for etapa in processo.etapas if etapa]
    else:
        etapas = []
    
    for candidato in curriculos.candidatos:
        c = db.curriculo(candidato)
        candidatos.append({"id": c.id,"nome": c.nome,"pontos":"10","foto":"http://127.0.0.1:8000/recrutalentos/static/img/avatar5.png"})
    
    

    response.view_title = "Processo : #"+request.args(0) + " Dashboard"
    return dict(nome_processo=nome_processo,candidatos=candidatos,etapas = etapas,modal_form= get_form_modals(),id_processo=processo.id)

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
    
    if request.ajax:
        data = datetime.strptime(request.vars.data, '%m/%d/%Y')
        request.vars.data = data
        
        vars = dict(tipo = int(request.vars.tipo), 
                    titulo = request.vars.titulo,
                    informacoes = request.vars.informacoes,
                    data = request.vars.data,
                    hora = "".join([str(datetime.now().time().hour),":",str(datetime.now().time().minute)])
                    
                    )
        processo = db.processo(request.vars.id_processo)
        id_etapa = db.etapa.insert(**db.etapa._filter_fields(vars))
        if processo.etapas:
            processo.update_record(etapas=processo.etapas+[id_etapa])
        else:
            processo.update_record(etapas=[id_etapa])
        return RC.parse_etapa(db.etapa(id_etapa),request.vars.id_processo,html=True)
     