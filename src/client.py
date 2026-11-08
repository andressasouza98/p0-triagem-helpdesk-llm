"""
Módulo Cliente - Integração Resiliente com a API Google Gemini REST.

Projeto P0 - Primeiro Fluxo com LLM (Nível Intermediário).

Responsabilidades:
- Carregar configurações do ambiente.
- Construir o endpoint da API Gemini.
- Configurar autenticação.
- Formatar requisições HTTP.
- Processar respostas do modelo.
- Tratar erros de configuração, rede e API.
- Evitar propagação de tracebacks para a interface CLI.
"""

import os
import math
from pathlib import Path

import requests
from dotenv import load_dotenv


# ==========================================================
# 1. CONFIGURAÇÃO DO AMBIENTE
# ==========================================================

# Localiza a raiz do projeto.
BASE_DIR = Path(__file__).resolve().parent.parent

# Localiza o arquivo .env.
ENV_PATH = BASE_DIR / ".env"

# Carrega as variáveis de ambiente.
load_dotenv(dotenv_path=ENV_PATH)


# ==========================================================
# 2. CARREGAMENTO DAS CONFIGURAÇÕES
# ==========================================================

def carregar_configuracoes() -> dict:
    """
    Carrega e valida as configurações necessárias
    para realizar chamadas à API Google Gemini.

    Retorna um dicionário com os parâmetros operacionais.
    """

    # Recupera a chave de API.
    api_key = (
        os.getenv("LLM_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or ""
    ).strip()

    # Valida a existência da chave.
    if not api_key or api_key == "COLOQUE_SUA_CHAVE_AQUI":

        raise ValueError(
            "Chave de API não configurada.\n"
            "Preencha a variável LLM_API_KEY no arquivo .env."
        )

    # Identificação do modelo.
    model_name = os.getenv(
        "LLM_MODEL_NAME",
        "gemini-3.5-flash-lite"
    ).strip()

    # Versão da API.
    api_version = os.getenv(
        "LLM_API_VERSION",
        "v1beta"
    ).strip()

   # Recuperação dos parâmetros numéricos.
    
    try:

        max_tokens = int(
            os.getenv("LLM_MAX_TOKENS", "500")
        )
        temperature = float(
            os.getenv("LLM_TEMPERATURE", "0.2")
        )
        timeout = float(
            os.getenv("LLM_TIMEOUT", "30")
        )

    except ValueError:
        raise ValueError("Parâmetros numéricos em .env inválidos.")

    # Validação do modelo.
    if not model_name:

        raise ValueError(
            "A variável LLM_MODEL_NAME não foi definida."
        )

    # Validação da versão.
    if api_version not in ("v1", "v1beta"):

        raise ValueError(
            "Versão da API inválida. Utilize v1 ou v1beta."
        )

    # Validação dos tokens.
    if max_tokens <= 0:

        raise ValueError(
            "LLM_MAX_TOKENS precisa ser maior que zero."
        )

    # Validação do timeout.
    if not math.isfinite(timeout) or timeout <= 0:

        raise ValueError(
            "LLM_TIMEOUT precisa ser um número positivo."
        )

    # Remove eventual prefixo models/.
    model_name = model_name.removeprefix("models/")

    return {
        "api_key": api_key,
        "model_name": model_name,
        "api_version": api_version,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "timeout": timeout,
    }


# ==========================================================
# 3. CONSTRUÇÃO DO ENDPOINT
# ==========================================================

def construir_endpoint(config: dict) -> str:
    """
    Constrói automaticamente o endpoint REST
    correspondente ao modelo configurado.
    """

    return (
        "https://generativelanguage.googleapis.com/"
        f"{config['api_version']}/models/"
        f"{config['model_name']}:generateContent"
    )


# ==========================================================
# 4. CONFIGURAÇÃO DA AUTENTICAÇÃO
# ==========================================================

def obter_cabecalhos(config: dict) -> dict:
    """
    Configura os cabeçalhos HTTP para autenticação.

    A API Gemini utiliza x-goog-api-key.
    A chave não é enviada na URL nem como Bearer.
    """

    return {
        "Content-Type": "application/json",
        "x-goog-api-key": config["api_key"],
    }


# ==========================================================
# 5. EXTRAÇÃO DAS MENSAGENS DE ERRO DA API
# ==========================================================

def extrair_mensagem_erro_api(
    response: requests.Response
) -> str:
    """
    Extrai com segurança a mensagem de erro
    retornada pelo Google Gemini.
    """

    try:

        dados = response.json()

        erro = dados.get("error", {})

        if isinstance(erro, dict):

            mensagem = erro.get("message")

            if mensagem:
                return mensagem

        return (
            response.text.strip()
            or "Detalhe não informado pelo servidor."
        )

    except ValueError:

        return (
            response.text.strip()
            or "Não foi possível interpretar o erro retornado."
        )


# ==========================================================
# 6. DIAGNÓSTICO DOS ERROS HTTP
# ==========================================================

def diagnosticar_erro_api(
    response: requests.Response,
    model_name: str
) -> str:
    """
    Identifica os principais códigos HTTP
    e retorna mensagens amigáveis em português.
    """

    status = response.status_code

    detalhe = extrair_mensagem_erro_api(response)

    # ------------------------------------------------------
    # HTTP 400 - REQUISIÇÃO INVÁLIDA
    # ------------------------------------------------------

    if status == 400:

        return (
            "[ERRO HTTP 400 - SOLICITAÇÃO INVÁLIDA]\n"
            "A API não conseguiu processar os parâmetros enviados.\n"
            f"Detalhes do Google: {detalhe}"
        )

    # ------------------------------------------------------
    # HTTP 401 - FALHA DE AUTENTICAÇÃO
    # ------------------------------------------------------

    if status == 401:

        return (
            "[ERRO DE AUTENTICAÇÃO (HTTP 401)]\n"
            "A credencial de acesso foi recusada pelo Google.\n"
            "Verifique se a chave de API está válida e ativa.\n"
            "Confira também a variável LLM_API_KEY no .env.\n\n"
            f"Detalhes do Google: {detalhe}"
        )

    # ------------------------------------------------------
    # HTTP 403 - PERMISSÃO NEGADA
    # ------------------------------------------------------

    if status == 403:

        return (
            "[ERRO DE PERMISSÃO (HTTP 403)]\n"
            "O acesso ao recurso solicitado foi negado.\n"
            "Verifique as permissões da chave e do projeto Google.\n\n"
            f"Detalhes do Google: {detalhe}"
        )

    # ------------------------------------------------------
    # HTTP 404 - MODELO NÃO ENCONTRADO
    # ------------------------------------------------------

    if status == 404:

        return (
            "[ERRO DE RECURSO NÃO ENCONTRADO (HTTP 404)]\n"
            f"O modelo '{model_name}' ou endpoint não foi localizado.\n"
            "Verifique LLM_MODEL_NAME e LLM_API_VERSION.\n\n"
            f"Detalhes do Google: {detalhe}"
        )

    # ------------------------------------------------------
    # HTTP 429 - LIMITE DE REQUISIÇÕES
    # ------------------------------------------------------

    if status == 429:

        return (
            "[LIMITE DE REQUISIÇÕES EXCEDIDO (HTTP 429)]\n"
            "A cota de utilização da API foi atingida.\n"
            "Verifique os limites de utilização do Google AI Studio.\n"
            "Aguarde antes de realizar uma nova solicitação.\n\n"
            f"Detalhes do Google: {detalhe}"
        )

    # ------------------------------------------------------
    # HTTP 500 OU SUPERIOR - FALHA NO SERVIDOR
    # ------------------------------------------------------

    if status >= 500:

        return (
            f"[FALHA TEMPORÁRIA NO SERVIÇO (HTTP {status})]\n"
            "Os servidores do Google Gemini estão instáveis "
            "ou temporariamente indisponíveis.\n"
            "Tente novamente em alguns instantes.\n\n"
            f"Detalhes do Google: {detalhe}"
        )

    # ------------------------------------------------------
    # OUTROS ERROS HTTP
    # ------------------------------------------------------

    return (
        f"[FALHA NA REQUISIÇÃO (HTTP {status})]\n"
        f"Mensagem do provedor: {detalhe}"
    )


# ==========================================================
# 7. EXTRAÇÃO E INSPEÇÃO DEFENSIVA DA RESPOSTA DO MODELO
# ==========================================================

def extrair_resposta(dados: dict) -> str:
    """
    Extrai o conteúdo textual retornado pelo modelo Gemini e inspeciona
    defensivamente o motivo de encerramento da geração (finishReason).
    """

    candidatos = dados.get("candidates", [])

    # 1. Verifica se a geração foi bloqueada antes de criar candidatos
    if not candidatos:

        feedback = dados.get("promptFeedback") or {}
        
        bloqueio = feedback.get(
            "blockReason",
            "Filtro de segurança ou ausência de resposta."
        )

        return (
            "[RESPOSTA BLOQUEADA PELO PROVEDOR]\n"
            "O modelo não gerou conteúdo textual para este chamado.\n"
            f"Motivo informado pelo Google: {bloqueio}"
        )

    candidato = candidatos[0]
    if not isinstance(candidato, dict):
        return "[ERRO DE ESTRUTURA]: Formato de candidato inválido na resposta da API."

    # 2. Extração segura e padronizada do motivo de término (finishReason)
    finish_reason = str(candidato.get("finishReason", "STOP")).upper()

    # 3. Extração defensiva das partes de texto geradas
    conteudo = candidato.get("content") or {}
    partes = conteudo.get("parts", []) if isinstance(conteudo, dict) else []
    textos = [
        parte.get("text")
        for parte in partes
        if isinstance(parte, dict) and isinstance(parte.get("text"), str)
    ]
    texto_gerado = "\n".join(textos).strip()

    # 4. Tratamento granular por tipo de encerramento
    if finish_reason == "STOP":
        if texto_gerado:
            return texto_gerado
        return "[AVISO]: O modelo concluiu a geração, mas não retornou texto visível."

    elif finish_reason in ("MAX_TOKENS", "LENGTH"):
        aviso_truncamento = (
            "\n\n----------------------------------------------------------\n"
            "[ALERTA DE TRUNCAMENTO]: O limite de tokens configurado foi atingido. "
            "A resposta pode estar incompleta.\n"
            "Sugestão técnica: Aumente o valor de 'LLM_MAX_TOKENS' no arquivo .env."
        )
        if texto_gerado:
            return texto_gerado + aviso_truncamento
        return (
            "[ALERTA DE TRUNCAMENTO]: O modelo atingiu o limite de tokens antes de gerar texto.\n"
            "Aumente o valor de 'LLM_MAX_TOKENS' no arquivo .env."
        )

    elif finish_reason == "SAFETY":
        return (
            "[RESPOSTA BLOQUEADA POR POLÍTICA DE SEGURANÇA (SAFETY)]\n"
            "O processamento foi interrompido pelos filtros de moderação do modelo.\n"
            "Causa: O relato fornecido ativou políticas de restrição de conteúdo do Google Gemini."
        )

    elif finish_reason == "RECITATION":
        return (
            "[BLOQUEIO POR RECITAÇÃO (RECITATION)]\n"
            "A geração foi interrompida para evitar reprodução exata de material protegido por direitos autorais."
        )

    else:
        # Tratamento de fallback para outros motivos (OTHER, UNKNOWN, etc.)
        aviso_generico = (
            f"\n\n[AVISO]: O processamento encerrou com status atípico: '{finish_reason}'."
        )
        if texto_gerado:
            return texto_gerado + aviso_generico
        return (
            "[AVISO]: O modelo encerrou o processamento sem gerar texto legível.\n"
            f"Status informado: {finish_reason}"
        )


# ==========================================================
# 8. ENVIO DO PROMPT PARA O GEMINI
# ==========================================================

def enviar_prompt_llm(prompt: str) -> str:
    """
    Executa a requisição HTTP POST à API Gemini.

    Responsabilidades:
    - Validar configurações.
    - Validar o prompt.
    - Preparar a autenticação.
    - Construir o payload.
    - Enviar a solicitação.
    - Processar a resposta.
    - Tratar exceções sem propagar tracebacks.
    """

    # ------------------------------------------------------
    # ETAPA 1 - CARREGAMENTO DAS CONFIGURAÇÕES
    # ------------------------------------------------------

    try:

        config = carregar_configuracoes()

        endpoint = construir_endpoint(config)

        headers = obter_cabecalhos(config)

    except ValueError as erro:

        return (
            "[ERRO DE CONFIGURAÇÃO]: "
            f"{str(erro)}"
        )

    # ------------------------------------------------------
    # ETAPA 2 - VALIDAÇÃO DO PROMPT
    # ------------------------------------------------------

    if not prompt or not prompt.strip():

        return (
            "[ERRO]: O prompt enviado está vazio."
        )

    # ------------------------------------------------------
    # ETAPA 3 - CONSTRUÇÃO DO PAYLOAD
    # ------------------------------------------------------

    payload = {

        "contents": [

            {
                "role": "user",

                "parts": [

                    {
                        "text": prompt.strip()
                    }

                ]

            }

        ],

       "generationConfig": {
            "maxOutputTokens": config.get("max_tokens", 500),
            "temperature": config.get("temperature", 0.2)
        }

    }

    # ------------------------------------------------------
    # ETAPA 4 - EXECUÇÃO DA REQUISIÇÃO HTTP
    # ------------------------------------------------------

    try:

        response = requests.post(

            endpoint,

            headers=headers,

            json=payload,

            timeout=config["timeout"]

        )

        # --------------------------------------------------
        # ETAPA 5 - VERIFICAÇÃO DO STATUS HTTP
        # --------------------------------------------------

        if not response.ok:

            return diagnosticar_erro_api(
                response,
                config["model_name"]
            )

        # --------------------------------------------------
        # ETAPA 6 - INTERPRETAÇÃO DA RESPOSTA JSON
        # --------------------------------------------------

        try:

            dados = response.json()

        except ValueError:

            return (
                "[ERRO DE PARSING]: "
                "A resposta recebida da API não pôde "
                "ser interpretada como JSON."
            )

        # --------------------------------------------------
        # ETAPA 7 - EXTRAÇÃO DA RESPOSTA
        # --------------------------------------------------

        return extrair_resposta(dados)

    # ======================================================
    # 9. TRATAMENTO DE EXCEÇÕES DE COMUNICAÇÃO
    # ======================================================

    # ------------------------------------------------------
    # TIMEOUT
    # ------------------------------------------------------

    except requests.exceptions.Timeout:

        return (
            "Erro de conexão: "
            "O serviço do LLM demorou muito para responder."
        )

    # ------------------------------------------------------
    # FALHA DE CONEXÃO
    # ------------------------------------------------------

    except requests.exceptions.ConnectionError:

        return (
            "[FALHA DE CONEXÃO DE REDE]\n"
            "Não foi possível alcançar os servidores "
            "da API do Google Gemini.\n"
            "Verifique sua conexão com a internet, "
            "firewall ou resolução de DNS."
        )

    # ------------------------------------------------------
    # OUTROS ERROS HTTP
    # ------------------------------------------------------

    except requests.exceptions.RequestException as erro:

        return (
            "[ERRO DE TRANSPORTE HTTP]\n"
            "Ocorreu uma falha durante a transmissão dos dados.\n"
            f"Detalhes: {str(erro)}"
        )

    # ------------------------------------------------------
    # ERROS INESPERADOS
    # ------------------------------------------------------

    except Exception as erro:

        return (
            "[ERRO INESPERADO NA APLICAÇÃO]\n"
            f"Tipo: {type(erro).__name__}\n"
            f"Detalhes: {str(erro)}"
        )