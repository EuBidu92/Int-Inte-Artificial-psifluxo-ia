<div align="center">

# 🧠 PsiFluxo IA

### Assistente inteligente para primeiro contato e triagem administrativa em Psicologia

**MVP v1.0 — arquitetura híbrida com Machine Learning, regras determinísticas e IA generativa via Groq**

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Flask](https://img.shields.io/badge/Flask-3.1.3-black)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.9.0-orange)
![Groq](https://img.shields.io/badge/LLM-Groq-purple)
![Tests](https://img.shields.io/badge/testes-179%20passed-brightgreen)
![Status](https://img.shields.io/badge/status-MVP%20funcional-success)

</div>

---

## 📖 Visão geral

O **PsiFluxo IA** é uma aplicação web desenvolvida para automatizar e organizar o primeiro contato com pessoas interessadas em atendimento psicológico. O sistema combina diferentes estratégias de Inteligência Artificial e regras de negócio para oferecer respostas iniciais, compreender solicitações frequentes e, quando existe interesse explícito em atendimento, conduzir uma coleta estruturada de informações.

O projeto foi desenvolvido como **MVP acadêmico e funcional**. A proposta não é substituir o psicólogo, realizar diagnóstico, avaliação psicológica ou psicoterapia, mas apoiar tarefas administrativas de acolhimento inicial e captação de solicitações.

A versão final utiliza uma **arquitetura híbrida**: mensagens simples e atalhos são tratados localmente; intenções operacionais podem ser reconhecidas por um classificador supervisionado; dúvidas abertas podem ser encaminhadas à Groq; e o fluxo de solicitação de atendimento permanece determinístico e controlado pelo código Python.

---

## 🎯 Problema

Clínicas e profissionais de Psicologia recebem com frequência contatos iniciais semelhantes: dúvidas sobre modalidade, funcionamento, valores, remarcação e interesse em iniciar acompanhamento. Quando todo esse processo é realizado manualmente, podem ocorrer demora nas respostas, repetição de tarefas administrativas, perda de contatos e falta de padronização na coleta de informações.

O PsiFluxo IA busca reduzir esse atrito sem delegar decisões clínicas à Inteligência Artificial.

---

## ✅ Objetivos

O projeto tem como objetivos:

- automatizar parte do primeiro contato administrativo;
- oferecer respostas iniciais mais naturais e úteis;
- reconhecer intenções operacionais recorrentes;
- evitar que saudações e mensagens genéricas sejam classificadas de forma inadequada;
- conduzir um fluxo estruturado de solicitação de atendimento;
- coletar modalidade, período, dia, nome, WhatsApp, e-mail e motivo do contato;
- registrar solicitações em CSV;
- disponibilizar painel administrativo autenticado;
- permitir pesquisa, filtros e exportação dos leads para Excel;
- manter fallback local quando a API de IA generativa não estiver disponível;
- validar o comportamento do sistema com testes automatizados.

---

## ✨ Funcionalidades do MVP

- Interface conversacional web;
- atalhos informativos para ansiedade, depressão, psicoterapia, modalidade e solicitação de atendimento;
- pré-roteamento de saudações e pedidos genéricos;
- detecção explícita de interesse em iniciar atendimento;
- classificação de intenções por Machine Learning;
- conversa livre com LLM via Groq;
- fallback local em caso de indisponibilidade da Groq;
- fluxo determinístico de captação de lead;
- interpretação e validação das respostas do usuário;
- gerenciamento do estado da conversa;
- persistência de leads em CSV;
- registro de classificações e origem da decisão conversacional;
- notificação opcional por e-mail;
- painel administrativo protegido por login;
- mascaramento de WhatsApp e e-mail no painel;
- filtros por modalidade e período;
- busca textual no painel;
- exportação para `.xlsx`;
- testes automatizados com Pytest.

---

## 🧠 Arquitetura de IA

O PsiFluxo não depende de uma única técnica. Cada componente é utilizado onde apresenta maior previsibilidade.

```text
                           USUÁRIO
                              │
                              ▼
                       Interface Flask
                              │
                              ▼
                    Roteador de conversa
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
      Saudação/atalho   Fluxo já ativo   Mensagem livre
             │                │                │
             ▼                ▼                ▼
     Resposta local      Orquestrador      Classificador ML
                              │                │
                              │        confiança suficiente?
                              │          ┌─────┴─────┐
                              │         sim         não
                              │          │           │
                              │          ▼           ▼
                              │    Motor/Regras     Groq
                              │          │           │
                              └──────────┴─────┬─────┘
                                               ▼
                                      Resposta ao usuário
                                               │
                                  interesse em atendimento
                                               ▼
                                      Fluxo determinístico
                                               │
                  modalidade → período → dia → nome → WhatsApp
                           → e-mail → motivo → confirmação
                                               │
                                               ▼
                                      Lead / Dashboard
```

### Por que uma arquitetura híbrida?

O classificador foi treinado para cinco intenções específicas. Mensagens como `Oi`, `Bom dia` ou perguntas amplas não devem ser forçadas artificialmente para uma dessas classes. Por isso, a versão final separa o problema em camadas:

1. **Pré-roteador:** trata saudações, pedidos genéricos e manifestações explícitas de interesse;
2. **Classificador ML:** reconhece intenções operacionais conhecidas;
3. **Groq:** responde dúvidas abertas e conversa livre;
4. **Motor de regras:** controla ações e etapas do processo;
5. **Interpretador:** valida as respostas dentro do fluxo de atendimento.

A LLM pode conversar, mas **não controla diretamente a coleta de dados nem decide etapas sensíveis do fluxo**.

---

## 🤖 Classificador de intenções

O modelo supervisionado utiliza:

- **TF-IDF** para representação dos textos;
- unigramas e bigramas;
- **Regressão Logística** como classificador;
- `class_weight="balanced"`;
- Scikit-Learn;
- persistência com Joblib.

### Intenções treinadas

| Intenção | Exemplo de solicitação |
|---|---|
| `agendamento` | Quero começar terapia |
| `funcionamento` | Como funciona uma sessão? |
| `modalidade` | Tem atendimento online? |
| `remarcacao` | Preciso mudar minha consulta |
| `valores` | Quanto custa o atendimento? |

Para a camada operacional híbrida, uma classificação precisa atingir confiança suficiente para ser utilizada; mensagens fora desse contexto podem seguir para a camada conversacional.

---

## 📊 Base de dados e desempenho do modelo

A base de treinamento utilizada no MVP contém **500 mensagens**, distribuídas de forma balanceada entre as cinco classes.

| Indicador | Resultado |
|---|---:|
| Total de registros | 500 |
| Classes | 5 |
| Registros por classe | 100 |
| Treino | 400 (80%) |
| Teste | 100 (20%) |
| Acurácia | **85%** |
| Precisão macro | **85%** |
| Recall macro | **85%** |
| F1 macro | **85%** |

### Resultados por classe

| Classe | Precisão | Recall | F1-score |
|---|---:|---:|---:|
| Agendamento | 0,95 | 0,95 | 0,95 |
| Funcionamento | 0,88 | 0,75 | 0,81 |
| Modalidade | 0,81 | 0,85 | 0,83 |
| Remarcação | 0,78 | 0,90 | 0,84 |
| Valores | 0,84 | 0,80 | 0,82 |

A matriz de confusão e os registros de métricas estão disponíveis em `resultados/`.

---

## 💬 Groq e IA generativa

A conversa aberta é realizada por meio da API da **Groq**, utilizando o cliente Python compatível com a interface OpenAI.

O modelo é configurável pela variável:

```env
GROQ_MODEL=llama-3.3-70b-versatile
```

Caso outro modelo esteja habilitado para a organização Groq, basta alterar essa variável sem modificar a arquitetura da aplicação.

A camada generativa possui instruções para:

- responder em português brasileiro;
- manter respostas curtas, claras e acolhedoras;
- não diagnosticar;
- não realizar psicoterapia;
- não prescrever medicamentos;
- não inventar valores, horários, endereços ou disponibilidade;
- não solicitar dados pessoais durante a conversa aberta;
- direcionar a coleta de dados ao fluxo determinístico.

Se a chave não estiver configurada ou a chamada externa falhar, o sistema utiliza uma resposta local de fallback.

---

## 🔁 Fluxo de solicitação de atendimento

Quando o sistema identifica interesse explícito em atendimento, a coleta passa a ser controlada pelas regras da aplicação:

```text
Interesse em atendimento
        │
        ▼
Modalidade
        │
        ▼
Período
        │
        ▼
Dia preferido
        │
        ▼
Nome
        │
        ▼
WhatsApp
        │
        ▼
E-mail
        │
        ▼
Motivo do contato
        │
        ▼
Resumo e confirmação
        │
        ▼
Registro do lead
```

Durante esse fluxo, a Groq não assume o controle das etapas. As respostas são interpretadas e validadas por componentes locais.

---

## 🧩 Principais módulos

### `app.py`

Aplicação Flask principal. Gerencia rotas, sessão, autenticação, persistência dos leads, painel administrativo, exportação e integração com a camada conversacional.

### `ia/classificador_ml.py`

Carrega os dados, cria o pipeline TF-IDF + Regressão Logística, treina, avalia, salva e utiliza o modelo de intenções.

### `ia/agente.py`

Representa o estado do atendimento e permite converter o estado entre objeto e dicionário para armazenamento em sessão.

### `ia/interpretador_respostas.py`

Normaliza e valida modalidade, período, dia, nome, WhatsApp, e-mail e motivo conforme a etapa atual.

### `ia/motor_regras.py`

Define a próxima ação do sistema e controla as regras do fluxo determinístico.

### `ia/orquestrador.py`

Integra classificador, interpretador, motor de regras e estado durante os fluxos estruturados.

### `services/roteador_conversa.py`

Trata saudações, pedidos genéricos, atalhos e padrões explícitos de interesse antes do classificador.

### `services/conversacao.py`

É a camada de decisão híbrida. Escolhe entre pré-roteador, fluxo determinístico, classificador ML ou Groq.

### `services/groq_service.py`

Configura a API Groq, monta o histórico recente e aplica instruções de segurança à conversa generativa.

### `services/conhecimento.py`

Mantém respostas controladas, contexto institucional e fallback local.

### `services/busca_atendimento.py`

Módulo auxiliar para busca em uma base estruturada de profissionais. Está presente no projeto e possui testes próprios, mas não é necessário ao fluxo principal do chat nesta versão do MVP.

---

## 📂 Estrutura do projeto

```text
psifluxo_ia/
│
├── app.py
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── .env.example
├── .gitignore
│
├── dados/
│   ├── base_conhecimento.txt
│   ├── classificacoes.csv
│   ├── dados_clinica.json
│   ├── intencoes.csv
│   ├── leads.csv
│   └── profissionais.csv
│
├── ia/
│   ├── agente.py
│   ├── busca.py
│   ├── classificador_ml.py
│   ├── classificador_regras.py
│   ├── grafo.py
│   ├── interpretador_respostas.py
│   ├── motor_regras.py
│   └── orquestrador.py
│
├── services/
│   ├── busca_atendimento.py
│   ├── conhecimento.py
│   ├── conversacao.py
│   ├── groq_service.py
│   └── roteador_conversa.py
│
├── modelos/
│   └── classificador_intencoes.joblib
│
├── resultados/
│   ├── cobertura_testes.txt
│   ├── matriz_confusao.csv
│   ├── metricas_modelo.txt
│   └── resumo_testes.txt
│
├── static/
│   ├── admin.css
│   ├── chat.css
│   └── favicon.ico
│
├── templates/
│   ├── index.html
│   ├── leads.html
│   ├── login.html
│   └── obrigado.html
│
└── testes/
    ├── teste_app_pytest.py
    ├── teste_classificador_ml_pytest.py
    ├── teste_conversacao_hibrida_pytest.py
    ├── teste_groq_service_pytest.py
    ├── teste_interpretador_pytest.py
    ├── teste_motor_regras_pytest.py
    ├── teste_orquestrador_pytest.py
    └── teste_roteador_conversa_pytest.py
```

Arquivos `__pycache__`, `.pytest_cache`, ambientes virtuais e demais artefatos temporários não fazem parte da estrutura lógica do projeto.

---

## 🛠 Tecnologias

| Tecnologia | Uso no projeto |
|---|---|
| Python 3.14 | Linguagem principal |
| Flask 3.1.3 | Aplicação web |
| Flask-Login 0.6.3 | Autenticação administrativa |
| Scikit-Learn 1.9.0 | TF-IDF e Regressão Logística |
| Pandas 3.0.3 | Leitura, análise e exportação de dados |
| NumPy 2.5.1 | Dependência numérica do pipeline |
| Joblib 1.5.3 | Persistência do modelo treinado |
| OpenPyXL 3.1.5 | Exportação para Excel |
| OpenAI Python SDK 2.53.0 | Cliente compatível utilizado para acessar a Groq |
| python-dotenv 1.2.2 | Configuração por variáveis de ambiente |
| HTML / CSS / Jinja | Interface web |
| Pytest 8.4.1 | Testes automatizados |
| pytest-cov 6.2.1 | Medição de cobertura |

---

## 🧪 Testes

A validação final do MVP registrou:

```text
179 passed
0 failed
0 errors
```

A suíte verifica, entre outros pontos:

- rotas Flask e criação da sessão;
- autenticação e logout;
- persistência e exportação de leads;
- integridade da base de 500 mensagens;
- treinamento e carregamento do modelo;
- classificações principais;
- limites de confiança;
- cache do modelo;
- validação de respostas;
- fluxo completo de agendamento;
- motor de regras;
- orquestração;
- saudações e pedidos genéricos;
- prevenção do erro em que `Bom dia` era interpretado como remarcação;
- uso da Groq em mensagens livres;
- garantia de que um fluxo de atendimento já ativo não seja entregue à Groq;
- fallback quando a chave da Groq não está disponível.

### Executar os testes

```bash
python -m pytest
```

### Testes com cobertura

```bash
python -m pytest --cov=app --cov=ia --cov=services --cov-report=term-missing
```

ou, para gerar HTML:

```bash
python -m pytest --cov=app --cov=ia --cov=services --cov-report=html
```

O percentual de cobertura deve ser interpretado em relação à versão e à suíte executadas no momento; os artefatos históricos estão em `resultados/`.

---

## 🚀 Instalação

### 1. Pré-requisitos

- Python compatível com as dependências do projeto;
- conexão com a internet para uso da Groq;
- chave de API Groq para habilitar conversa generativa.

O ambiente final do projeto foi validado em **Python 3.14.6**.

### 2. Criar ambiente virtual

Windows / PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependências

Para execução:

```bash
python -m pip install -r requirements.txt
```

Para desenvolvimento e testes:

```bash
python -m pip install -r requirements-dev.txt
```

---

## ⚙️ Configuração

Copie `.env.example` para `.env` e preencha as variáveis locais.

```env
SECRET_KEY=
ADMIN_USER=
ADMIN_PASS=

EMAIL_REMETENTE=
EMAIL_SENHA=
EMAIL_DESTINATARIO=

GROQ_API_KEY=
GROQ_MODEL=llama-3.3-70b-versatile
```

### Variáveis obrigatórias

- `SECRET_KEY`: chave usada pela sessão Flask;
- `ADMIN_USER`: usuário do painel administrativo;
- `ADMIN_PASS`: senha do painel.

### Variáveis opcionais

- `EMAIL_REMETENTE`, `EMAIL_SENHA` e `EMAIL_DESTINATARIO`: habilitam notificação por e-mail;
- `GROQ_API_KEY`: habilita a camada generativa;
- `GROQ_MODEL`: define o modelo disponível na organização Groq.

Sem `GROQ_API_KEY`, o sistema continua disponível e utiliza fallback local nas situações que dependeriam da camada generativa.

### Gerar uma `SECRET_KEY`

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Nunca publique o arquivo `.env` ou chaves reais no repositório.

---

## ▶️ Execução

### Treinar/recriar o modelo

```bash
python -m ia.classificador_ml
```

O modelo será salvo em:

```text
modelos/classificador_intencoes.joblib
```

### Iniciar a aplicação

```bash
python app.py
```

No ambiente local, acesse:

```text
http://127.0.0.1:5000
```

### Painel administrativo

```text
http://127.0.0.1:5000/login
```

O acesso utiliza `ADMIN_USER` e `ADMIN_PASS` definidos no `.env`.

---

## 📋 Persistência e painel administrativo

O MVP utiliza arquivos CSV para manter baixo o custo e a complexidade de implantação.

O lead contém:

- data;
- nome;
- WhatsApp;
- e-mail;
- motivo;
- modalidade;
- período;
- dia preferido.

No painel, WhatsApp e e-mail são apresentados de forma mascarada. A exportação administrativa gera um arquivo Excel com os registros disponíveis.

`dados/leads.csv` deve ser tratado como dado de execução. Antes de compartilhar publicamente o projeto, remova registros reais ou utilize somente dados fictícios.

---

## 🔒 Segurança e privacidade

O MVP possui algumas medidas de proteção:

- credenciais e chaves fora do código-fonte por meio de `.env`;
- autenticação administrativa com Flask-Login;
- comparação de credenciais com `hmac.compare_digest`;
- cookie de sessão configurado como `HttpOnly` e `SameSite=Lax`;
- mascaramento de telefone e e-mail no painel;
- fluxo generativo instruído a não solicitar dados pessoais;
- coleta de dados pessoais concentrada no fluxo determinístico;
- fallback quando a API externa falha.

### Atenção para produção

A configuração atual é de desenvolvimento local. Antes de implantação pública, recomenda-se:

- HTTPS;
- `SESSION_COOKIE_SECURE=True`;
- servidor WSGI de produção;
- armazenamento persistente apropriado;
- política de retenção e exclusão de dados;
- revisão de conformidade com LGPD;
- controle de acesso mais robusto;
- registro e monitoramento de incidentes;
- avaliação específica das condições de tratamento de dados por serviços externos.

---

## 🩺 Limites clínicos

O PsiFluxo IA foi projetado como **assistente administrativo e informativo de primeiro contato**.

Ele não deve ser utilizado para:

- diagnóstico psicológico ou psiquiátrico;
- avaliação psicológica;
- psicoterapia automatizada;
- prescrição ou recomendação de medicamentos;
- substituição do julgamento de um profissional;
- atendimento de emergências.

A IA generativa recebe instruções explícitas para permanecer dentro desses limites.

---

## 📌 Limitações do MVP

- armazenamento principal em CSV;
- execução local pelo servidor de desenvolvimento Flask;
- ausência de integração nativa com WhatsApp Business;
- ausência de agenda eletrônica integrada ao fluxo principal;
- ausência de banco de dados relacional;
- autenticação administrativa simples;
- qualidade do classificador condicionada à base de 500 exemplos;
- dependência externa da Groq para conversa generativa, embora exista fallback local.

---

## 🔮 Possíveis evoluções

Fora do escopo do MVP entregue, o projeto pode evoluir com:

- PostgreSQL ou outro banco relacional;
- integração com Google Calendar;
- WhatsApp Business API;
- API REST;
- Docker;
- CI/CD;
- gestão de permissões e múltiplos usuários;
- métricas de uso em tempo real;
- observabilidade e monitoramento;
- ampliação e avaliação contínua da base de intenções;
- RAG sobre informações institucionais validadas;
- implantação pública com infraestrutura adequada.

---

## 📈 Status

**MVP v1.0 funcional e validado.**

Marcos da versão:

- 500 mensagens na base do classificador;
- 5 intenções balanceadas;
- 85% de acurácia no conjunto de teste;
- arquitetura híbrida ML + regras + Groq;
- fluxo completo de captação de lead;
- painel administrativo;
- exportação Excel;
- **179 testes automatizados aprovados** na validação final.

---

## 👨‍💻 Autor

**Jader Gonçalves dos Santos**

Projeto desenvolvido no contexto de formação em **Desenvolvimento de Aplicações para Inteligência Artificial**, articulando conhecimentos de tecnologia e Psicologia.

---

## 📄 Observação sobre licença

Nenhum arquivo de licença foi incluído nesta versão do MVP. Caso o projeto seja publicado em repositório público, escolha e adicione uma licença compatível com a forma de distribuição desejada.
