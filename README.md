# Desafio b2bflow - Envio de Mensagens via Supabase + Z-API

Script em Python que lê contatos cadastrados no Supabase e envia uma mensagem personalizada via WhatsApp usando a Z-API.

## Setup da tabela (Supabase)

Crie uma tabela `contatos` com as colunas:
- `id` (int8, primary key, auto-increment)
- `nome_contato` (text)
- `telefone` (text) — formato: DDI + DDD + número, ex: 5511999999999
- `created_at` (timestamptz, default now())

## Variáveis de ambiente (.env)

## Crie um arquivo `.env` na raiz com:

SUPABASE_URL=
SUPABASE_KEY=
ZAPI_INSTANCE_ID=
ZAPI_TOKEN=
ZAPI_CLIENT_TOKEN=

## Como rodar

```bash
pip install -r requirements.txt
python main.py
```