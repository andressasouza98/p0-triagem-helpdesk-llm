"""
Módulo cliente HTTP para comunicação REST com a API Google Gemini.
Responsável pelo carregamento de variáveis, estruturação de chamadas,
resiliência operacional, telemetria (LGPD) e inspeção de finishReason.
"""

import json
import logging
import os

from pathlib import Path
import time
from typing import Any, Dict
from dotenv import load_dotenv
import requests


# =====================================================================
# CONFIGURAÇÃO DE LOGGING ESTRUTURADO (LGPD / ZERO PII)
# =====================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

logger = logging.getLogger("helpdesk_llm_client")
logger.setLevel(logging.INFO)

# Evita duplicar handlers se o módulo for recarregado
if not logger.handlers:
    file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# Garante que os logs NÃO subam para a tela da CLI (console limpo)
logger.propagate = False


def carregar_configuracoes() -> Dict[str, Any]:
    """
    Carrega e valida defensivamente as configurações do arquivo .env.
    """
    load_dotenv(override=True)

    api_key = os.getenv("LLM_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "Chave de API ausente. Defina a variável 'LLM_API_KEY' no arquivo .env."
        )

    model_name = os.getenv("LLM_MODEL_NAME", "gemini-3.5-flash-lite").strip()
    api_version = os.getenv("LLM_API_VERSION", "v1beta").strip()


    try:
        max_tokens = int(os.getenv("LLM_MAX_TOKENS", "500"))
        temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
        timeout = float(os.getenv("LLM_TIMEOUT", "30"))
    except ValueError:
        raise ValueError("Parâmetros numéricos no arquivo .env inválidos.")

    return {
        "api_key": api_key,
        "model_name": model_name,
        "api_version": api_version,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "timeout": timeout,
    }


def extrair_resposta(response_data: dict) -> str:
    """
    Extrai o texto e inspeciona granularmente o finishReason retornado pela LLM.
    """
    candidates = response_data.get("candidates", [])
    if not candidates or not isinstance(candidates, list):
        raise ValueError("Resposta da API sem candidatos válidos.")

    primeiro_candidato = candidates[0]
    finish_reason = primeiro_candidato.get("finishReason", "UNKNOWN")

    # Tratamento de bloqueio por filtros de segurança
    if finish_reason in ["SAFETY", "BLOCKLIST", "PROHIBITED_CONTENT"]:
        return (
            "[BLOQUEIO DE SEGURANÇA]: A resposta foi interrompida pelos filtros "
            "de moderação da IA."
        )

    content = primeiro_candidato.get("content", {})
    parts = content.get("parts", [])
    if not parts or not isinstance(parts, list):
        raise ValueError("Conteúdo da resposta retornado vazio ou inválido.")

    texto_gerado = parts[0].get("text", "").strip()

    # Alerta de truncamento caso o limite de tokens tenha sido atingido
    if finish_reason in ["MAX_TOKENS", "length"]:
        texto_gerado += (
            "\n\n[ALERTA DE TRUNCAMENTO]: O limite de tokens configurado foi atingido. "
            "A resposta pode estar incompleta.\n"
            "Sugestão técnica: Aumente o valor de 'LLM_MAX_TOKENS' no arquivo .env."
        )
    elif finish_reason not in ["STOP", "UNKNOWN"]:
        texto_gerado += f"\n\n[AVISO]: Finalização anormal da resposta ({finish_reason})."

    return texto_gerado


def enviar_prompt_llm(prompt: str) -> str:
    """
    Envia o prompt para a API do Gemini via REST, registrando telemetria
    estritamente técnica (LGPD / Zero PII) em logs/app.log.
    """
    config = carregar_configuracoes()

    url = (
        f"https://generativelanguage.googleapis.com/{config['api_version']}/"
        f"models/{config['model_name']}:generateContent"
    )

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": config["api_key"]
    }

    payload = {

        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": config["max_tokens"],
            "temperature": config["temperature"]
        }

    }

    prompt_char_len = len(prompt)
    inicio = time.perf_counter()

    try:

        response = requests.post(
            url,
            headers=headers,

            json=payload,
            
            timeout=config["timeout"]
        )
        latencia = round(time.perf_counter() - inicio, 3)

        # Interceptação de códigos HTTP específicos
        if response.status_code == 401 or response.status_code == 403:
            logger.error(
                f"status={response.status_code} | latency={latencia}s | "
                f"prompt_chars={prompt_char_len} | model={config['model_name']} | error=AuthError"
            )
            return (
                "[ERRO DE AUTENTICAÇÃO]: Chave de API inválida ou sem permissão. "
                "Verifique a variável 'LLM_API_KEY' no arquivo .env."
            )

        if response.status_code == 429:
            logger.warning(
                f"status={response.status_code} | latency={latencia}s | "
                f"prompt_chars={prompt_char_len} | model={config['model_name']} | error=RateLimit"
            )
            return (
                "[LIMITE DE REQUISIÇÕES]: Quota de uso excedida na API. "
                "Aguarde alguns instantes antes de enviar um novo relato."
            )

        if response.status_code >= 500:
            logger.error(
                f"status={response.status_code} | latency={latencia}s | "
                f"prompt_chars={prompt_char_len} | model={config['model_name']} | error=ServerError"
            )
            return (
                f"[ERRO DO SERVIDOR]: Os servidores do Gemini retornaram status {response.status_code}. "
                "Tente novamente em breve."
            )

        response.raise_for_status()

        # Decodificação do payload
        data = response.json()
        candidatos = data.get("candidates", [{}])
        finish_reason = candidatos[0].get("finishReason", "UNKNOWN") if candidatos else "UNKNOWN"

        # Telemetria de Sucesso (Zero PII: sem texto de relato ou resposta)
        logger.info(
            f"status={response.status_code} | latency={latencia}s | "
            f"prompt_chars={prompt_char_len} | model={config['model_name']} | finish_reason={finish_reason}"
        )

        return extrair_resposta(data)

    except requests.exceptions.Timeout:
        latencia = round(time.perf_counter() - inicio, 3)
        logger.error(
            f"status=TIMEOUT | latency={latencia}s | "
            f"prompt_chars={prompt_char_len} | model={config['model_name']} | error=Timeout"
        )
        return (
            f"[TEMPO LIMITE EXCEDIDO]: A requisição ultrapassou o limite de {config['timeout']}s. "
            "Verifique a sua conexão com a internet."
        )
    

    except requests.exceptions.ConnectionError:
        latencia = round(time.perf_counter() - inicio, 3)
        logger.error(
            f"status=CONNECTION_ERROR | latency={latencia}s | "
            f"prompt_chars={prompt_char_len} | model={config['model_name']} | error=ConnectionError"
        )
        return (
            "[FALHA DE CONEXÃO]: Não foi possível conectar ao servidor da API. "
            "Verifique se o seu dispositivo possui acesso à rede."
        )

    except requests.exceptions.RequestException as err:
        latencia = round(time.perf_counter() - inicio, 3)
        logger.error(
            f"status=REQUEST_EXCEPTION | latency={latencia}s | "
            f"prompt_chars={prompt_char_len} | model={config['model_name']} | error={type(err).__name__}"
        )
        return f"[FALHA DE COMUNICAÇÃO HTTP]: Ocorreu um erro inesperado: {err}"