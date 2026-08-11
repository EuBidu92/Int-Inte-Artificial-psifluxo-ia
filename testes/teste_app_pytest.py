import csv
from pathlib import Path
from typing import Any

import pytest


# ==========================================================
# FIXTURES
# ==========================================================

@pytest.fixture()
def modulo_app(
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Importa o módulo app com variáveis de ambiente
    fictícias, próprias para os testes.
    """

    monkeypatch.setenv(
        "SECRET_KEY",
        "chave-secreta-exclusiva-dos-testes",
    )
    monkeypatch.setenv(
        "ADMIN_USER",
        "admin_teste",
    )
    monkeypatch.setenv(
        "ADMIN_PASS",
        "senha_teste",
    )
    monkeypatch.setenv(
        "EMAIL_REMETENTE",
        "remetente@teste.com",
    )
    monkeypatch.setenv(
        "EMAIL_SENHA",
        "senha-email-teste",
    )
    monkeypatch.setenv(
        "EMAIL_DESTINATARIO",
        "destino@teste.com",
    )

    import app as aplicacao

    aplicacao.app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SESSION_COOKIE_SECURE=False,
    )

    return aplicacao


@pytest.fixture()
def ambiente_app(
    modulo_app,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Redireciona os arquivos do sistema para
    uma pasta temporária e desativa o e-mail.
    """

    leads_temporario = (
        tmp_path
        / "leads_teste.csv"
    )

    classificacoes_temporario = (
        tmp_path
        / "classificacoes_teste.csv"
    )

    exportacao_temporaria = (
        tmp_path
        / "leads_export_teste.xlsx"
    )

    monkeypatch.setattr(
        modulo_app,
        "LEADS_CSV",
        leads_temporario,
    )

    monkeypatch.setattr(
        modulo_app,
        "CLASSIFICACOES_CSV",
        classificacoes_temporario,
    )

    monkeypatch.setattr(
        modulo_app,
        "EXPORTACAO_XLSX",
        exportacao_temporaria,
    )

    # Impede envio real de e-mail.
    monkeypatch.setattr(
        modulo_app,
        "iniciar_notificacao",
        lambda lead: None,
    )

    cliente = modulo_app.app.test_client()

    return {
        "modulo": modulo_app,
        "cliente": cliente,
        "leads_csv": leads_temporario,
        "classificacoes_csv": classificacoes_temporario,
        "exportacao_xlsx": exportacao_temporaria,
    }


@pytest.fixture()
def cliente(ambiente_app):
    return ambiente_app["cliente"]


# ==========================================================
# FUNÇÕES AUXILIARES DOS TESTES
# ==========================================================

def fazer_login(
    cliente,
    usuario: str = "admin_teste",
    senha: str = "senha_teste",
):
    return cliente.post(
        "/login",
        data={
            "username": usuario,
            "password": senha,
        },
        follow_redirects=True,
    )


def criar_estado_completo(
    modulo_app,
) -> dict[str, Any]:
    """
    Cria um estado pronto para envio,
    sem depender do classificador.
    """

    estado = modulo_app.estado_de_dict(
        None
    )

    estado.intencao = "agendamento"
    estado.modalidade = "online"
    estado.periodo = "noite"
    estado.dia_preferido = "quinta-feira"
    estado.nome = "Maria Da Silva"
    estado.whatsapp = "71999999999"
    estado.email = "maria@email.com"
    estado.motivo = (
        "Quero iniciar acompanhamento "
        "por ansiedade."
    )
    estado.etapa_atual = "confirmar_envio"
    estado.pronto_para_envio = True

    return modulo_app.estado_para_dict(
        estado
    )


# ==========================================================
# PÁGINA INICIAL E SESSÃO
# ==========================================================

def test_pagina_inicial_carrega(
    cliente,
) -> None:
    resposta = cliente.get("/")

    assert resposta.status_code == 200
    assert (
        "Saúde Mental Psicologia"
        in resposta.get_data(as_text=True)
    )


def test_pagina_inicial_cria_sessao(
    cliente,
) -> None:
    cliente.get("/")

    with cliente.session_transaction() as sessao:
        assert "historico_chat" in sessao
        assert "estado_atendimento" in sessao
        assert "mostrar_botao_lead" in sessao

        assert (
            sessao["mostrar_botao_lead"]
            is False
        )


def test_post_vazio_redireciona(
    cliente,
) -> None:
    resposta = cliente.post(
        "/",
        data={
            "pergunta": "   ",
        },
        follow_redirects=False,
    )

    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith(
        "/"
    )


def test_limpar_conversa(
    cliente,
) -> None:
    cliente.get("/")

    with cliente.session_transaction() as sessao:
        sessao["historico_chat"] = [
            {
                "tipo": "usuario",
                "texto": "Mensagem de teste",
            }
        ]

    resposta = cliente.get(
        "/limpar",
        follow_redirects=False,
    )

    assert resposta.status_code == 302

    with cliente.session_transaction() as sessao:
        assert "historico_chat" not in sessao
        assert "estado_atendimento" not in sessao
        assert "mostrar_botao_lead" not in sessao


# ==========================================================
# LOGIN, PAINEL E LOGOUT
# ==========================================================

def test_login_invalido(
    cliente,
) -> None:
    resposta = fazer_login(
        cliente,
        usuario="usuario_errado",
        senha="senha_errada",
    )

    pagina = resposta.get_data(
        as_text=True
    )

    assert resposta.status_code == 401

    assert (
        "Usuário ou senha inválidos."
        in pagina
    )


def test_login_valido(
    cliente,
) -> None:
    resposta = fazer_login(
        cliente
    )

    assert resposta.status_code == 200
    assert (
        "Leads"
        in resposta.get_data(as_text=True)
        or "Solicitações"
        in resposta.get_data(as_text=True)
    )


def test_painel_exige_login(
    cliente,
) -> None:
    resposta = cliente.get(
        "/leads",
        follow_redirects=False,
    )

    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]


def test_logout(
    cliente,
) -> None:
    fazer_login(cliente)

    resposta = cliente.get(
        "/logout",
        follow_redirects=False,
    )

    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]

    resposta_painel = cliente.get(
        "/leads",
        follow_redirects=False,
    )

    assert resposta_painel.status_code == 302


# ==========================================================
# PROCESSAMENTO DE MENSAGENS
# ==========================================================

def test_mensagem_e_resposta_entram_no_historico(
    ambiente_app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    modulo = ambiente_app["modulo"]
    cliente_teste = ambiente_app["cliente"]

    def processar_simulado(
        *,
        estado,
        mensagem_usuario: str,
        historico,
        limite_confianca: float,
    ) -> dict[str, Any]:
        estado.intencao = "valores"
        estado.etapa_atual = "responder_valores"
        estado.concluido = True

        return {
            "sucesso": True,
            "acao": "responder_valores",
            "mensagem": (
                "Os valores são informados "
                "pela equipe responsável."
            ),
            "estado": estado,
            "origem": "teste",
        }

    monkeypatch.setattr(
        modulo,
        "processar_conversa",
        processar_simulado,
    )

    resposta = cliente_teste.post(
        "/",
        data={
            "pergunta": (
                "Qual é o valor do atendimento?"
            )
        },
    )

    assert resposta.status_code == 200

    with cliente_teste.session_transaction() as sessao:
        historico = sessao["historico_chat"]

    assert historico[-2] == {
        "tipo": "usuario",
        "texto": (
            "Qual é o valor do atendimento?"
        ),
    }

    assert historico[-1] == {
        "tipo": "bot",
        "texto": (
            "Os valores são informados "
            "pela equipe responsável."
        ),
    }


def test_confirmacao_exibe_resumo(
    ambiente_app,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    modulo = ambiente_app["modulo"]
    cliente_teste = ambiente_app["cliente"]

    def processar_simulado(
        *,
        estado,
        mensagem_usuario: str,
        historico,
        limite_confianca: float,
    ) -> dict[str, Any]:
        estado.intencao = "agendamento"
        estado.modalidade = "online"
        estado.periodo = "noite"
        estado.dia_preferido = "quinta-feira"
        estado.nome = "Maria Da Silva"
        estado.whatsapp = "71999999999"
        estado.email = "maria@email.com"
        estado.motivo = (
            "Quero atendimento por ansiedade."
        )

        estado.etapa_atual = "confirmar_envio"
        estado.pronto_para_envio = True

        return {
            "sucesso": True,
            "acao": "confirmar_envio",
            "mensagem": (
                "Confira o resumo e envie "
                "a solicitação."
            ),
            "estado": estado,
            "origem": "teste",
        }

    monkeypatch.setattr(
        modulo,
        "processar_conversa",
        processar_simulado,
    )

    resposta = cliente_teste.post(
        "/",
        data={
            "pergunta": (
                "Quero concluir meu atendimento"
            )
        },
    )

    assert resposta.status_code == 200

    pagina = resposta.get_data(
        as_text=True
    )

    assert (
        "Confira o resumo"
        in pagina
    )

    assert (
        "Maria Da Silva"
        in pagina
    )

    assert (
        "online"
        in pagina.lower()
    )

    assert (
        "quinta-feira"
        in pagina.lower()
    )

    assert (
        "maria@email.com"
        in pagina
    )

    with cliente_teste.session_transaction() as sessao:
        assert (
            sessao["mostrar_botao_lead"]
            is True
        )


# ==========================================================
# ENVIO E PERSISTÊNCIA DO LEAD
# ==========================================================

def test_envio_incompleto_retorna_400(
    ambiente_app,
) -> None:
    cliente_teste = ambiente_app["cliente"]

    cliente_teste.get("/")

    resposta = cliente_teste.post(
        "/enviar_solicitacao"
    )

    assert resposta.status_code == 400
    assert (
        "ainda não está completa"
        in resposta.get_data(as_text=True)
    )


def test_envio_salva_lead_no_csv(
    ambiente_app,
) -> None:
    modulo = ambiente_app["modulo"]
    cliente_teste = ambiente_app["cliente"]
    leads_csv = ambiente_app[
        "leads_csv"
    ]

    cliente_teste.get("/")

    with cliente_teste.session_transaction() as sessao:
        sessao["estado_atendimento"] = (
            criar_estado_completo(
                modulo
            )
        )
        sessao["mostrar_botao_lead"] = True

    resposta = cliente_teste.post(
        "/enviar_solicitacao"
    )

    assert resposta.status_code == 200
    assert leads_csv.exists()

    with leads_csv.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as arquivo:
        linhas = list(
            csv.DictReader(arquivo)
        )

    assert len(linhas) == 1

    lead = linhas[0]

    assert lead["Nome"] == "Maria Da Silva"
    assert lead["WhatsApp"] == "71999999999"
    assert lead["Email"] == "maria@email.com"
    assert lead["Preferencia"] == "online"
    assert lead["Periodo"] == "noite"
    assert (
        lead["DiaPreferido"]
        == "quinta-feira"
    )


def test_envio_limpa_sessao(
    ambiente_app,
) -> None:
    modulo = ambiente_app["modulo"]
    cliente_teste = ambiente_app["cliente"]

    cliente_teste.get("/")

    with cliente_teste.session_transaction() as sessao:
        sessao["estado_atendimento"] = (
            criar_estado_completo(
                modulo
            )
        )
        sessao["historico_chat"] = [
            {
                "tipo": "usuario",
                "texto": "Teste",
            }
        ]
        sessao["mostrar_botao_lead"] = True

    resposta = cliente_teste.post(
        "/enviar_solicitacao"
    )

    assert resposta.status_code == 200

    with cliente_teste.session_transaction() as sessao:
        assert "historico_chat" not in sessao
        assert "estado_atendimento" not in sessao
        assert "mostrar_botao_lead" not in sessao


def test_csv_nao_repete_cabecalho(
    ambiente_app,
) -> None:
    modulo = ambiente_app["modulo"]
    leads_csv = ambiente_app[
        "leads_csv"
    ]

    estado_dict = criar_estado_completo(
        modulo
    )

    estado = modulo.estado_de_dict(
        estado_dict
    )

    lead = modulo.criar_lead_do_estado(
        estado
    )

    modulo.salvar_lead_csv(lead)
    modulo.salvar_lead_csv(lead)

    with leads_csv.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as arquivo:
        linhas = list(
            csv.reader(arquivo)
        )

    assert linhas[0] == modulo.CABECALHO_LEADS
    assert len(linhas) == 3


# ==========================================================
# PAINEL E EXPORTAÇÃO
# ==========================================================

def test_painel_lista_lead(
    ambiente_app,
) -> None:
    modulo = ambiente_app["modulo"]
    cliente_teste = ambiente_app["cliente"]

    estado = modulo.estado_de_dict(
        criar_estado_completo(
            modulo
        )
    )

    lead = modulo.criar_lead_do_estado(
        estado
    )

    modulo.salvar_lead_csv(lead)

    fazer_login(
        cliente_teste
    )

    resposta = cliente_teste.get(
        "/leads"
    )

    pagina = resposta.get_data(
        as_text=True
    )

    assert resposta.status_code == 200
    assert "Maria Da Silva" in pagina
    assert "online" in pagina
    assert "noite" in pagina


def test_exportacao_sem_leads_retorna_404(
    ambiente_app,
) -> None:
    cliente_teste = ambiente_app["cliente"]

    fazer_login(
        cliente_teste
    )

    resposta = cliente_teste.get(
        "/exportar"
    )

    assert resposta.status_code == 404
    assert (
        "Nenhum lead encontrado"
        in resposta.get_data(as_text=True)
    )


def test_exportacao_excel(
    ambiente_app,
) -> None:
    modulo = ambiente_app["modulo"]
    cliente_teste = ambiente_app["cliente"]

    estado = modulo.estado_de_dict(
        criar_estado_completo(
            modulo
        )
    )

    lead = modulo.criar_lead_do_estado(
        estado
    )

    modulo.salvar_lead_csv(
        lead
    )

    fazer_login(
        cliente_teste
    )

    resposta = cliente_teste.get(
        "/exportar"
    )

    assert resposta.status_code == 200

    assert (
        resposta.headers[
            "Content-Disposition"
        ].startswith("attachment")
    )

    assert (
        "leads_export.xlsx"
        in resposta.headers[
            "Content-Disposition"
        ]
    )