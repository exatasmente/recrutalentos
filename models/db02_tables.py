# -*- coding: utf-8 -*-

MetaDados = db.define_table("meta_dados",
Field("chave","string",notnull=True),
Field("valor","string",notnull=True)
)
# in sql SELECT valor FROM metadados where chave = "<chave>"

Etapa = db.define_table("etapa",
Field('data','date',label="Data da etapa",requires = IS_DATE(format=('%m/%d/%Y'))),
Field('hora','time'),
Field('informacoes','string',label="Informações"),
Field('titulo','string'),
Field("tipo","integer",label="tipo",notnull=True,requires = IS_IN_SET((1,2,3,4))),
)



Curriculo = db.define_table('curriculo',
Field('nome', 'string', label='Nome', notnull=True),
Field('cpf', 'string', label='CPF', notnull=True, unique=True),
Field('contato', 'list:string', label='Contato', notnull=True),
Field('endereco', 'list:string', label='Endereço'),
Field('foto', 'upload', label='Foto'),
Field('data_nascimento', 'date', label='Data de Nascimento', requires = IS_DATE(format=('%m/%d/%Y'))),
Field('objetivo_setor', 'string', label='Cargo')
)

Form_academica = db.define_table("formacao_academica",
Field("instituicao","string",label="Instituição",notnull=True),
Field("tipo","integer",label="Formação",notnull=True,requires = IS_IN_SET((1,2,3,4,5))),
Field("curso","string",label="Curso",default="Não Se Aplica"),
Field("situacao","integer",label="Situação",notnull=True, requires = IS_IN_SET((1,2,3))),
Field("ano_inicio","date",label="Ano de Inicio",notnull=True,requires = IS_DATE(format=('%m/%d/%Y'))),
Field("ano_conclusao","date",label="Ano de Conclusão",notnull=True,requires = IS_DATE(format=('%m/%d/%Y'))),
Field("id_curriculo","reference curriculo")
)

Experiencia = db.define_table("experiencia",
Field("empresa","string",label="Nome da Empresa",notnull=True),
Field("cargo","string",label="Cargo na Empresa",notnull=True),
Field("duracao","integer",label="Periodo (em meses)",notnull=True),
Field("id_curriculo","reference curriculo")
)


Vaga = db.define_table('vaga',
Field('nome', 'string', label='Nome'),
Field("form_academica","integer",label="Formação Acadêmica",notnull=True,requires = IS_IN_SET((1,2,3,4,5))),
Field('experiencia', 'integer', label='Experiencia Profissional (em Meses)'),
Field('localTrabalho', 'string', label='Local de Trabalho'),
Field('horario_inicio', 'time', label='Horario de Entrada'),
Field('horario_fim', 'time', label='Horario de Saida'),
Field('salarioOferecido', 'float', label='Salario Oferecido'),
Field('qtdVagas', 'integer', label='Quantidade de Vagas'),
Field('qtdCandidatos', 'integer', label='Quantidade de Candidatos'),
Field('responsavelVaga', 'string', label='Responsável pela Vaga')
)


Processo = db.define_table('processo',
Field('etapas', 'list:reference etapa'),
Field('idVaga', 'reference vaga'),
Field('prazo', 'date')
)



Entrevista = db.define_table('entrevista',
Field('obs_gerais', 'json', label='Observações gerais'),
Field('id_processo', 'reference processo')
)

Dinamica = db.define_table('dinamica',
Field('nome', 'string', label='Nome'),
Field('descricao', 'string', label='Descrição'),
Field('tipo', 'boolean', label='Tipo de Dinamica'),
Field('obs_gerais', 'json', label='Observações gerais'),
Field('id_processo', 'reference processo')
)

Teste = db.define_table('teste',
Field('nome', 'string', label='Nome'),
Field('descricao', 'string', label='Contato'),
Field('tipo', 'boolean', label='Tipo de Dinamica'),
Field('obs_gerais', 'json', label='Observações gerais'),
Field('id_processo', 'reference processo')
)



ProcessoCurriculo = db.define_table('processo_curriculo',
Field('candidatos', 'list:reference curriculo'),
Field('id_processo', 'reference processo')
)

