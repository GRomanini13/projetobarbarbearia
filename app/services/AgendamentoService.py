from sqlalchemy.orm import Session
from datetime import datetime, timedelta, time, date
from typing import List
from fastapi import HTTPException
from app.models.Agendamento import Agendamento
from app.models.Usuario import Usuario
from app.models.Servico import Servico

def criar_agendamento(db: Session, agendamento_data):
    # Verifica se cliente existe
    cliente = db.query(Usuario).filter(Usuario.idusuario == agendamento_data.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Verifica se barbeiro existe e é realmente barbeiro
    barbeiro = db.query(Usuario).filter(Usuario.idusuario == agendamento_data.barbeiro_id).first()
    if not barbeiro:
        raise HTTPException(status_code=404, detail="Barbeiro não encontrado")
    if not barbeiro.is_barbeiro:
        raise HTTPException(status_code=400, detail="Usuário selecionado não é um barbeiro")
    
    # Verifica se serviço existe
    servico = db.query(Servico).filter(Servico.idservicos == agendamento_data.servico_id).first()
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    # Converte data + hora para datetime
    data_hora_inicio = datetime.combine(agendamento_data.data, agendamento_data.hora_inicio)
    data_hora_fim = datetime.combine(agendamento_data.data, agendamento_data.hora_fim)
    
    # VALIDAÇÃO 1: Horário de término deve ser maior que horário de início
    if data_hora_fim <= data_hora_inicio:
        raise HTTPException(
            status_code=400, 
            detail="Horário de término deve ser maior que horário de início"
        )
    
    # VALIDAÇÃO 2: Valida se o horário está dentro do expediente do barbeiro
    if barbeiro.inicio_expediente and barbeiro.fim_expediente:
        if not (barbeiro.inicio_expediente <= agendamento_data.hora_inicio <= barbeiro.fim_expediente):
            raise HTTPException(
                status_code=400, 
                detail=f"Horário fora do expediente. Barbeiro atende das {barbeiro.inicio_expediente} às {barbeiro.fim_expediente}"
            )
        if not (barbeiro.inicio_expediente <= agendamento_data.hora_fim <= barbeiro.fim_expediente):
            raise HTTPException(
                status_code=400, 
                detail=f"Horário fora do expediente. Barbeiro atende das {barbeiro.inicio_expediente} às {barbeiro.fim_expediente}"
            )
    
    # VALIDAÇÃO 3: Valida conflito com horário de almoço (se existir)
    if barbeiro.inicio_almoco and barbeiro.fim_almoco:
        # Verifica se o agendamento sobrepõe o horário de almoço
        if (agendamento_data.hora_inicio < barbeiro.fim_almoco and 
            agendamento_data.hora_fim > barbeiro.inicio_almoco):
            raise HTTPException(
                status_code=400, 
                detail=f"Horário conflita com intervalo de almoço ({barbeiro.inicio_almoco} - {barbeiro.fim_almoco})"
            )
    
    # VALIDAÇÃO 4: Checa conflitos de horário com outros agendamentos
    # Um agendamento conflita quando há qualquer sobreposição de horários
    conflito = db.query(Agendamento).filter(
        Agendamento.barbeiro_id == agendamento_data.barbeiro_id,
        Agendamento.status_id != 3,  # Ignora agendamentos cancelados (assumindo que 3 = cancelado)
        Agendamento.data_hora_inicio < data_hora_fim,
        Agendamento.data_hora_fim > data_hora_inicio
    ).first()
    
    if conflito:
        raise HTTPException(
            status_code=400, 
            detail=f"Horário indisponível. Conflita com agendamento #{conflito.idagendamento} ({conflito.data_hora_inicio.strftime('%H:%M')} - {conflito.data_hora_fim.strftime('%H:%M')})"
        )
    
    # VALIDAÇÃO 5 (OPCIONAL): Verifica duração mínima do serviço
    # Se o serviço tiver uma duração esperada, você pode validar aqui
    # duracao_agendamento = (data_hora_fim - data_hora_inicio).total_seconds() / 60
    # if hasattr(servico, 'duracao_minutos') and duracao_agendamento < servico.duracao_minutos:
    #     raise HTTPException(
    #         status_code=400,
    #         detail=f"Duração mínima do serviço é {servico.duracao_minutos} minutos"
    #     )
    
    # Cria o novo agendamento
    novo_agendamento = Agendamento(
        cliente_id=agendamento_data.cliente_id,
        barbeiro_id=agendamento_data.barbeiro_id,
        servico_id=agendamento_data.servico_id,
        data_hora_inicio=data_hora_inicio,
        data_hora_fim=data_hora_fim,
        observacao=agendamento_data.observacao,
        status_id=1  # 1 = agendado/pendente
    )
    
    db.add(novo_agendamento)
    db.commit()
    db.refresh(novo_agendamento)
    
    return novo_agendamento


def obter_horarios_disponiveis(
    db: Session, 
    barbeiro_id: int, 
    servico_id: int, 
    data_desejada: date
):
    # Verifica se barbeiro existe
    barbeiro = db.query(Usuario).filter(Usuario.idusuario == barbeiro_id).first()
    if not barbeiro or not barbeiro.is_barbeiro:
        raise HTTPException(status_code=404, detail="Barbeiro não encontrado")
    
    # Verifica se serviço existe
    servico = db.query(Servico).filter(Servico.idservicos == servico_id).first()
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    # Verifica se o serviço tem duração definida
    if not hasattr(servico, 'duracao') or not servico.duracao:
        raise HTTPException(
            status_code=400, 
            detail="Serviço não possui duração definida"
        )
    
    # Pega os horários de expediente do barbeiro
    if not barbeiro.inicio_expediente or not barbeiro.fim_expediente:
        raise HTTPException(
            status_code=400, 
            detail="Barbeiro não possui horário de expediente configurado"
        )
    
    # Busca todos os agendamentos do barbeiro naquele dia
    inicio_dia = datetime.combine(data_desejada, time.min)
    fim_dia = datetime.combine(data_desejada, time.max)
    
    agendamentos_dia = db.query(Agendamento).filter(
        Agendamento.barbeiro_id == barbeiro_id,
        Agendamento.status_id != 3,  # Ignora cancelados
        Agendamento.data_hora_inicio >= inicio_dia,
        Agendamento.data_hora_inicio <= fim_dia
    ).all()
    
    # Gera todos os slots possíveis
    horarios_disponiveis = []
    duracao = timedelta(minutes=servico.duracao)  # ← MUDOU AQUI
    
    # Converte time para datetime para facilitar cálculos
    hora_atual = datetime.combine(data_desejada, barbeiro.inicio_expediente)
    hora_fim_expediente = datetime.combine(data_desejada, barbeiro.fim_expediente)
    
    # Horário de almoço (se existir)
    almoco_inicio = None
    almoco_fim = None
    if barbeiro.inicio_almoco and barbeiro.fim_almoco:
        almoco_inicio = datetime.combine(data_desejada, barbeiro.inicio_almoco)
        almoco_fim = datetime.combine(data_desejada, barbeiro.fim_almoco)
    
    # Percorre todos os slots possíveis
    while hora_atual + duracao <= hora_fim_expediente:
        hora_fim_slot = hora_atual + duracao
        slot_disponivel = True
        
        # Verifica se está no horário de almoço
        if almoco_inicio and almoco_fim:
            if hora_atual < almoco_fim and hora_fim_slot > almoco_inicio:
                slot_disponivel = False
        
        # Verifica se conflita com algum agendamento existente
        if slot_disponivel:
            for agendamento in agendamentos_dia:
                if (hora_atual < agendamento.data_hora_fim and 
                    hora_fim_slot > agendamento.data_hora_inicio):
                    slot_disponivel = False
                    break
        
        # Se disponível, adiciona na lista
        if slot_disponivel:
            horarios_disponiveis.append({
                "hora_inicio": hora_atual.time(),
                "hora_fim": hora_fim_slot.time()
            })
        
        # Avança para o próximo slot
        hora_atual += duracao
    
    return {
        "barbeiro_id": barbeiro.idusuario,
        "barbeiro_nome": barbeiro.nome,
        "servico_id": servico.idservicos,
        "servico_nome": servico.nome if hasattr(servico, 'nome') else "Serviço",
        "duracao_minutos": servico.duracao,  # ← MUDOU AQUI
        "data": data_desejada,
        "horarios_disponiveis": horarios_disponiveis
    }