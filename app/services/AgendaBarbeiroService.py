from datetime import datetime, timedelta, time
from sqlalchemy.orm import Session
from app.models.AgendaBarbeiro import AgendaBarbeiro
from app.models.Servico import Servico
from app.models.Usuario import Usuario

def gerar_horarios_disponiveis(db: Session, barbeiro_id: int, data: datetime.date, duracao_minutos: int):
    """
    Retorna os horários disponíveis para um barbeiro em uma determinada data,
    considerando expediente, almoço e duração do serviço.
    """
    barbeiro = db.query(Usuario).filter(Usuario.idusuario == barbeiro_id).first()
    if not barbeiro:
        raise Exception("Barbeiro não encontrado")

    # Pega todos os agendamentos do barbeiro na data
    agendamentos = db.query(AgendaBarbeiro).filter(
        AgendaBarbeiro.barbeiro_id == barbeiro_id,
        AgendaBarbeiro.data == data
    ).order_by(AgendaBarbeiro.hora_inicio).all()

    # Horários do expediente
    horario_inicio = datetime.combine(data, barbeiro.inicio_expediente)
    horario_fim = datetime.combine(data, barbeiro.fim_expediente)
    almoco_inicio = datetime.combine(data, barbeiro.inicio_almoco)
    almoco_fim = datetime.combine(data, barbeiro.fim_almoco)

    horarios_disponiveis = []
    atual = horario_inicio

    for ag in agendamentos:
        inicio_ag = datetime.combine(data, ag.hora_inicio)
        fim_ag = datetime.combine(data, ag.hora_fim)

        # Pula horário de almoço
        if atual >= almoco_inicio and atual < almoco_fim:
            atual = almoco_fim

        # Intervalo livre antes do agendamento
        if atual + timedelta(minutes=duracao_minutos) <= inicio_ag:
            horarios_disponiveis.append(atual.time())

        atual = max(atual, fim_ag)

    # Últimos horários disponíveis após o último agendamento
    while atual + timedelta(minutes=duracao_minutos) <= horario_fim:
        # pula almoço se necessário
        if atual >= almoco_inicio and atual < almoco_fim:
            atual = almoco_fim
        if atual + timedelta(minutes=duracao_minutos) <= horario_fim:
            horarios_disponiveis.append(atual.time())
        atual += timedelta(minutes=duracao_minutos)

    # Converte os horários para string "HH:MM"
    horarios_disponiveis_str = [h.strftime("%H:%M") for h in horarios_disponiveis]

    return horarios_disponiveis_str
