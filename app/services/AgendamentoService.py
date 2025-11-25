from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from app.models.Agendamento import Agendamento
from app.models.Usuario import Usuario
from app.models.Servico import Servico
from app.models.AgendaBarbeiro import AgendaBarbeiro  # se você tiver esse model

def criar_agendamento(db: Session, agendamento_data):
    # Verifica se cliente existe
    cliente = db.query(Usuario).filter(Usuario.idusuario == agendamento_data.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Verifica se barbeiro existe
    barbeiro = db.query(Usuario).filter(Usuario.idusuario == agendamento_data.barbeiro_id).first()
    if not barbeiro or not barbeiro.is_barbeiro:
        raise HTTPException(status_code=404, detail="Barbeiro não encontrado")

    # Verifica se serviço existe
    servico = db.query(Servico).filter(Servico.idservicos == agendamento_data.servico_id).first()
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    # Converte data + hora
    data_hora_inicio = datetime.combine(agendamento_data.data, agendamento_data.hora_inicio)
    data_hora_fim = datetime.combine(agendamento_data.data, agendamento_data.hora_fim)

    # Valida se o horário está dentro da agenda do barbeiro
    agenda = db.query(AgendaBarbeiro).filter(AgendaBarbeiro.usuario_id == agendamento_data.barbeiro_id).first()
    if agenda:
        if not (agenda.inicio_expediente <= agendamento_data.hora_inicio <= agenda.fim_expediente):
            raise HTTPException(status_code=400, detail="Horário fora do expediente do barbeiro")
        if not (agenda.inicio_expediente <= agendamento_data.hora_fim <= agenda.fim_expediente):
            raise HTTPException(status_code=400, detail="Horário fora do expediente do barbeiro")

    # Checa conflitos
    conflito = db.query(Agendamento).filter(
        Agendamento.barbeiro_id == agendamento_data.barbeiro_id,
        Agendamento.data_hora_inicio < data_hora_fim,
        Agendamento.data_hora_fim > data_hora_inicio
    ).first()

    if conflito:
        raise HTTPException(status_code=400, detail="Horário já agendado para este barbeiro")

    novo_agendamento = Agendamento(
        cliente_id=agendamento_data.cliente_id,
        barbeiro_id=agendamento_data.barbeiro_id,
        servico_id=agendamento_data.servico_id,
        data_hora_inicio=data_hora_inicio,
        data_hora_fim=data_hora_fim,
        observacao=agendamento_data.observacao
)

    db.add(novo_agendamento)
    db.commit()
    db.refresh(novo_agendamento)
    return novo_agendamento
