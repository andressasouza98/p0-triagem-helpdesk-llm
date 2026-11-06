# 🛠️ Sistema de Triagem e Classificação de Chamados (Help Desk)

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![API REST](https://img.shields.io/badge/integration-REST%20HTTP-green.svg)](https://requests.readthedocs.io/)
[![Google Gemini](https://img.shields.io/badge/LLM-Gemini%20Flash-orange.svg)](https://ai.google.dev/)
[![Marco](https://img.shields.io/badge/milestone-p0--basico-success.svg)](#-status-do-marco)

Aplicação utilitária de linha de comando (CLI) desenvolvida em Python para padronizar, categorizar e priorizar relatos informais de falhas de TI enviados por colaboradores corporativos. O sistema consome diretamente a API REST do Google Gemini (sem uso de SDKs intermediários proprietários), transformando textos livres e ambíguos em fichas operacionais estruturadas para equipes de Suporte Técnico N1.

---

## 🎯 Problema e Valor da Solução

> **Definição Canônica:**  
> *"Uma pessoa que realiza atendimento de suporte técnico interno precisa transformar relatos livres e informais de incidentes em um resumo operacional padronizado com categoria, severidade e síntese da falha, porque atualmente enfrenta perda de tempo interpretando textos confusos ou redundantes para conseguir abrir chamados no sistema."*

### Por que usar LLM em vez de regras determinísticas?

Regras estáticas baseadas em *Regex*, `if/else` ou busca por palavras-chave mostram-se ineficazes porque:

1. **Variabilidade Vocabular:** Usuários leigos descrevem o mesmo problema de dezenas de formas diferentes ("tela preta", "não dá sinal", "monitor não acende", "computador apagou").
2. **Inferência de Gravidade por Contexto:** A criticidade de um chamado depende do contexto de negócio exposto no texto (ex.: *"tenho folhas de pagamento para emitir em 1 hora"* qualifica o incidente como Alta/Crítica), nuance que regras fixas não compreendem.
3. **Poder de Síntese:** Modelos de linguagem conseguem extrair a causa raiz em uma única oração técnica limpa, eliminando redundâncias.

---

## 🏗️ Arquitetura do Repositório

O projeto segue padrões de modularidade, separação de configurações e isolamento de dependências:

```text
p0-triagem-helpdesk-llm/
├── .vscode/               # Configuração do interpretador para VS Code
├── logs/                  # Diretório reservado para telemetria operacional
│   └── .gitkeep
├── src/
│   └── app.py             # Interface CLI, validações e integração HTTP REST
├── tests/                 # Diretório estruturado para testes unitários
├── .env.example           # Modelo público das variáveis de ambiente
├── .gitignore             # Regras de exclusão de artefatos e credenciais
├── README.md              # Documentação técnica e guia de execução
└── requirements.txt       # Dependências estritas do projeto


📋 Pré-requisitos
Python: Versão 3.12 ou superior instalada.
Git: Instalado e configurado no sistema.
Chave de API: Chave de acesso emitida no Google AI Studio.
🚀 Guia Quick Start (Instalação e Execução)
Siga o passo a passo abaixo para reproduzir o projeto a partir de um terminal limpo:
1. Clonar o repositório
Bash
git clone https://github.com/SEU-USUARIO/p0-triagem-helpdesk-llm.git
cd p0-triagem-helpdesk-llm
2. Criar e ativar o ambiente virtual isolado (.venv)
Sem Linux/macOS:
Bash
python3 -m venv .venv
source .venv/bin/activate
Sem Windows (Git Bash):
Bash
python -m venv .venv
source .venv/Scripts/activate
Sem Windows (PowerShell):
PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1
(Certifique-se de visualizar o prefixo (.venv) no início da linha de comandos).
3. Instalar as dependências estritas
Bash
pip install -r requirements.txt
4. Configurar as variáveis de ambiente
Copie o template de exemplo e preencha a sua chave de API:
Bash
cp .env.example .env
Edite o arquivo.env recém-criado e insira a sua credencial:
Esse
LLM_API_KEY=sua_chave_real_do_google_ai_studio
LLM_API_URL=https://generativelanguage.googleapis.com/v1beta/models
LLM_MODEL_NAME=gemini-1.5-flash
LLM_MAX_TOKENS=500
LLM_TEMPERATURE=0.2
5. Executar a aplicação
Execute a aplicação via terminal como módulo Python:
Bash
python -m src.app
💻 Exemplo Prático de Uso
Entrada (Relato informal fornecido pelo usuário no terminal):
Texto
Olá suporte, preciso de ajuda com urgência. Cheguei hoje de manhã no setor financeiro e meu computador liga, as luzes acendem, mas o monitor fica piscando uma luz laranja e a tela fica preta sem sinal de imagem nenhum. Já tentei mexer nos cabos pretos atrás dele e nada. Não consigo abrir o faturamento e temos folhas de pagamento para emitir hoje até as 12h!
Saída Estruturada Gerada pela Aplicação:
Texto
================ RESULTADO DA TRIAGEM ================
CATEGORIA: Hardware
SEVERIDADE SUGERIDA: Alta
SÍNTESE DA FALHA: Computador liga normalmente, mas não transmite sinal de vídeo para o monitor.
AÇÃO RECOMENDADA: Verificar fixação e integridade dos cabos de vídeo (HDMI/DisplayPort) ou testar o monitor em outra estação.
======================================================
🔒 Segurança, Privacidade e Gestão de Segredos
Exclusão de Credenciais: O arquivo .env está explicitamente listado no .gitignore e nunca é comitado no repositório.
Isolamento de Variáveis: O código consome variáveis via python-dotenveos.getenv(), sem chaves hardcoded no código-fonte.
Transparência de Configuração: O arquivo .env.exemplo fornece os contratos necessários para execução sem expor credenciais reais.
Tratamento Seguro de Falhas: Erros de autenticação (HTTP 401/403) ou transporte de rede são interceptados cirurgicamente, retornando mensagens claras sem expor chaves ou exibir stacktraces técnicos brutos.
## 📌 Status do Marco

Nível Básico (p0-básico): Fluxo CLI mínimo funcional de ponta a ponta, integração REST pura e isolamento com .venv.

Nível Intermediário (p0-intermediário): Refatoração modular (src/client.py) e tratamento defensivo via Pull Request.

Nível Avançado (avanço p0): Logging operacional auditado (LGPD) e testes 100% offline via pytestesolicitações-simulação.
Código
---

# 2. Passo a Passo em Git para Fechamento do Marco `p0-basico`

Execute a sequência de comandos abaixo no seu terminal **Git Bash** para registrar as alterações, criar a tag oficial e enviá-las ao repositório remoto.

### Passo 2.1: Verificar integridade dos arquivos
Certifique-se de que o arquivo `.env` **não** consta na lista de arquivos rastreados:
```bash
git status
(O retorno deve listar apenas README.md e eventuais arquivos modificados, com o .env devidamente ignorado).
