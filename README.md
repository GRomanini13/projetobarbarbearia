CRUD Barbearia

Projeto focado no trabalho da disciplina de “Desenvolvimento de Sistemas Web I”.
Este trabalho tem como objetivo criar um CRUD completo e funcional, visando melhorias e o lançamento de um app/plataforma para produção.

Pré-requisitos
Antes de iniciar, certifique-se de ter instalado:
    • Python 3.10 ou superior

    • Git

    • Virtualenv

    • Banco de dados (ex: PostgreSQL, MySQL ou SQLite)

Clonando o repositório:

git clone <URL_DO_REPOSITORIO>
cd <NOME_DO_PROJETO>

Criando e ativando o ambiente virtual

No Linux/macOS
# Criar o ambiente virtual
python3 -m venv venv

# Ativar o ambiente virtual
source venv/bin/activate
No Windows (PowerShell)
# Criar o ambiente virtual
python -m venv venv

# Ativar o ambiente virtual
.\venv\Scripts\Activate.ps1
Dica: Sempre ative o ambiente virtual ao iniciar uma nova sessão de terminal antes de rodar o projeto.

Instalando dependências

Com o ambiente virtual ativo, rode:
pip install -r requirements.txt
Para gerar um requirements.txt atualizado com todas as dependências instaladas:
pip freeze > requirements.txt

Configurando variáveis de ambiente
Crie um arquivo .env na raiz do projeto com suas configurações. Exemplo:
DATABASE_URL=postgresql://usuario:senha@localhost:5432/meubanco
SECRET_KEY=minha_chave_secreta
Observação: Para informações detalhadas de conexão com o banco de dados, entre em contato.

Rodando o projeto
Com o ambiente virtual ativo:

uvicorn app.main:app --reload
    • Acesse a API em: http://127.0.0.1:8000
    • A documentação automática está disponível em: http://127.0.0.1:8000/docs

Boas práticas de Git
    • Se atente para realizar commits nas branches corretas.
    • Use mensagens claras e descritivas ao fazer commit.
