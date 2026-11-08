"""
Interface de Linha de Comando (CLI) - Triagem de Incidentes de Help Desk.

Projeto P0 - Primeiro Fluxo com LLM (Nível Intermediário).

Responsabilidades:
- Receber os relatos dos usuários.
- Validar as entradas.
- Construir o prompt de triagem.
- Acionar o cliente de integração com LLM.
- Apresentar o resultado da classificação.
"""

import sys


# ==========================================================
# 1. CONSTRUÇÃO DO PROMPT DE TRIAGEM
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
# 2. VALIDAÇÃO DA ENTRADA DO USUÁRIO
# ==========================================================

def validar_relato(relato: str) -> bool:
    """
    Valida se o relato do usuário não está vazio,
    não contém apenas espaços e possui o tamanho mínimo.
    """

    # Verifica entradas vazias ou contendo apenas espaços.
    if not relato.strip():
        print(
            "\n[AVISO]: O relato não pode estar vazio. "
            "Digite uma descrição do incidente."
        )
        return False

    # Verifica o tamanho mínimo do relato.
    if len(relato.strip()) < 10:
        print(
            "\n[AVISO]: Informe um relato detalhado "
            "com pelo menos 10 caracteres."
        )
        return False

    return True


# ==========================================================
# 3. EXECUÇÃO DA INTERFACE CLI
# ==========================================================

def executar_cli():
    """
    Orquestra a interação com o usuário no terminal.

    Fluxo:
    1. Apresenta a interface.
    2. Recebe o relato.
    3. Valida a entrada.
    4. Constrói o prompt.
    5. Invoca o cliente LLM.
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
        # ETAPA 1: ENTRADA DO USUÁRIO
        # --------------------------------------------------

        relato = input(
            "Cole ou digite o relato do incidente:\n> "
        )

        # --------------------------------------------------
        # ETAPA 2: VALIDAÇÃO DA ENTRADA
        # --------------------------------------------------

        if not validar_relato(relato):
            return

        # Remove espaços desnecessários antes e depois do texto.
        relato = relato.strip()

        # --------------------------------------------------
        # ETAPA 3: CONSTRUÇÃO DO PROMPT
        # --------------------------------------------------

        prompt = construir_prompt_triagem(relato)

        print(
            "\nProcessando chamado com inteligência "
            "artificial... Aguarde..."
        )

        # --------------------------------------------------
        # ETAPA 4: IMPORTAÇÃO E CHAMADA DO CLIENTE
        # --------------------------------------------------

        # O cliente somente é importado após a validação.
        # Assim, entradas inválidas não acionam a integração.

        from src.client import enviar_prompt_llm

        resultado = enviar_prompt_llm(prompt)

        # --------------------------------------------------
        # ETAPA 5: APRESENTAÇÃO DO RESULTADO
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

    except ImportError as erro:

        print(
            "\n[ERRO DE IMPORTAÇÃO]: "
            "Não foi possível carregar o módulo client.py."
        )

        print(f"Detalhes: {erro}")

    except Exception as erro:

        print(
            "\n[ERRO INESPERADO]: "
            f"{type(erro).__name__}: {erro}"
        )


# ==========================================================
# 4. FUNÇÃO PRINCIPAL
# ==========================================================

def main():
    """
    Ponto de entrada principal da aplicação.
    """

    executar_cli()


# ==========================================================
# 5. EXECUÇÃO DO PROGRAMA
# ==========================================================

if __name__ == "__main__":
    main()