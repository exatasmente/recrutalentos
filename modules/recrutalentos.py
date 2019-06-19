
# -*- coding: utf-8 -*-
from gluon import *
#Recrutalentos, módulo responsável por manipular a persistência dos processos de recrutamento de seleção
def buscaCandidatos(vaga,id_processo):

    print(id_processo)

    formacao = vaga.form_academica
    experiencia = vaga.experiencia
    sel =[]
    curriculos = current.db().select(current.db.curriculo.ALL)
    for curriculo in curriculos:
        form = current.db.formacao_academica(current.db.formacao_academica.id_curriculo == curriculo.id)
        if form.tipo == formacao:
            print(curriculo.id)
            sel.append(curriculo.id)
            
    
    current.db.processo_curriculo.insert(id_processo=id_processo,candidatos= sel)
    
def parse_etapa(etapa,id_processo):
        
        cores = {"1":"red",2:"blue",3:"green",4:"yellow"}
        icones= {"1":"fa-address-book",2:"fa-flag-o",3:"green",4:"yellow"}
        return dict(
                id= etapa.id,
                id_processo = id_processo,
                hora=str(etapa.hora),
                cor= cores[etapa.tipo],
                nome = etapa.titulo,
                data = str(etapa.data),
                icone = icones[etapa.tipo],
                informacoes = ""
                )