import os
import logging
import requests
from dotenv import load_dotenv
from supabase import create_client, Client
load_dotenv()

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Variáveis de ambiente
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")

# Headers reutilizados em todas as chamadas à Z-API
ZAPI_HEADERS = {
    "Client-Token": ZAPI_CLIENT_TOKEN,
    "Content-Type": "application/json"
}

# Validação das variáveis de ambiente
required_vars = {
    "SUPABASE_URL": SUPABASE_URL,
    "SUPABASE_KEY": SUPABASE_KEY,
    "ZAPI_INSTANCE_ID": ZAPI_INSTANCE_ID,
    "ZAPI_TOKEN": ZAPI_TOKEN,
    "ZAPI_CLIENT_TOKEN": ZAPI_CLIENT_TOKEN,
}
missing = [name for name, value in required_vars.items() if not value]
if missing:
    logger.error(f"Variáveis de ambiente faltando no .env: {', '.join(missing)}")
    raise SystemExit(1)


# Conecta ao Supabase
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def buscar_contatos(supabase: Client, limite: int = 3):
    """Busca até `limite` contatos cadastrados na tabela 'contatos'."""
    try:
        response = supabase.table("contatos").select("*").limit(limite).execute()
        contatos = response.data
        logger.info(f"{len(contatos)} contato(s) encontrado(s) no Supabase.")
        return contatos
    except Exception as e:
        logger.error(f"Erro ao buscar contatos no Supabase: {e}")
        return []


def enviar_mensagem_zapi(telefone: str, mensagem: str) -> bool:
    """Envia mensagem de texto via Z-API para o número informado."""
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"
    payload = {
        "phone": telefone,
        "message": mensagem
    }

    try:
        response = requests.post(url, json=payload, headers=ZAPI_HEADERS, timeout=15)
        logger.info(f"Resposta da Z-API ({response.status_code}): {response.text}")
        response.raise_for_status()
        logger.info(f"Mensagem enviada com sucesso para {telefone}.")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao enviar mensagem para {telefone}: {e}")
        return False


def main():
    logger.info("Iniciando processo de envio de mensagens.")

    supabase = get_supabase_client()
    contatos = buscar_contatos(supabase, limite=3)

    if not contatos:
        logger.warning("Nenhum contato encontrado. Encerrando.")
        return

    sucessos = 0
    falhas = 0

    for contato in contatos:
        nome_contato = contato.get("nome_contato", "Contato")
        telefone = contato.get("telefone")

        if not telefone:
            logger.warning(f"Contato '{nome_contato}' sem telefone cadastrado. Pulando.")
            falhas += 1
            continue

        mensagem = f"Olá, {nome_contato} tudo bem com você?"

        enviado = enviar_mensagem_zapi(telefone, mensagem)
        if enviado:
            sucessos += 1
        else:
            falhas += 1

    logger.info(f"Processo finalizado. Sucessos: {sucessos} | Falhas: {falhas}")


if __name__ == "__main__":
    main()