from pydantic import BaseModel
from typing import Optional

# Define a estrutura de dados esperada para um item de pagamento
class ItemPagamento(BaseModel):
    title: str
    description: Optional[str] = None
    quantity: int = 1
    unit_price: float
    
# Estrutura para o request de criação de preferência
class PreferenciaRequest(BaseModel):
    item: ItemPagamento
    agendamento_id: int # Para rastrear qual agendamento está sendo pago