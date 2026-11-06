"""
Interface de Linha de Comando (CLI) - Triagem de Incidentes de Help Desk.

Projeto P0 - Nível Intermediário.

Responsabilidades:
- Entrada e validação dos relatos dos usuários.
- Construção do prompt especializado de Help Desk.
- Preparação das configurações da API Gemini.
- Integração com o módulo client.py.
- Apresentação dos resultados da triagem.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


# ==========================================================
# 1. CONFIGURAÇÃO DO AMBIENTE
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ENV_PATH = BASE_DIR / ".env"

# Carrega as variáveis de ambiente antes de importar o cliente.
load_dotenv(dotenv_path=ENV_PATH)


# ==========================================================
# 2. CONFIGURAÇÃO DO ENDPOINT GEMINI
# ==========================================================

def preparar_configuracao_api() -> str:
    """
    Verifica e prepara as configurações necessárias
    para a comunicação com a API Gemini.

    Caso LLM_API_URL não esteja definida no .env,
    constrói automaticamente o endpoint utilizando
    o modelo e a versão da API configurados.
    """

    model_name = os.getenv(
        "LLM_MODEL_NAME",
        "gemini-3.5-flash-lite"
    ).strip()

    api_version = os.getenv(
        "LLM_API_VERSION",
        "v1beta"
    ).strip()

    if not model_name:
        raise ValueError(
            "A variável LLM_MODEL_NAME não está definida."
        )

    if api_version not in ("v1", "v1beta"):
        raise ValueError(
            "Versão da API inválida. Utilize v1 ou v1beta."
        )

    # Remove o prefixo models/ caso esteja presente.
    model_name = model_name.removeprefix("models/")

    # Constrói o endpoint correspondente ao modelo.
    endpoint = (
        "https://generativelanguage.googleapis.com/"
        f"{api_version}/models/"
        f"{model_name}:generateContent"
    )

    # Disponibiliza a variável para o módulo client.py.
    # Isso evita o erro de LLM_API_URL não definida.
    os.environ["LLM_API_URL"] = endpoint

    return endpoint


# ==========================================================
# 3. CONSTRUÇÃO DO PROMPT DE TRIAGEM
# ==========================================================

def construir_prompt_triagem(relato_usuario: str) -> str:
    """
    Estrutura o prompt especializado de Help Desk
    para análise e classificação dos incidentes.
    """

    return f"""
Você é um especialista em suporte técnico de TI
e gerenciamento de chamados de Help Desk.

Sua tarefa é analisar o relato apresentado pelo usuário
e gerar uma classificação técnica do incidente.

Analise cuidadosamente o problema e responda
EXATAMENTE no formato abaixo, sem introduções
ou comentários adicionais:

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
""".strip()


# ==========================================================
# 4. VALIDAÇÃO DO RELATO DO USUÁRIO
# ==========================================================

def validar_relato(relato: str) -> bool:
    """
    Valida se o relato possui conteúdo suficiente
    para realizar a classificação do incidente.
    """

    if not relato:
        print(
            "\n[AVISO]: Nenhum relato foi informado."
        )
        return False

    if len(relato) < 10:
        print(
            "\n[AVISO]: Informe um relato detalhado "
            "com pelo menos 10 caracteres."
        )
        return False

    return True


# ==========================================================
# 5. EXECUÇÃO DA INTERFACE CLI
# ==========================================================

def executar_cli():
    """
    Orquestra a interação com o usuário no terminal.

    Fluxo:
    1. Prepara as configurações.
    2. Importa o cliente da API.
    3. Recebe o relato.
    4. Constrói o prompt.
    5. Envia a solicitação ao Gemini.
    6. Apresenta o resultado.
    """

    print("\n" + "=" * 58)

    print(
        "       SISTEMA DE TRIAGEM DE CHAMADOS DE TI"
    )

    print(
        "                    HELP DESK"
    )

    print("=" * 58)

    print(
        "\nProjeto P0 - Primeiro Fluxo com LLM "
        "(Nível Intermediário)"
    )

    print(
        "Digite o relato do usuário para gerar "
        "a ficha técnica do chamado."
    )

    print(
        "Pressione Ctrl + C para encerrar "
        "a qualquer momento.\n"
    )

    try:

        # --------------------------------------------------
        # ETAPA 1: PREPARAÇÃO DA CONFIGURAÇÃO
        # --------------------------------------------------

        endpoint = preparar_configuracao_api()

        model_name = os.getenv(
            "LLM_MODEL_NAME",
            "gemini-3.5-flash-lite"
        )

        print(
            f"\nModelo configurado: {model_name}"
        )

        print(
            "Configuração da API preparada com sucesso."
        )

        # --------------------------------------------------
        # ETAPA 2: IMPORTAÇÃO DO CLIENTE
        # --------------------------------------------------

        # Importação realizada após carregar as configurações.
        from src.client import enviar_prompt_llm

        # --------------------------------------------------
        # ETAPA 3: ENTRADA DO USUÁRIO
        # --------------------------------------------------

        relato = input(
            "\nCole ou digite o relato do incidente:\n> "
        ).strip()

        # --------------------------------------------------
        # ETAPA 4: VALIDAÇÃO
        # --------------------------------------------------

        if not validar_relato(relato):
            return

        # --------------------------------------------------
        # ETAPA 5: CONSTRUÇÃO DO PROMPT
        # --------------------------------------------------

        prompt = construir_prompt_triagem(relato)

        print(
            "\nProcessando chamado com inteligência "
            "artificial... Aguarde..."
        )

        # --------------------------------------------------
        # ETAPA 6: CHAMADA AO CLIENTE GEMINI
        # --------------------------------------------------

        resultado = enviar_prompt_llm(prompt)

        # --------------------------------------------------
        # ETAPA 7: APRESENTAÇÃO DO RESULTADO
        # --------------------------------------------------

        print("\n" + "=" * 58)

        print(
            "              RESULTADO DA TRIAGEM"
        )

        print("=" * 58)

        print("\n" + resultado)

        print("\n" + "=" * 58 + "\n")

    except KeyboardInterrupt:

        print(
            "\n\nOperação cancelada pelo usuário. "
            "Encerrando..."
        )

        sys.exit(0)

    except ValueError as erro:

        print(
            f"\n[ERRO DE CONFIGURAÇÃO]: {erro}"
        )

    except ImportError as erro:

        print(
            "\n[ERRO DE IMPORTAÇÃO]: "
            "Não foi possível carregar o módulo client.py."
        )

        print(
            f"Detalhes: {erro}"
        )

    except Exception as erro:

        print(
            "\n[ERRO INESPERADO]: "
            f"{type(erro).__name__}: {erro}"
        )


# ==========================================================
# 6. FUNÇÃO PRINCIPAL
# ==========================================================

def main():
    """
    Ponto de entrada principal da aplicação.
    """

    executar_cli()


# ==========================================================
# 7. EXECUÇÃO DO PROGRAMA
# ==========================================================

if __name__ == "__main__":
    main()