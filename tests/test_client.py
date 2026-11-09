"""
Suíte de testes unitários 100% offline para o módulo src/client.py.
Utiliza pytest, monkeypatch e requests-mock para garantir isolamento total de rede.
"""

import pytest
import requests
from src.client import enviar_prompt_llm, carregar_configuracoes


@pytest.fixture(autouse=True)
def setup_variaveis_ambiente(monkeypatch):
    """
    Simula as variáveis de ambiente necessárias para isolar completamente
    a execução do arquivo .env real da máquina.
    """
    monkeypatch.setenv("LLM_API_KEY", "mock_key_segura_123456")
    monkeypatch.setenv("LLM_MODEL_NAME", "gemini-3.5-flash-lite")
    monkeypatch.setenv("LLM_API_VERSION", "v1beta")
    monkeypatch.setenv("LLM_MAX_TOKENS", "500")
    monkeypatch.setenv("LLM_TEMPERATURE", "0.2")
    monkeypatch.setenv("LLM_TIMEOUT", "5")


def test_chamada_sucesso(requests_mock):
    """
    Valida a chamada bem-sucedida (HTTP 200) com finishReason STOP,
    assegurando a extração do texto retornado sem consumo de créditos.
    """
    config = carregar_configuracoes()
    endpoint = (
        f"https://generativelanguage.googleapis.com/{config['api_version']}/"
        f"models/{config['model_name']}:generateContent"
    )

    payload_resposta = {
        "candidates": [
            {
                "finishReason": "STOP",
                "content": {
                    "parts": [
                        {
                            "text": (
                                "CATEGORIA: Hardware\n"
                                "URGÊNCIA: Média\n"
                                "AÇÃO RECOMENDADA: Verificar cabos da impressora."
                            )
                        }
                    ]
                }
            }
        ]
    }

    requests_mock.post(endpoint, json=payload_resposta, status_code=200)

    resultado = enviar_prompt_llm("Impressora sem comunicação com o faturamento.")

    assert "CATEGORIA: Hardware" in resultado
    assert "AÇÃO RECOMENDADA: Verificar cabos da impressora." in resultado
    assert "[ALERTA DE TRUNCAMENTO]" not in resultado


def test_erro_autenticacao_401(requests_mock):
    """
    Valida interceptação de erro HTTP 401, garantindo resposta orientativa
    ao usuário sem quebrar o fluxo da aplicação.
    """
    config = carregar_configuracoes()
    endpoint = (
        f"https://generativelanguage.googleapis.com/{config['api_version']}/"
        f"models/{config['model_name']}:generateContent"
    )

    requests_mock.post(endpoint, status_code=401)

    resultado = enviar_prompt_llm("Relato com chave inválida.")

    assert "[ERRO DE AUTENTICAÇÃO]" in resultado
    assert "LLM_API_KEY" in resultado


def test_timeout_conexao(requests_mock):
    """
    Valida a captura limpa de Timeout via requests-mock, confirmando
    que a aplicação não lança tracebacks não tratados.
    """
    config = carregar_configuracoes()
    endpoint = (
        f"https://generativelanguage.googleapis.com/{config['api_version']}/"
        f"models/{config['model_name']}:generateContent"
    )

    requests_mock.post(endpoint, exc=requests.exceptions.Timeout)

    resultado = enviar_prompt_llm("Relato com lentidão extrema de rede.")

    assert "[TEMPO LIMITE EXCEDIDO]" in resultado
    assert "Verifique a sua conexão com a internet." in resultado