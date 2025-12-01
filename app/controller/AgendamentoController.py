from sqlite3 import Date
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, aliased
from datetime import date, datetime
from app.schemas.AgendamentoSchema import AgendamentoCreate, AgendamentoResponse, DisponibilidadeResponse
from app.services.AgendamentoService import criar_agendamento, obter_horarios_disponiveis
from app.core.database import get_db
from app.models.Agendamento import Agendamento
from app.models.Usuario import Usuario
from app.models.Servico import Servico

router = APIRouter(
    prefix="/agendamento",
    tags=["Agendamentos"]
)

@router.post("/agendamento/", response_model=AgendamentoResponse)
def post_agendamento(
    agendamento: AgendamentoCreate,
    db: Session = Depends(get_db)
):
    """
    Cria um novo agendamento.
    """
    return criar_agendamento(db, agendamento)

@router.get("/agendamento/disponibilidade/", response_model=DisponibilidadeResponse)
def get_horarios_disponiveis(
    barbeiro_id: int = Query(..., description="ID do barbeiro"),
    servico_id: int = Query(..., description="ID do serviço"),
    data: date = Query(..., description="Data desejada (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Retorna todos os horários disponíveis para um barbeiro e serviço em uma data específica.
    """
    return obter_horarios_disponiveis(db, barbeiro_id, servico_id, data)


@router.get("/agendamentos/{id_agendamento}")
def get_agendamento(id_agendamento: int, db: Session = Depends(get_db)):
    # Aliases para a mesma tabela Usuario
    Cliente = aliased(Usuario)
    Barbeiro = aliased(Usuario)

    agendamento = (
        db.query(
            Agendamento.idagendamento,
            Agendamento.data_hora_inicio,
            Agendamento.data_hora_fim,
            Agendamento.observacao,
            Agendamento.preco,
            Agendamento.status_id,
            Agendamento.cliente_id,
            Agendamento.barbeiro_id,
            Agendamento.servico_id,
            # Nomes relacionados
            Cliente.nome.label("nome_cliente"),
            Barbeiro.nome.label("nome_barbeiro"),
            Servico.nome.label("nome_servico")
        )
        .join(Cliente, Agendamento.cliente_id == Cliente.idusuario)
        .join(Barbeiro, Agendamento.barbeiro_id == Barbeiro.idusuario)
        .join(Servico, Agendamento.servico_id == Servico.idservicos)
        .filter(Agendamento.idagendamento == id_agendamento)
        .first()
    )

    if not agendamento:
        return {"error": "Agendamento não encontrado"}

    return {
        "id": agendamento.idagendamento,
        "data_hora_inicio": agendamento.data_hora_inicio,
        "data_hora_fim": agendamento.data_hora_fim,
        "observacao": agendamento.observacao,
        "preco": float(agendamento.preco),
        "status_id": agendamento.status_id,
        "cliente": {
            "id": agendamento.cliente_id,
            "nome": agendamento.nome_cliente
        },
        "barbeiro": {
            "id": agendamento.barbeiro_id,
            "nome": agendamento.nome_barbeiro
        },
        "servico": {
            "id": agendamento.servico_id,
            "nome": agendamento.nome_servico
        }
    }


@router.get("/barbeiro/agendamentos/")
def listar_agendamentos_barbeiro(
    barbeiro_id: int = Query(..., description="ID do barbeiro"),
    data: date = Query(..., description="Data desejada (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Lista todos os agendamentos do barbeiro em uma data específica.
    """
    from app.services.AgendamentoService import listar_agendamentos_barbeiro

    return listar_agendamentos_barbeiro(db, barbeiro_id, data)



@router.get("/cliente/agendamentos/")
def listar_agendamentos_clientes(
    cliente_id: int,
    data: str,
    db: Session = Depends(get_db)
):
    from datetime import datetime
    from sqlalchemy import func
    from sqlalchemy.orm import aliased

    # Converte a data
    try:
        data_formatada = datetime.strptime(data, "%Y-%m-%d").date()
    except:
        raise HTTPException(status_code=400, detail="Data inválida. Use YYYY-MM-DD.")

    Cliente = aliased(Usuario)
    Barbeiro = aliased(Usuario)

    resultados = (
        db.query(
            Agendamento.idagendamento.label("id"),
            Cliente.nome.label("cliente"),
            Servico.nome.label("servico"),
            Servico.duracao.label("duracao"),
            Agendamento.preco.label("preco"),
            Agendamento.data_hora_inicio,
            Agendamento.data_hora_fim,
            Agendamento.observacao
        )
        .join(Cliente, Agendamento.cliente_id == Cliente.idusuario)
        .join(Barbeiro, Agendamento.barbeiro_id == Barbeiro.idusuario)
        .join(Servico, Agendamento.servico_id == Servico.idservicos)
        .filter(
            Agendamento.cliente_id == cliente_id,
            func.date(Agendamento.data_hora_inicio) == data_formatada
        )
        .order_by(Agendamento.data_hora_inicio)
        .all()
    )

    resposta = []
    for r in resultados:
        resposta.append({
            "id": r.id,
            "cliente": r.cliente,
            "servico": r.servico,
            "duracao": r.duracao,
            "preco": float(r.preco),
            "data_hora_inicio": r.data_hora_inicio,
            "data_hora_fim": r.data_hora_fim,
            "observacao": r.observacao
        })

    return resposta

