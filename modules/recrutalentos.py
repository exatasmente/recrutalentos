
# -*- coding: utf-8 -*-
from gluon import *
#Recrutalentos, módulo responsável por manipular a persistência dos processos de recrutamento de seleção
def buscaCandidatos(vaga,id_processo):
    formacao = vaga.form_academica
    experiencia = vaga.experiencia
    sel =[]
    pc = current.db.processo_curriculo(current.db.processo_curriculo.id_processo == id_processo)
    curriculos = current.db().select(current.db.curriculo.ALL)
    for curriculo in curriculos:
        formacao = current.db.formacao_academica(current.db.formacao_academica.id_curriculo == curriculo.id)
        experiencia = current.db.experiencia(current.db.experiencia.id_curriculo == curriculo.id)
        if vaga.nome.lower() in experiencia.cargo.lower():
            print(curriculo.id)
            sel.append(curriculo.id)
        elif formacao['tipo'] == formacao:
        
            sel.append(curriculo.id)
            
        
            
        
    
    pc.update_record(candidatos= sel)
    
def parse_etapa(etapa,id_processo,html=False):
        etapa.tipo = int(etapa.tipo)
        cores = {1:"blue",2:"red",3:"green",4:"yellow",5:"danger"}
        icones= {1:"fa-flag-o",2:"fa-flag-o",3:"green",4:"yellow",5:"danger"}

        if html:
                return "jQuery('#timeline').append('"+str(LI(SPAN( str(etapa.data),_class=cores[etapa.tipo]),_class="time-label"))+str(LI(
        I(_class="fa "+icones[etapa.tipo]+" bg-"+cores[etapa.tipo]),
        DIV(
            SPAN(
                I(_class="fa fa-clock-o"),
                " "+str(etapa.hora),
                _class="time"
                ),
            H3(
                A(etapa.titulo,_href="#"),
                _class="timeline-header"
                )
            ,
            DIV(
                etapa.informacoes,
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
        else:
            return dict(
                id= etapa.id,
                id_processo = id_processo,
                hora=str(etapa.hora),
                cor= cores[etapa.tipo],
                nome = etapa.titulo,
                data = str(etapa.data),
                icone = icones[etapa.tipo],
                informacoes = etapa.informacoes
                )
def get_descricao_vaga(vaga):
        return "Desicrição"