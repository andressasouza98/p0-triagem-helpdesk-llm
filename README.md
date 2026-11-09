# p0-triagem-helpdesk-llm

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Code Style](https://img.shields.io/badge/code%20style-pep8-green.svg)](https://pep8.org/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)
[![Release p0-basico](https://img.shields.io/badge/release-p0--basico-orange.svg)](https://github.com/andressasouza98/p0-triagem-helpdesk-llm/releases/tag/p0-basico)
[![Release p0-intermediario](https://img.shields.io/badge/release-p0--intermediario-yellow.svg)](https://github.com/andressasouza98/p0-triagem-helpdesk-llm/releases/tag/p0-intermediario)
[![Release p0-avancado](https://img.shields.io/badge/release-p0--avancado-brightgreen.svg)](https://github.com/andressasouza98/p0-triagem-helpdesk-llm/releases/tag/p0-avancado)

Sistema de triagem inteligente e automação de chamados de suporte técnico de TI utilizando Grandes Modelos de Linguagem (Google Gemini API). O sistema processa descrições livres de incidentes técnicos, extraindo de forma estruturada a categoria do problema, severidade operacional, síntese executiva e recomendações preliminares de resolução.

---

## 🎯 Frase-Problema e Público-Alvo

* **Frase-Problema:** Relatos de incidentes em centrais de suporte chegam com redação heterogénea, ambígua ou prolixa, provocando atrasos na classificação manual, roteamento erróneo de chamados e estouro de SLAs operacionais.
* **Público-Alvo:**
  * Equipes de suporte técnico N1 e N2 (Service Desk / Helpdesk).
  * Gestores de operações de TI focados na triagem primária ágil.
  * Usuários corporativos que demandam encaminhamento imediato e padronizado de incidentes.

---

## 🧠 Justificativa Técnica: LLM vs. Abordagem Determinística Tradicional

| Critério | Abordagem Determinística (Regex / Regras / Palavras-chave) | Abordagem Generativa com LLM (Google Gemini API) |
| :--- | :--- | :--- |
| **Compreensão Semântica** | Rígida; falha diante de erros ortográficos, variações sintáticas, gírias regionais e descrições indiretas. | Profunda; interpreta nuances de linguagem natural, sinonímia e gravidade implícita no contexto. |
| **Contextualização de Incidentes** | Não relaciona causas concorrentes descritas no mesmo chamado. | Capaz de ponderar causas múltiplas e priorizar o evento de maior impacto ao negócio. |
| **Manutenibilidade** | Requer criação e manutenção manual contínua de extensas tabelas de termos e regras booleanas. | Adaptável por meio de engenharia de prompt (Zero-Shot / Few-Shot), sem necessidade de retreino de código de parsing. |
| **Geração de Ação Recomendada** | Limitada a mensagens estáticas previamente cadastradas. | Elabora sínteses dinâmicas e direcionadas com orientações técnicas preliminares contextualizadas. |

---

## 🚧 Limites de Escopo da Entrega

### O que o sistema cobre

* Recepção de relatos textuais livres via interface interativa de linha de comando (CLI).
* Integração direta e parametrizada com o endpoint REST da API Google Gemini (`gemini-3.5-flash-lite`).
* Extração padronizada de quatro entidades obrigatórias: **Categoria**, **Severidade Sugerida**, **Síntese da Falha** e **Ação Recomendada**.
* Observabilidade técnica segura (logging em `logs/app.log`) sem persistência de dados sensíveis ou pessoais (Conformidade com a LGPD).
* Testes unitários determinísticos cobrindo cenários de sucesso, erro de autenticação (HTTP 401) e timeout de rede sem chamadas externas.

### O que não está no escopo

* Persistência de tickets em banco de dados relacional ou noSQL.
* Roteamento e criação automatizada de chamados em plataformas de Service Desk (ex.: Jira Service Management, ServiceNow, Zendesk).
* Aplicação automatizada de scripts de correção no sistema operacional do usuário final.
* Recuperação de informações sobre bases documentais internas proprietárias (RAG - *Retrieval-Augmented Generation*).

---

## 🏛️ Arquitetura Modular e Estrutura de Pastas

O projeto adota uma divisão modular que isola a interface de usuário, as regras de comunicação HTTP e os testes automatizados, utilizando `pathlib` para garantir resolução de caminhos agnóstica de sistema operacional (compatível com Linux, macOS e Windows).

```text
p0-triagem-helpdesk-llm/
│
├── logs/                      # Armazenamento de logs gerados em tempo de execução
│   └── app.log                # Registro técnico operacional em conformidade com LGPD
│
├── src/                       # Módulos principais da aplicação
│   ├── __init__.py            # Inicializador de pacote Python
│   ├── app.py                 # Interface de linha de comando (CLI) e orquestração do fluxo
│   └── client.py              # Cliente HTTP com requests, carregamento de .env e logging
│
├── tests/                     # Bateria de testes automatizados
│   ├── __init__.py            # Inicializador do pacote de testes
│   └── test_client.py         # Testes unitários com requests-mock e isolamento de rede
│
├── .env                       # Variáveis de ambiente locais (ignorado no versionamento)
├── .env.example               # Modelo de referência das variáveis de ambiente exigidas
├── .gitignore                 # Arquivos e pastas excluídos do controle de versão
├── pytest.ini                 # Configuração do executor de testes pytest (pythonpath e logs)
├── README.md                  # Documentação completa de engenharia e reprodução
└── requirements.txt           # Dependências externas do projeto com versões fixadas
```

---

## 🚀 Guia Quick Start Passo a Passo

### Pré-requisitos

* Interpretador **Python 3.10+** instalado (validado na versão Python 3.12.3).
* Gerenciador de versão **Git** configurado.
* Chave de API ativa do **Google AI Studio** ([Obtenha sua chave aqui](https://aistudio.google.com/)).

---

### 1. Clonagem do Repositório

```bash
git clone [https://github.com/andressasouza98/p0-triagem-helpdesk-llm.git](https://github.com/andressasouza98/p0-triagem-helpdesk-llm.git)
cd p0-triagem-helpdesk-llm
```

---

### 2. Criação e Ativação do Ambiente Virtual (`.venv`)

* **No Windows (Git Bash):**

  ```bash
  python -m venv .venv
  source .venv/Scripts/activate
  ```

* **No Windows (PowerShell):**

  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```

* **No Linux / macOS (Bash ou Zsh):**

  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

---

### 3. Instalação das Dependências

```bash
pip install -r requirements.txt
```

---

### 4. Configuração das Variáveis de Ambiente

Copie o arquivo de exemplo para gerar seu arquivo de configuração local:

```bash
cp .env.example .env
```

Abra o arquivo `.env` gerado e preencha a sua credencial:

```env
# ==============================================================================
# CREDENCIAIS DE ACESSO
# ==============================================================================
LLM_API_KEY=sua_chave_real_aqui

# ==============================================================================
# ENDPOINT E MODELO
# ==============================================================================
LLM_MODEL_NAME=gemini-3.5-flash-lite
LLM_API_VERSION=v1beta

# ==============================================================================
# PARÂMETROS DE INFERÊNCIA E RESILIÊNCIA
# ==============================================================================
LLM_MAX_TOKENS=500
LLM_TEMPERATURE=0.2
LLM_TIMEOUT=30
```

| Variável | Descrição Técnica | Valor Padrão |
| :--- | :--- | :--- |
| `LLM_API_KEY` | Chave de autenticação gerada no Google AI Studio. | `Obrigatória` |
| `LLM_MODEL_NAME` | Identificador do modelo de linguagem utilizado. | `gemini-3.5-flash-lite` |
| `LLM_API_VERSION` | Versão da API REST do Google Generative Language. | `v1beta` |
| `LLM_MAX_TOKENS` | Limite máximo de tokens gerados na resposta. | `500` |
| `LLM_TEMPERATURE` | Grau de aleatoriedade da amostragem (baixo para manter determinismo). | `0.2` |
| `LLM_TIMEOUT` | Tempo limite em segundos para requisições de rede HTTP. | `30` |

---

## 💻 Instruções de Execução

### Execução da Aplicação Interativa (CLI)

Com o ambiente virtual ativado, execute o módulo `src.app`:

```bash
python -m src.app
```

**Exemplo de Execução no Terminal:**

```text
Informe o relato do chamado de suporte:
> A impressora térmica do setor de expedição parou de imprimir as etiquetas de envio.

Processando chamado com inteligência artificial... Aguarde...

==================================================
              RESULTADO DA TRIAGEM
==================================================

CATEGORIA:
Hardware

SEVERIDADE SUGERIDA:
Média

SÍNTESE DA FALHA:
Parada funcional da impressora térmica no setor de expedição, impedindo a emissão de etiquetas de envio.

AÇÃO RECOMENDADA:
Verificar a conexão física dos cabos de energia e USB/rede, checar o status da fila de impressão no sistema operacional e confirmar se há erro de atolamento de papel ou falta de suprimento (ribbon/etiquetas) no equipamento.

==================================================
```

---

### Execução da Suíte de Testes Offline

A suíte de testes unitários foi construída utilizando `pytest` e `requests-mock`, garantindo validação determinística sem requisições reais de rede e sem consumir saldo da API:

```bash
pytest -v
```

**Saída esperada:**

```text
tests/test_client.py::test_chamada_sucesso PASSED                        [ 33%]
tests/test_client.py::test_erro_autenticacao_401 PASSED                  [ 66%]
tests/test_client.py::test_timeout_conexao PASSED                        [100%]

============================== 3 passed in 0.32s ==============================
```

---

## 🔒 Observabilidade e Conformidade LGPD

O sistema implementa rastreabilidade técnica estruturada sem violar a privacidade dos dados:

* **Arquivo gerado:** `logs/app.log` (pasta e arquivo criados via `pathlib.Path`).
* **Dados gravados:** Exclusivamente metadados técnicos operacionais (*timestamp ISO 8601 em UTC, código de status HTTP, latência da chamada em ms, total de caracteres do prompt, modelo utilizado e finish_reason*).
* **Proteção à Privacidade (LGPD):** Nenhum dado pessoal, nome de usuário, endereço IP corporativo, chave de API ou texto original do relato é gravado no disco.

**Exemplo de linha de log gerada:**

```text
2026-11-09T18:58:18Z | INFO | status=200 | latency_ms=1899ms | prompt_chars=1144 | model=gemini-3.5-flash-lite | finish_reason=STOP
```

---

## ⚠️ Limitações Conhecidas do Modelo

1. **Dependência de Conectividade:** A execução requer conexão estável com a internet para alcançar os servidores da Google Generative Language API.
2. **Quotas de Rate Limit:** O uso em planos gratuitos está sujeito a limites de requisições por minuto (RPM) e dia (RPD), podendo gerar erros HTTP 429 em chamadas consecutivas.
3. **Stateless (Sem Memória de Conversação):** O modelo processa cada incidente de forma isolada, não mantendo contexto acumulado entre diferentes execuções.
4. **Alucinação Residual em Cenários Específicos:** Na ausência de manuais proprietários indexados por RAG, o modelo utiliza conhecimento geral pré-treinado, podendo sugerir procedimentos que não correspondam à infraestrutura particular da organização.

---

## 📺 Vídeo de Demonstração

* **Link da Apresentação Técnica:** `[INSERIR_LINK_DO_VIDEO_AQUI]`
