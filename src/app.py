"""
Módulo Principal - Triagem e Classificação de Chamados de Help Desk.

Projeto P0 - Primeiro Fluxo com LLM.

Funcionalidades:
- Integração com a API Gemini.
- Autenticação segura por variável de ambiente.
- Seleção configurável do modelo.
- Classificação automática de chamados.
- Diagnóstico de erros da API.
- Tratamento de falhas de conexão e timeout.
"""

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv


# ==========================================================
# 1. CONFIGURAÇÃO DO AMBIENTE
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)


# ==========================================================
# 2. CARREGAMENTO DAS CONFIGURAÇÕES
# ==========================================================

def carregar_configuracoes() -> dict:
    """
    Carrega as configurações do arquivo .env.
    """

    api_key = (
        os.getenv("LLM_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or ""
    ).strip()

    if not api_key:
        raise ValueError(
            "A chave da API não foi encontrada.\n"
            "Verifique se LLM_API_KEY está preenchida no arquivo .env."
        )

    model_name = os.getenv(
        "LLM_MODEL_NAME",
        "gemini-3.8-flash"
    ).strip()

    api_version = os.getenv(
        "LLM_API_VERSION",
        "v1beta"
    ).strip()

    max_tokens = int(
        os.getenv("LLM_MAX_TOKENS", "500")
    )

    temperature = float(
        os.getenv("LLM_TEMPERATURE", "0.2")
    )

    timeout = int(
        os.getenv("LLM_TIMEOUT", "60")
    )

    if not model_name:
        raise ValueError("O nome do modelo não foi configurado.")

    if api_version not in ("v1", "v1beta"):
        raise ValueError(
            "Versão da API inválida. Utilize v1 ou v1beta."
        )

    if max_tokens <= 0:
        raise ValueError("LLM_MAX_TOKENS precisa ser maior que zero.")

    if not 0 <= temperature <= 2:
        raise ValueError("LLM_TEMPERATURE deve estar entre 0 e 2.")

    if timeout <= 0:
        raise ValueError("LLM_TIMEOUT precisa ser maior que zero.")

    return {
        "api_key": api_key,
        "model_name": model_name,
        "api_version": api_version,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "timeout": timeout,
    }


# ==========================================================
# 3. CONSTRUÇÃO DO ENDPOINT E AUTENTICAÇÃO
# ==========================================================

def construir_endpoint(config: dict) -> str:
    """
    Constrói o endpoint oficial da API Gemini.
    """

    modelo = config["model_name"].replace("models/", "")

    endpoint = (
        "https://generativelanguage.googleapis.com/"
        f"{config['api_version']}/models/"
        f"{modelo}:generateContent"
    )

    return endpoint


def obter_cabecalhos(config: dict) -> dict:
    """
    Configura os cabeçalhos de autenticação.

    IMPORTANTE:
    A API Gemini utiliza x-goog-api-key.
    Não utilizar Authorization Bearer para enviar a API key.
    """

    return {
        "Content-Type": "application/json",
        "x-goog-api-key": config["api_key"],
    }


# ==========================================================
# 4. CONSTRUÇÃO DO PROMPT DE TRIAGEM
# ==========================================================

def construir_prompt_triagem(relato_usuario: str) -> str:
    """
    Cria o prompt padronizado para classificação
    dos chamados de Help Desk.
    """

    prompt = f"""
Você é um especialista em suporte técnico de TI
e gerenciamento de chamados de Help Desk.

Sua tarefa é analisar o relato apresentado pelo usuário
e gerar uma classificação técnica do incidente.

Analise cuidadosamente o problema e responda
EXATAMENTE no formato abaixo, sem introduções
ou comentários adicionais.

CATEGORIA:
[Hardware, Software, Rede, Acesso/Segurança ou Outro]

SEVERIDADE SUGERIDA:
[Baixa, Média, Alta ou Crítica]

SÍNTESE DA FALHA:
[Descreva o problema em uma única frase,
com linguagem técnica e objetiva.]

AÇÃO RECOMENDADA:
[Apresente a primeira ação que um técnico
de suporte de Nível 1 deverá executar.]

CRITÉRIOS DE CLASSIFICAÇÃO:

Baixa:
Problemas simples que não comprometem
significativamente o trabalho do usuário.

Média:
Problemas que prejudicam parcialmente
as atividades do usuário.

Alta:
Problemas que comprometem atividades importantes
ou afetam vários usuários.

Crítica:
Indisponibilidade de sistemas essenciais,
falhas graves de segurança ou interrupção
generalizada dos serviços.

RELATO DO USUÁRIO:

{relato_usuario}

FIM DO RELATO.
"""

    return prompt.strip()


# ==========================================================
# 5. TRATAMENTO DAS RESPOSTAS DE ERRO DA API
# ==========================================================

def diagnosticar_erro_api(response: requests.Response) -> str:
    """
    Interpreta os erros retornados pela API Gemini.
    """

    status = response.status_code

    try:
        dados = response.json()

        mensagem = (
            dados.get("error", {})
            .get("message", response.text)
        )

    except ValueError:
        mensagem = response.text

    if status == 400:
        return (
            "[ERRO HTTP 400]\n"
            "A solicitação enviada à API é inválida.\n"
            f"Detalhes: {mensagem}"
        )

    elif status == 401:
        return (
            "[ERRO HTTP 401 - AUTENTICAÇÃO]\n"
            "A API Gemini não aceitou a credencial enviada.\n\n"
            "Verifique:\n"
            "1. Se a chave pertence ao Google AI Studio.\n"
            "2. Se a chave é do tipo de autorização aceito "
            "pela API Gemini.\n"
            "3. Se a variável LLM_API_KEY está correta no .env.\n"
            "4. Se a chave não foi revogada.\n\n"
            f"Detalhes do Google: {mensagem}"
        )

    elif status == 403:
        return (
            "[ERRO HTTP 403 - PERMISSÃO NEGADA]\n"
            "A credencial foi recebida, mas não possui "
            "permissão para realizar essa operação.\n"
            "Verifique as restrições da chave, o projeto "
            "e a ativação da API Gemini.\n\n"
            f"Detalhes: {mensagem}"
        )

    elif status == 404:
        return (
            "[ERRO HTTP 404 - MODELO NÃO ENCONTRADO]\n"
            "O modelo configurado não está disponível "
            "nesse endpoint.\n"
            "Verifique LLM_MODEL_NAME no arquivo .env.\n\n"
            f"Detalhes: {mensagem}"
        )

    elif status == 429:
        return (
            "[ERRO HTTP 429 - LIMITE DE REQUISIÇÕES]\n"
            "O limite de utilização da API foi atingido.\n"
            "Verifique as cotas e os limites do seu projeto.\n\n"
            f"Detalhes: {mensagem}"
        )

    elif status >= 500:
        return (
            f"[ERRO HTTP {status} - SERVIDOR GOOGLE]\n"
            "O serviço Gemini apresentou uma falha temporária.\n"
            "Tente novamente em alguns instantes.\n\n"
            f"Detalhes: {mensagem}"
        )

    return (
        f"[ERRO HTTP {status}]\n"
        f"Detalhes: {mensagem}"
    )


# ==========================================================
# 6. ENVIO DA SOLICITAÇÃO PARA O GEMINI
# ==========================================================

def enviar_solicitacao_llm(
    prompt: str,
    config: dict,
    endpoint: str
) -> str:
    """
    Envia o prompt para o modelo Gemini
    e retorna a resposta gerada.
    """

    headers = obter_cabecalhos(config)

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
            "temperature": config["temperature"],
            "maxOutputTokens": config["max_tokens"],
        }
    }

    try:

        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=(10, config["timeout"])
        )

        # Verifica se a API retornou algum erro.

        if not response.ok:
            return diagnosticar_erro_api(response)

        dados = response.json()

        # Verifica se existem candidatos de resposta.

        candidatos = dados.get("candidates", [])

        if not candidatos:

            feedback = dados.get("promptFeedback", {})

            motivo = feedback.get(
                "blockReason",
                "Motivo não informado."
            )

            return (
                "[AVISO]: O Gemini não retornou uma resposta.\n"
                f"Motivo: {motivo}"
            )

        # Extrai o conteúdo textual gerado pelo modelo.

        partes = (
            candidatos[0]
            .get("content", {})
            .get("parts", [])
        )

        textos = [
            parte["text"]
            for parte in partes
            if isinstance(parte, dict) and "text" in parte
        ]

        if textos:
            return "\n".join(textos).strip()

        motivo = candidatos[0].get(
            "finishReason",
            "Resposta sem conteúdo textual."
        )

        return (
            "[AVISO]: O modelo respondeu sem conteúdo textual.\n"
            f"Motivo: {motivo}"
        )

    except requests.exceptions.Timeout:

        return (
            "[ERRO]: Tempo limite de conexão ou resposta "
            "excedido.\n"
            "Verifique a conexão e tente novamente."
        )

    except requests.exceptions.ConnectionError:

        return (
            "[ERRO]: Não foi possível estabelecer conexão "
            "com a API Gemini.\n"
            "Verifique sua internet."
        )

    except requests.exceptions.RequestException as erro:

        return (
            "[ERRO DE REQUISIÇÃO]: "
            f"{str(erro)}"
        )

    except ValueError:

        return (
            "[ERRO]: Não foi possível interpretar "
            "a resposta JSON da API."
        )

    except Exception as erro:

        return (
            "[ERRO INESPERADO]: "
            f"{str(erro)}"
        )


# ==========================================================
# 7. FUNÇÃO PRINCIPAL DO SISTEMA
# ==========================================================

def main():

    print("\n")
    print("=" * 58)
    print("       SISTEMA DE TRIAGEM DE CHAMADOS DE TI")
    print("                    HELP DESK")
    print("=" * 58)

    print(
        "\nProjeto P0 - Primeiro Fluxo com LLM"
    )

    print(
        "\nDigite o relato do usuário para gerar "
        "a ficha técnica do chamado."
    )

    try:

        # Carrega as configurações.

        config = carregar_configuracoes()

        # Constrói o endpoint do modelo.

        endpoint = construir_endpoint(config)

        print("\nConfigurações carregadas com sucesso.")

        print(
            f"Modelo selecionado: {config['model_name']}"
        )

        print("\n" + "-" * 58)

        # Recebe o relato do usuário.

        relato = input(
            "\nCole ou digite o relato do incidente:\n> "
        ).strip()

        if not relato or len(relato) < 10:

            print(
                "\n[AVISO]: Informe um relato com "
                "pelo menos 10 caracteres."
            )

            return

        # Constrói o prompt.

        prompt = construir_prompt_triagem(relato)

        print(
            "\nProcessando chamado com inteligência artificial..."
        )

        # Envia a solicitação para o Gemini.

        resultado = enviar_solicitacao_llm(
            prompt,
            config,
            endpoint
        )

        # Apresenta o resultado.

        print("\n")
        print("=" * 58)
        print("              RESULTADO DA TRIAGEM")
        print("=" * 58)

        print("\n" + resultado)

        print("\n" + "=" * 58)

    except ValueError as erro:

        print(f"\n[ERRO DE CONFIGURAÇÃO]: {erro}")

        sys.exit(1)

    except KeyboardInterrupt:

        print("\n\nOperação cancelada pelo usuário.")

        sys.exit(0)


# ==========================================================
# 8. EXECUÇÃO DO PROGRAMA
# ==========================================================

if __name__ == "__main__":
    main()