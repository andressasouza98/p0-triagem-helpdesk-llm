# Relatório de Execução Técnica de Engenharia

**Projeto:** `p0-triagem-helpdesk-llm`

**Autor:** Andressa Alves de Souza

**Data:** 09 de Novembro de 2026

**Repositório:** <https://github.com/andressasouza98/p0-triagem-helpdesk-llm>

## 1. Evolução Incremental por Nível

O desenvolvimento da solução seguiu um ciclo evolutivo estrito, estruturado em três marcos técnicos de engenharia de software:

* **Nível Básico (`p0-basico`):**

  * Estabelecimento do fluxo funcional ponta a ponta consumindo a API Google Generative Language (modelo `gemini-3.5-flash-lite`).

  * Implementação de prompt contextual com diretrizes contratuais estritas para parsing determinístico de quatro entidades operacionais: Categoria, Severidade Sugerida, Síntese da Falha e Ação Recomendada.

  * Validação inicial de execução interativa no terminal.

* **Nível Intermediário (`p0-intermediario`):**

  * Refatoração e desacoplamento arquitetural: isolamento da interface de usuário (`src/app.py`) e da camada de comunicação HTTP (`src/client.py`).

  * Programação defensiva com captura explícita de exceções de transporte (`requests.exceptions.RequestException`, `requests.exceptions.Timeout`), autenticação incorreta (`HTTP 401`) e bloqueio preventivo de entradas vazias ou em branco.

  * Proteção do repositório com `.gitignore` rigoroso e disponibilização de `.env.example` para replicação padronizada de ambiente.

* **Nível Avançado (`p0-avancado`):**

  * Parametrização dinâmica via variáveis de ambiente sem alteração em código-fonte (`LLM_TIMEOUT`, `LLM_MAX_TOKENS`, `LLM_TEMPERATURE`, `LLM_MODEL_NAME`, `LLM_API_VERSION`).

  * Observabilidade estruturada com persistência em `logs/app.log`, implementando manipulação agnóstica de caminhos via `pathlib.Path` compatível com Windows, Linux e macOS.

  * Conformidade estrita com a LGPD: higienização total de logs técnicos, registrando exclusivamente metadados operacionais e descartando qualquer dado de identificação pessoal (PII) ou conteúdo integral de prompts.

  * Construção de suíte de testes unitários offline determinísticos (`tests/test_client.py`) utilizando `pytest` e `requests-mock`, eliminando dependências de rede e consumo de cotas de API em testes.

## 2. Decisões Principais de Engenharia

| \# | Decisão Tomada | Alternativa Considerada | Justificativa Técnica |
| ----- | ----- | ----- | ----- |
| **01** | Consumo REST direto da API via biblioteca `requests` nativa. | Utilização do SDK oficial `google-generativeai`. | O uso de requisições HTTP diretas elimina dependências pesadas, concede controle refinado sobre cabeçalhos e timeouts operacionais, e permite interceptação simples para mocks de testes offline sem introspecção complexa do SDK. |
| **02** | Logging técnico sanitizado em conformidade com a LGPD. | Log completo contendo o prompt e o texto retornado pelo modelo. | O conteúdo de incidentes de helpdesk frequentemente contém nomes, e-mails, números de IP corporativo e dados sensíveis. Restringir os logs a metadados operacionais (*status code*, latência, contagem de caracteres e motivo de finalização) garante auditoria técnica sem risco de vazamento de dados pessoais. |
| **03** | Bateria de testes offline com `requests-mock`. | Testes de integração realizando chamadas reais contra o endpoint da Google. | Testes reais introduzem flakiness decorrente de latência externa, instabilidade de rede e esgotamento de cotas de API (erros 429). O mock a nível de transporte garante determinismo estrito, validação de exceções de borda (timeout e HTTP 401) e execução instantânea em esteiras de CI/CD. |

## 3. Matriz de Testes e Resultados

A matriz abaixo consolida os cenários de validação funcional e defensiva executados na solução:

| Teste | Entrada / Situação | Resultado Esperado | Resultado Obtido |
| ----- | ----- | ----- | ----- |
| **01 (Sucesso - Funcional)** | Relato técnico válido via CLI: *"A impressora térmica do setor de expedição parou de imprimir as etiquetas de envio."* | Retorno HTTP 200, parsing bem-sucedido e exibição dos 4 blocos formatados no console. | Sucesso. Saída estruturada contendo Categoria (Hardware), Severidade (Média), Síntese e Ação Recomendada. |
| **02 (Defensivo - Validação CLI)** | Entrada vazia ou contendo apenas espaços em branco no prompt da CLI. | Bloqueio imediato na camada de interface, impedindo disparo de requisição externa inútil. | Sucesso. Mensagem: *"O relato do chamado não pode estar vazio."* com reexibição do prompt sem onerar a API. |
| **03 (Defensivo - Autenticação 401)** | `LLM_API_KEY` inválida ou expirada simulada na suíte de testes (`test_erro_autenticacao_401`). | Disparo de `ValueError` contextualizado contendo diagnóstico claro, sem vazamento de stack trace ao usuário. | Sucesso. Exceção interceptada e validada via `pytest` com status code 401 reportado claramente. |
| **04 (Resiliência - Timeout de Rede)** | Latência de resposta superior ao `LLM_TIMEOUT` configurado (`test_timeout_conexao`). | Disparo controlado de `RuntimeError` alertando sobre a indisponibilidade ou lentidão do serviço. | Sucesso. Exceção capturada com mensagem amigável orientando verificação de conectividade. |

## 4. Falhas e Limitações Conhecidas

* **Ocorrência de Rate Limit (HTTP 429) e Variação de Latência:**

  * *Contexto e Identificação:* Durante rodadas de testes manuais sequenciais rápidos, observou-se variação de latência (1.2s a 3.8s) e risco de bloqueio por quota de requisições por minuto no tier gratuito do Google AI Studio.

  * *Tratamento Implementado:* Parametrização de timeout explícito no cliente HTTP e tratamento robusto de exceções de transporte na camada de aplicação para evitar travamento da CLI.

  * *Justificativa de Permanência:* A limitação de taxa é intrínseca à modalidade de consumo gratuito da API gerenciada. Em ambiente de produção empresarial, o comportamento é mitigado com a contratação de cotas corporativas pagas, pool de chaves ou fila de mensageria assíncrona com política de *exponential backoff*.

## 5. Uso de Ferramentas de IA no Desenvolvimento

Em conformidade com as diretrizes de integridade e transparência técnica do percurso:

* **Ferramentas Utilizadas:** Google Gemini e VS Code.

* **Tarefas Delegadas:**

  * Apoio na estruturação inicial de expressões regulares e refinamento do prompt contratual do modelo.

  * Sugestão de cenários de teste unitário baseados em fixtures para o `requests-mock`.

  * Rascunho inicial de padronização visual da documentação em Markdown.

* **Partes Aproveitadas:**

  * Esqueleto dos testes unitários com Pytest e formatação de tabelas comparativas.

* **Correções e Refatorações Manuais Realizadas:**

  * Reestruturação completa do sistema de logging em `src/client.py` para adequação às exigências da LGPD, removendo qualquer persistência do corpo bruto de requisição e resposta.

  * Ajuste na resolução de diretórios com `pathlib` para evitar quebras de caminho relativo ao executar módulos a partir de diferentes pastas raiz.

* **Forma de Validação Técnica:**

  * Execução manual e automatizada da suíte de testes (`pytest -v`) no terminal local e inspeção manual dos arquivos gerados em `logs/app.log`.

## 6. Reflexão Final e Desenvolvimento de Competências

* **Principal Aprendizado Técnico:**

  * A integração de Grandes Modelos de Linguagem em sistemas de produção exige rigor de engenharia idêntico ao consumo de qualquer dependência externa crítica. O valor da entrega não reside apenas na inferência do modelo, mas na resiliência da arquitetura, no tratamento defensivo de falhas, na testabilidade offline determinística e na proteção da privacidade dos dados.

* **Competências Mais Desenvolvidas (C01 a C04):**

  * **C01 (Construção de Fluxos com LLM):** Domínio no condicionamento estruturado de modelos fundacionais via prompt engineering para retorno rigoroso de esquemas de dados.

  * **C03 (Engenharia Defensiva e Resiliência):** Implementação de sanitização de entradas, tratamento de códigos HTTP de borda, timeouts configuráveis e suíte de testes desacoplada de rede externa.

* **Ponto de Melhoria para Ciclos Futuros:**

  * Implementação de uma arquitetura baseada em RAG (*Retrieval-Augmented Generation*) acoplada a uma base vetorial local, permitindo que a IA consulte manuais específicos de infraestrutura da empresa antes de inferir a ação recomendada, minimizando qualquer alucinação residual sobre sistemas proprietários.
