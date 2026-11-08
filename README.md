# 🛠️ Sistema de Triagem e Classificação de Incidentes (Help Desk)

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Google Gemini API](https://img.shields.io/badge/Google%20Gemini-REST%20API-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Requests HTTP](https://img.shields.io/badge/Requests-HTTP%20Resilient-2CA5E0?style=for-the-badge)](https://requests.readthedocs.io/)
[![Milestone](https://img.shields.io/badge/Milestone-p0--intermediario-2ea44f?style=for-the-badge)](#-matriz-de-marcos-do-projeto)

Aplicação utilitária em linha de comando (CLI) desenvolvida em Python para transformar relatos informais de suporte de TI em fichas técnicas operacionais padronizadas. A integração com o modelo de linguagem Google Gemini é realizada diretamente via requisições HTTP REST nativas com a biblioteca `requests`, sem intermediários proprietários, assegurando portabilidade, previsibilidade e resiliência de engenharia.

---

## 📌 Índice

1. [Visão Geral e Problema de Negócio](#-visão-geral-e-problema-de-negócio)
2. [Arquitetura de Software e Modularização](#-arquitetura-de-software-e-modularização)
3. [Segurança e Gestão de Credenciais](#-segurança-e-gestão-de-credenciais)
4. [Tratamento Defensivo de Exceções](#-tratamento-defensivo-de-exceções)
5. [Guia de Instalação e Execução (Quick Start)](#-guia-de-instalação-e-execução-quick-start)
6. [Exemplo Prático de Execução](#-exemplo-prático-de-execução)
7. [Matriz de Marcos do Projeto (PBL)](#-matriz-de-marcos-do-projeto-pbl)

---

## 🎯 Visão Geral e Problema de Negócio

### Definição Canônica
>
> *"Profissionais de atendimento de Help Desk N1 frequentemente perdem tempo decifrando relatos livres, confusos e redundantes enviados por colaboradores corporativos. Esta solução automatiza a extração da falha, a classificação da severidade e a sugestão da ação inicial de atendimento antes da abertura formal do ticket."*

### Por que utilizar LLM em vez de regras estáticas (Regex / `if-else`)?

* **Tratamento de Linguagem Informal:** Usuários leigos descrevem a mesma falha física com jargões distintos (*"computador apagou"*, *"luz laranja piscando"*, *"tela preta sem sinal"*).
* **Interpretação de Criticidade Contextual:** O modelo infere a urgência operacional com base nas regras de negócio (ex.: folha de pagamento bloqueada eleva automaticamente o incidente para severidade Alta ou Crítica).
* **Síntese Operacional:** O modelo condensa o cerne técnico do problema em uma frase direta e orienta a intervenção física imediata recomendada para o técnico de N1.

---

## 🏛️ Arquitetura de Software e Modularização

O projeto adota o princípio de responsabilidade única (SRP), desacoplando a camada de apresentação da camada de rede e transporte de dados:

```text
p0-triagem-helpdesk-llm/
│
├── .vscode/               # Diretório de configurações locais de desenvolvimento
├── logs/                  # Diretório reservado para telemetria operacional
│   └── .gitkeep
│
├── src/                   # Código-fonte da aplicação
│   ├── __init__.py
│   ├── app.py             # Interface CLI, validação defensiva e formatação
│   └── client.py          # Camada de integração: HTTP REST, parâmetros e resiliência
│
├── tests/                 # Estrutura modular reservada para suíte de testes unitários
├── .env.example           # Contrato público das variáveis de ambiente necessárias
├── .gitignore             # Bloqueio estrito de segredos (.env) e arquivos temporários
├── README.md              # Documentação técnica integral da aplicação
└── requirements.txt       # Dependências estritas e reproduzíveis do projeto
```

### Divisão de Responsabilidades

| Componente | Responsabilidade Principal | Mecanismos Implementados |
| :--- | :--- | :--- |
| **`src/app.py`** | Apresentação e Interação com Usuário | Entrada e saída via CLI; validação defensiva (tamanho mínimo $\ge 10$ caracteres); bloqueio preventivo de strings vazias; captura graciosa de `KeyboardInterrupt` (`Ctrl + C`); *lazy import* defensivo de `src.client`. |
| **`src/client.py`** | Integração e Comunicação HTTP | • Resolução de caminhos agnósticos via `pathlib.Path`.<br>• Autenticação segura pelo cabeçalho `x-goog-api-key`.<br>• Injeção de parâmetros (`maxOutputTokens`, `temperature`).<br>• Timeouts explícitos configurados.<br>• Tratamento granular de códigos HTTP e exceções de rede. |

---

## 🔒 Segurança e Gestão de Credenciais

* **Isolamento de Segredos:** A chave de API nunca é gravada no código nem adicionada ao Git. O arquivo `.env` é protegido pelo `.gitignore`.
* **Contrato de Ambiente:** O repositório fornece o arquivo `.env.example` higienizado com os padrões funcionais do serviço.
* **Autenticação em Cabeçalho:** A chave trafega estritamente via header HTTP `x-goog-api-key`, evitando exposição em logs de URL, proxies corporativos ou histórico de roteamento.

---

## 🛡️ Tratamento Defensivo de Exceções

O módulo de integração foi desenhado com barreiras de contenção que evitam a propagação de *tracebacks* brutos para o terminal do usuário:

* **Validação de Configuração:** Valida tipos numéricos e intervalos para `LLM_MAX_TOKENS`, `LLM_TEMPERATURE` e `LLM_TIMEOUT`.
* **Timeout Explícito:** Interrupção controlada de requisições que excedam o limite estabelecido (padrão: 30s), exibindo mensagem em português.
* **Falhas de Conectividade:** Captura cirúrgica de `requests.exceptions.ConnectionError` e `requests.exceptions.Timeout`.
* **Diagnóstico Semântico de Erros HTTP:** Tratamento com retornos orientativos para respostas:
  * `400`: Parâmetros ou payload malformatado.
  * `401`: Chave de API inválida, ausente ou expirada.
  * `403`: Restrição de permissão de acesso ao modelo ou projeto.
  * `404`: Modelo ou versão de endpoint não localizada.
  * `429`: Limite de cota de requisições excedido.
  * `>= 500`: Instabilidade temporária dos servidores externos.

---

## 🚀 Guia de Instalação e Execução (Quick Start)

### 1. Clonar o Repositório

```bash
git clone https://github.com/andressasouza98/p0-triagem-helpdesk-llm.git
cd p0-triagem-helpdesk-llm
```

### 2. Configurar o Ambiente Virtual Isolado (`.venv`)

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

* **No Linux / macOS:**

  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 3. Instalar as Dependências Estritas

```bash
pip install -r requirements.txt
```

### 4. Configurar as Variáveis de Ambiente

Copie o template modelo para criar seu arquivo de execução local:

```bash
cp .env.example .env
```

Edite o arquivo `.env` gerado e preencha a sua credencial emitida pelo Google AI Studio:

```env
LLM_API_KEY=coloque_aqui_sua_chave_real
LLM_MODEL_NAME=gemini-3.5-flash-lite
LLM_API_VERSION=v1beta
LLM_MAX_TOKENS=500
LLM_TEMPERATURE=0.2
LLM_TIMEOUT=30
```

### 5. Executar a Aplicação

Inicie a CLI a partir da raiz do repositório:

```bash
python -m src.app
```

---

## 💻 Exemplo Prático de Execução

### Entrada Fornecida via Terminal

```text
Olá suporte, preciso de ajuda com urgência. Cheguei hoje de manhã no setor financeiro e meu computador liga, as luzes acendem, mas o monitor fica piscando uma luz laranja e a tela fica preta sem sinal de imagem nenhum. Já tentei mexer nos cabos pretos atrás dele e nada. Não consigo abrir o faturamento e temos folhas de pagamento para emitir hoje até as 12h!
```

### Saída Estruturada Retornada

```text
==========================================================
                  RESULTADO DA TRIAGEM                    
==========================================================

CATEGORIA:
Hardware

SEVERIDADE SUGERIDA:
Alta

SÍNTESE DA FALHA:
Computador inicializa normalmente, porém o monitor permanece sem sinal de vídeo apresentando tela preta e LED laranja piscando.

AÇÃO RECOMENDADA:
Inspecionar a integridade e conexão física dos cabos de vídeo (HDMI/DisplayPort), testar o display em outra estação de trabalho e verificar a fonte de alimentação do monitor.

==========================================================
```

---

## 📊 Matriz de Marcos do Projeto (PBL)

| Nível do Marco | Tag Oficial | Status | Principais Evidências Entregues |
| :--- | :--- | :---: | :--- |
| **Básico** | `p0-basico` | **Concluído** | Fluxo CLI funcional ponta a ponta, integração REST pura sem SDKs e isolamento em ambiente virtual `.venv`. |
| **Intermediário** | `p0-intermediario` | **Concluído** | Desacoplamento entre `app.py` e `client.py`, validações defensivas de entrada, parametrização dinâmica de geração (`temperature`), contenção total de *tracebacks* e fluxo Git com PR via *Squash and Merge*. |
| **Avançado** | `p0-avancado` | *Planejado* | Telemetria e logging estruturado com conformidade à LGPD (`logs/app.log`), detecção de respostas truncadas (`finishReason`) e suíte de testes unitários offline com `pytest` e `requests-mock`. |
