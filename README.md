# 🛠️ Sistema de Triagem e Classificação de Chamados (Help Desk)

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![API REST](https://img.shields.io/badge/integration-REST%20HTTP-green.svg)](https://requests.readthedocs.io/)
[![Google Gemini](https://img.shields.io/badge/LLM-Gemini%20Flash%20Lite-orange.svg)](https://ai.google.dev/)
[![Marco](https://img.shields.io/badge/milestone-p0--intermediario-success.svg)](#-status-dos-marcos-do-projeto)

Aplicação utilitária de linha de comando (CLI) desenvolvida em Python para padronizar, categorizar e priorizar relatos informais de incidentes de TI enviados por colaboradores corporativos. O sistema consome diretamente a API REST do Google Gemini via `requests` (sem uso de SDKs intermediários proprietários), transformando textos livres e ambíguos em fichas operacionais estruturadas para equipes de Suporte Técnico N1[cite: 17].

---

## 🎯 Problema e Valor da Solução

> **Definição Canônica:**  
> *"Uma pessoa que realiza atendimento de suporte técnico interno precisa transformar relatos livres e informais de incidentes em um resumo operacional padronizado com categoria, severidade, síntese da falha e ação recomendada, porque atualmente enfrenta perda de tempo interpretando textos confusos ou redundantes para conseguir abrir chamados no sistema."*

### Por que usar LLM em vez de regras determinísticas?

1. **Variabilidade Vocabular:** Usuários leigos descrevem o mesmo sintoma de formas imprevisíveis ("tela preta", "não dá sinal", "monitor não acende", "o computador morreu").
2. **Inferência de Gravidade por Contexto:** A criticidade de um chamado depende do contexto de negócio exposto (ex.: *"tenho a folha de pagamento para rodar em 1 hora"* qualifica o incidente como Alta ou Crítica), nuance que regras de *Regex* e palavras-chave não capturam.
3. **Poder de Síntese:** Modelos de linguagem consolidam a causa provável em uma oração técnica limpa e sugerem o primeiro passo de triagem operacional[cite: 17, 18].

---

## 🏗️ Arquitetura do Repositório

O projeto segue princípios rigorosos de desacoplamento, separação de responsabilidades e isolamento de ambiente[cite: 2]:

```text
p0-triagem-helpdesk-llm/
├── .vscode/               # Configuração do interpretador e ambiente do VS Code
├── logs/                  # Diretório reservado para telemetria operacional
│   └── .gitkeep
├── src/
│   ├── __pycache__/
│   ├── app.py             # Camada CLI: interface, validação defensiva e formatação
│   └── client.py          # Camada de Integração: HTTP REST, parâmetros e resiliência
├── tests/                 # Diretório estruturado para suíte de testes unitários
├── .env.example           # Modelo público das variáveis de ambiente exigidas
├── .gitignore             # Regras de exclusão de artefatos, cache e credenciais (.env)
├── README.md              # Documentação técnica e guia de execução
└── requirements.txt       # Dependências estritas do projeto
Divisão de Responsabilidades (Desacoplamento)src/app.py: Responsável exclusivo pela apresentação[cite: 17]. Faz validação preventiva de relatos vazios ou com menos de 10 caracteres, constrói o prompt estruturado de Help Desk[cite: 17, 18] e possui lazy import defensivo do cliente para economizar recursos.   src/client.py: Responsável exclusivo pela integração de rede e conformidade com a API REST[cite: 2]. Carrega e valida configurações de ambiente, autentica requisições via cabeçalho x-goog-api-key, injeta parâmetros de geração (maxOutputTokens, temperature) e intercepta falhas de rede (Timeout, ConnectionError, RequestException) e códigos de status HTTP sem propagar tracebacks no terminal.   📋 Pré-requisitosPython: Versão 3.12 ou superior instalada.Git: Instalado e configurado no terminal.Chave de API: Credencial ativa emitida no Google AI Studio.🚀 Guia Quick Start (Instalação e Execução)Siga os passos abaixo para reproduzir a execução a partir de um terminal limpo:1. Clonar o repositórioBashgit clone [https://github.com/andressasouza98/p0-triagem-helpdesk-llm.git](https://github.com/andressasouza98/p0-triagem-helpdesk-llm.git)
cd p0-triagem-helpdesk-llm
2. Criar e ativar o ambiente virtual isolado (.venv)No Windows (Git Bash):Bashpython -m venv .venv
source .venv/Scripts/activate
No Windows (PowerShell):PowerShellpython -m venv .venv
.\.venv\Scripts\Activate.ps1
No Linux / macOS:Bashpython3 -m venv .venv
source .venv/bin/activate
(Certifique-se de visualizar o prefixo (.venv) no início da linha de comando).3. Instalar as dependências estritasBashpip install -r requirements.txt
4. Configurar as variáveis de ambienteCopie o template de exemplo e preencha a sua credencial real:Bashcp .env.example .env
Edite o arquivo .env recém-criado:Snippet de códigoLLM_API_KEY=sua_chave_real_aqui
LLM_MODEL_NAME=gemini-3.5-flash-lite
LLM_API_VERSION=v1beta
LLM_MAX_TOKENS=500
LLM_TEMPERATURE=0.2
LLM_TIMEOUT=30
5. Executar a aplicaçãoExecute a aplicação como módulo a partir da raiz do projeto:Bashpython -m src.app
💻 Exemplo Prático de UsoEntrada (Relato informal fornecido pelo usuário no terminal):PlaintextOlá suporte, preciso de ajuda com urgência. Cheguei hoje de manhã no setor financeiro e meu computador liga, as luzes acendem, mas o monitor fica piscando uma luz laranja e a tela fica preta sem sinal de imagem nenhum. Já tentei mexer nos cabos pretos atrás dele e nada. Não consigo abrir o faturamento e temos folhas de pagamento para emitir hoje até as 12h!
Saída Estruturada Gerada pela Aplicação:Plaintext==========================================================
                  RESULTADO DA TRIAGEM                    
==========================================================

CATEGORIA:
Hardware

SEVERIDADE SUGERIDA:
Alta

SÍNTESE DA FALHA:
Computador liga normalmente, mas o monitor não recebe sinal de vídeo, permanecendo com tela preta e LED laranja.

AÇÃO RECOMENDADA:
Verificar a conexão e integridade dos cabos de vídeo (HDMI/DisplayPort), testar o monitor em outra tomada/estação ou substituir o cabo de sinal.

==========================================================
🛡️ Resiliência, Segurança e Gestão de SegredosProteção de Segredos: O arquivo .env está estritamente listado no .gitignore. Nenhuma chave de API ou credencial privada é comitada no repositório.Contrato Público: O arquivo .env.example documenta todas as variáveis de controle (LLM_API_KEY, LLM_MODEL_NAME, LLM_API_VERSION, LLM_MAX_TOKENS, LLM_TEMPERATURE, LLM_TIMEOUT) sem conter valores confidenciais.   Autenticação Segura: A chave é trafegada via cabeçalho HTTP x-goog-api-key, impedindo vazamentos em logs de servidor, proxies reversos ou históricos de URL.   Contenção Cirúrgica de Erros:Timeout Controlado: Requisições que ultrapassam 30 segundos são abortadas de forma limpa com mensagem amigável.   Status HTTP Granular: Interceptação contextual de erros 400, 401, 403, 404, 429 e >= 500 com orientações em português.   Zero Traceback Vermelho: Falhas de rede, interrupções com Ctrl + C (KeyboardInterrupt) e respostas inesperadas são capturadas de forma graciosa sem poluir a interface do usuário.   📌 Status dos Marcos do Projeto[x] Nível Básico (p0-basico): Fluxo funcional mínimo de ponta a ponta na CLI, consumo direto da API REST com requests e ambiente isolado com .venv.   [x] Nível Intermediário (p0-intermediario): Desacoplamento arquitetural em src/client.py, validação preventiva de entrada, parametrização dinâmica de geração (temperature, max_tokens), resiliência a timeouts/falhas de conexão e fluxo Git profissional com Pull Request via Squash and Merge[cite: 18].[ ] Nível Avançado (p0-avancado): Sistema de telemetria operacional com logging auditável compatível com a LGPD (logs/app.log), alerta para respostas truncadas (finishReason) e suíte de testes unitários 100% offline com pytest e requests-mock.
