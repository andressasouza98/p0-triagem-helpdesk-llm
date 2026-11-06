"""
Módulo Cliente de Integração com LLM (Google Gemini REST API).

Projeto P0 - Primeiro Fluxo com LLM (Nível Intermediário).

Responsabilidades:
- Carregar as configurações do ambiente.
- Construir o endpoint da API Gemini.
- Configurar a autenticação.
- Formatar as requisições HTTP.
- Processar as respostas do modelo.
- Tratar erros de conexão e comunicação.
"""

import os
from pathlib import Path

import requests
from dotenv import load_dotenv


# ==========================================================
# 1. CONFIGURAÇÃO DO AMBIENTE
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ENV_PATH = BASE_DIR / ".env"

# Carrega as variáveis do arquivo .env.
load_dotenv(dotenv_path=ENV_PATH)


# ==========================================================
# 2. CARREGAMENTO DAS CONFIGURAÇÕES
# ==========================================================

def carregar_configuracoes() -> dict:
    """
    Carrega e valida as configurações necessárias
    para realizar chamadas à API Gemini.
    """

    api_key = os.getenv(
        "LLM_API_KEY", ""
    ).strip()

    model_name = os.getenv(
        "LLM_MODEL_NAME",
        "gemini-3.5-flash-lite"
    ).strip()

    api_version = os.getenv(
        "LLM_API_VERSION",
        "v1beta"
    ).strip()

    # Carrega o limite de tokens.
    try:

        max_tokens = int(
            os.getenv("LLM_MAX_TOKENS", "500")
        )

    except ValueError:

        return {
            "valido": False,
            "erro": (
                "[ERRO DE CONFIGURAÇÃO]: "
                "LLM_MAX_TOKENS precisa ser um número inteiro."
            )
        }

    # ------------------------------------------------------
    # VALIDAÇÃO DA CHAVE DE API
    # ------------------------------------------------------

    if not api_key:

        return {
            "valido": False,
            "erro": (
                "[ERRO DE CONFIGURAÇÃO]: "
                "A variável 'LLM_API_KEY' não foi encontrada.\n"
                "Verifique o arquivo .env."
            )
        }

    # ------------------------------------------------------
    # VALIDAÇÃO DO MODELO
    # ------------------------------------------------------

    if not model_name:

        return {
            "valido": False,
            "erro": (
                "[ERRO DE CONFIGURAÇÃO]: "
                "A variável 'LLM_MODEL_NAME' não está definida."
            )
        }

    # Remove o prefixo models/ caso esteja presente.
    model_name = model_name.removeprefix("models/")

    # ------------------------------------------------------
    # VALIDAÇÃO DA VERSÃO DA API
    # ------------------------------------------------------

    if api_version not in ("v1", "v1beta"):

        return {
            "valido": False,
            "erro": (
                "[ERRO DE CONFIGURAÇÃO]: "
                "Versão da API inválida. "
                "Utilize v1 ou v1beta."
            )
        }

    # ------------------------------------------------------
    # VALIDAÇÃO DO LIMITE DE TOKENS
    # ------------------------------------------------------

    if max_tokens <= 0:

        return {
            "valido": False,
            "erro": (
                "[ERRO DE CONFIGURAÇÃO]: "
                "LLM_MAX_TOKENS precisa ser maior que zero."
            )
        }

    # ------------------------------------------------------
    # CONSTRUÇÃO DO ENDPOINT
    # ------------------------------------------------------

    endpoint = (
        "https://generativelanguage.googleapis.com/"
        f"{api_version}/models/"
        f"{model_name}:generateContent"
    )

    # ------------------------------------------------------
    # RETORNO DAS CONFIGURAÇÕES
    # ------------------------------------------------------

    return {
        "valido": True,
        "api_key": api_key,
        "model_name": model_name,
        "endpoint": endpoint,
        "max_tokens": max_tokens,
    }


# ==========================================================
# 3. CONFIGURAÇÃO DA AUTENTICAÇÃO
# ==========================================================

def obter_cabecalhos(config: dict) -> dict:
    """
    Configura os cabeçalhos HTTP para autenticação
    na API Gemini.
    """

    return {
        "Content-Type": "application/json",
        "x-goog-api-key": config["api_key"],
    }


# ==========================================================
# 4. TRATAMENTO DOS ERROS DA API
# ==========================================================

def diagnosticar_erro_api(response: requests.Response) -> str:
    """
    Interpreta os erros HTTP retornados pelo Google.
    """

    status = response.status_code

    try:

        dados = response.json()

        mensagem = (
            dados.get("error", {}).get(
                "message",
                response.text
            )
        )

    except ValueError:

        mensagem = response.text

    # ------------------------------------------------------
    # ERRO 400
    # ------------------------------------------------------

    if status == 400:

        return (
            "[ERRO HTTP 400 - SOLICITAÇÃO INVÁLIDA]\n"
            "A API não conseguiu processar os parâmetros enviados.\n"
            f"Detalhes do Google: {mensagem}"
        )

    # ------------------------------------------------------
    # ERRO 401
    # ------------------------------------------------------

    if status == 401:

        return (
            "[ERRO HTTP 401 - AUTENTICAÇÃO]\n"
            "A credencial enviada não foi aceita pelo Google.\n"
            "Verifique a chave configurada em LLM_API_KEY.\n\n"
            f"Detalhes do Google: {mensagem}"
        )

    # ------------------------------------------------------
    # ERRO 403
    # ------------------------------------------------------

    if status == 403:

        return (
            "[ERRO HTTP 403 - ACESSO NEGADO]\n"
            "A requisição foi recebida, mas o acesso "
            "ao recurso foi negado.\n"
            "Verifique as permissões da chave e do projeto Google.\n\n"
            f"Detalhes do Google: {mensagem}"
        )

    # ------------------------------------------------------
    # ERRO 404
    # ------------------------------------------------------

    if status == 404:

        return (
            "[ERRO HTTP 404 - MODELO NÃO ENCONTRADO]\n"
            "O modelo ou endpoint informado não foi localizado.\n"
            "Confira LLM_MODEL_NAME e LLM_API_VERSION.\n\n"
            f"Detalhes do Google: {mensagem}"
        )

    # ------------------------------------------------------
    # ERRO 429
    # ------------------------------------------------------

    if status == 429:

        return (
            "[ERRO HTTP 429 - LIMITE DE REQUISIÇÕES]\n"
            "O limite de utilização da API foi atingido.\n"
            "Verifique sua cota e tente novamente depois.\n\n"
            f"Detalhes do Google: {mensagem}"
        )

    # ------------------------------------------------------
    # ERROS DO SERVIDOR
    # ------------------------------------------------------

    if status >= 500:

        return (
            f"[ERRO HTTP {status} - SERVIDOR GOOGLE]\n"
            "O serviço Gemini apresentou uma falha temporária.\n"
            "Tente novamente em alguns instantes.\n\n"
            f"Detalhes do Google: {mensagem}"
        )

    return (
        f"[ERRO HTTP {status}]\n"
        f"Detalhes: {mensagem}"
    )


# ==========================================================
# 5. EXTRAÇÃO DA RESPOSTA DO MODELO
# ==========================================================

def extrair_resposta(dados: dict) -> str:
    """
    Extrai o conteúdo textual retornado pelo Gemini.
    """

    candidatos = dados.get("candidates", [])

    if not candidatos:

        feedback = dados.get("promptFeedback", {})

        motivo = feedback.get(
            "blockReason",
            "Nenhum candidato foi retornado."
        )

        return (
            "[AVISO]: O Gemini não gerou uma resposta.\n"
            f"Motivo: {motivo}"
        )

    candidato = candidatos[0]

    partes = (
        candidato
        .get("content", {})
        .get("parts", [])
    )

    textos = [
        parte["text"]
        for parte in partes
        if isinstance(parte, dict)
        and isinstance(parte.get("text"), str)
    ]

    if textos:

        return "\n".join(textos).strip()

    motivo = candidato.get(
        "finishReason",
        "Resposta sem conteúdo textual."
    )

    return (
        "[AVISO]: A resposta recebida não possui "
        "conteúdo textual.\n"
        f"Motivo: {motivo}"
    )


# ==========================================================
# 6. ENVIO DO PROMPT PARA O GEMINI
# ==========================================================

def enviar_prompt_llm(prompt: str) -> str:
    """
    Envia o prompt para a API Gemini.

    Responsabilidades:
    - Validar as configurações.
    - Configurar a autenticação.
    - Construir a requisição HTTP.
    - Enviar a solicitação ao modelo.
    - Extrair a resposta.
    - Tratar erros de comunicação.
    """

    # ------------------------------------------------------
    # CARREGAMENTO DAS CONFIGURAÇÕES
    # ------------------------------------------------------

    config = carregar_configuracoes()

    if not config["valido"]:

        return config["erro"]

    # ------------------------------------------------------
    # VALIDAÇÃO DO PROMPT
    # ------------------------------------------------------

    if not prompt or not prompt.strip():

        return (
            "[ERRO]: O prompt enviado está vazio."
        )

    # ------------------------------------------------------
    # CABEÇALHOS DE AUTENTICAÇÃO
    # ------------------------------------------------------

    headers = obter_cabecalhos(config)

    # ------------------------------------------------------
    # CONSTRUÇÃO DO PAYLOAD
    # ------------------------------------------------------

    payload = {

        "contents": [

            {
                "role": "user",

                "parts": [

                    {
                        "text": prompt
                    }

                ]

            }

        ],

        "generationConfig": {

            "maxOutputTokens": config["max_tokens"],

        }

    }

    # ------------------------------------------------------
    # ENVIO DA REQUISIÇÃO HTTP
    # ------------------------------------------------------

    try:

        response = requests.post(
            config["endpoint"],
            headers=headers,
            json=payload,
            timeout=10
        )

        # Verifica se a API retornou algum erro HTTP.
        if not response.ok:

            return diagnosticar_erro_api(response)

        # --------------------------------------------------
        # INTERPRETAÇÃO DA RESPOSTA JSON
        # --------------------------------------------------

        try:

            dados = response.json()

        except ValueError:

            return (
                "[ERRO]: O servidor retornou uma resposta "
                "que não está em formato JSON válido."
            )

        # --------------------------------------------------
        # EXTRAÇÃO DO TEXTO GERADO
        # --------------------------------------------------

        return extrair_resposta(dados)

    # ------------------------------------------------------
    # TRATAMENTO DE TIMEOUT
    # ------------------------------------------------------

    except requests.exceptions.Timeout:

        return (
            "Erro de conexão: "
            "O serviço do LLM demorou muito para responder."
        )

    # ------------------------------------------------------
    # TRATAMENTO DE ERRO DE CONEXÃO
    # ------------------------------------------------------

    except requests.exceptions.ConnectionError:

        return (
            "[ERRO DE REDE]: Não foi possível estabelecer "
            "conexão com o servidor Gemini.\n"
            "Verifique sua conexão com a internet."
        )

    # ------------------------------------------------------
    # TRATAMENTO DE OUTROS ERROS HTTP
    # ------------------------------------------------------

    except requests.exceptions.RequestException as erro:

        return (
            "[ERRO DE COMUNICAÇÃO HTTP]: "
            f"{str(erro)}"
        )

    # ------------------------------------------------------
    # TRATAMENTO DE ERROS INESPERADOS
    # ------------------------------------------------------

    except Exception as erro:

        return (
            "[ERRO INESPERADO]: "
            f"{type(erro).__name__}: {str(erro)}"
        )