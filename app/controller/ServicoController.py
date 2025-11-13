from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from app.schemas.ServicoSchema import ServicoCreate, ServicoResponse
from app.services.ServicoService import criar_servico, listar_servicos, obter_servico, deletar_servico, atualizar_servico
from app.core.database import get_db

router = APIRouter(
    prefix="/sericos",
    tags=["Serviços"]
)

# GET todos os serviços
@router.get("/")
def get_servicos(db: Session = Depends(get_db)):
    return listar_servicos(db)  

# GET serviço por ID
@router.get("/{servico_id}")
def get_servico(servico_id: int, db: Session = Depends(get_db)):
    return obter_servico(db, servico_id)    

# POST criar serviço
@router.post("/")
def post_servico(servico: ServicoCreate, db: Session = Depends(get_db)):
    return criar_servico(db, servico.nome, servico.duracao, servico.preco)      


# DELETE serviço
@router.delete("/{servico_id}")
def delete_servico(servico_id: int, db: Session = Depends(get_db)):
    return deletar_servico(db, servico_id)  

# PUT atualizar serviço
@router.put("/{servico_id}")
def put_servico(servico_id: int, servico: ServicoCreate, db: Session = Depends(get_db)):
    return atualizar_servico(db, servico_id, servico.nome, servico.duracao, servico.preco)  


