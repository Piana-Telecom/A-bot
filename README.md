# A-bot: Integração com Aliance

Este projeto é uma aplicação Streamlit que se conecta a um banco de dados SQL Server via ODBC, com suporte para execução local e via Docker.

---

## ⚙️ Requisitos

- Python 3.10+
- `pip` (gerenciador de pacotes)
- Driver ODBC 18 para SQL Server
- [Opcional] Docker instalado

---

## 📦 Instalação

Clone o repositório e instale as dependências:

```bash
pip install -r requirements.txt
```

---

## 🔐 Configuração do `.env`

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
ODBC_DRIVER=ODBC Driver 18 for SQL Server
ODBC_SERVER=192.168.x.x
ODBC_DATABASE=NomeDoBanco
ODBC_UID=usuario
ODBC_PWD=senha
ODBC_ENCRYPT=no
ODBC_TRUSTCERT=yes
```

---

## ▶️ Executar localmente
__É necessário ter instalado e configurado ODBC Data Sources__

Rode a aplicação Streamlit dentro da pasta `src`:

```bash
streamlit run src/app.py
```

Acesse no navegador: [http://localhost:8501](http://localhost:8501)

---

## 🐳 Rodar com Docker

### Build da imagem:

```bash
docker build -t abot .
```

### Executar o container:

```bash
docker run -p 8501:8501 --env-file .env abot
```

A aplicação estará acessível em [http://localhost:8501](http://localhost:8501)

---

## 📁 Estrutura do projeto

```
.
├── .env
├── Dockerfile
├── requirements.txt
├── src/
│   ├── app.py
│   ├── backend/
│   │   └── db.py
│   └── components/
│       ├── calendar.py
│       └── spreadsheet.py
```

---

## ✅ Funcionalidades

- Conexão com SQL Server via ODBC
- Filtro por datas com calendário customizado
- Exportação de planilha Excel formatada com base nos dados
- Interface visual com Streamlit

---

