import pytest

from ia.agente import criar_estado_inicial
from ia.interpretador_respostas import (
    atualizar_estado_com_resposta,
    identificar_dia,
    identificar_email,
    identificar_modalidade,
    identificar_motivo,
    identificar_nome,
    identificar_periodo,
    identificar_whatsapp,
    normalizar_texto,
)


# ==========================================================
# NORMALIZAÇÃO
# ==========================================================

@pytest.mark.parametrize(
    (
        "entrada",
        "esperado",
    ),
    [
        (
            "Olá, tudo bem?",
            "ola, tudo bem?",
        ),
        (
            "  QUINTA-FEIRA  ",
            "quinta-feira",
        ),
        (
            "Psicóloga",
            "psicologa",
        ),
    ],
)
def test_normalizar_texto(
    entrada: str,
    esperado: str,
) -> None:
    assert (
        normalizar_texto(entrada)
        == esperado
    )


# ==========================================================
# MODALIDADE
# ==========================================================

@pytest.mark.parametrize(
    (
        "entrada",
        "esperado",
    ),
    [
        (
            "Prefiro online",
            "online",
        ),
        (
            "Pode ser por videochamada",
            "online",
        ),
        (
            "Quero atendimento presencial",
            "presencial",
        ),
        (
            "Prefiro ir ao consultório",
            "presencial",
        ),
    ],
)
def test_identificar_modalidade_valida(
    entrada: str,
    esperado: str,
) -> None:
    assert (
        identificar_modalidade(entrada)
        == esperado
    )


@pytest.mark.parametrize(
    "entrada",
    [
        "Não sei",
        "Talvez",
        "Qualquer modalidade",
    ],
)
def test_identificar_modalidade_invalida(
    entrada: str,
) -> None:
    assert (
        identificar_modalidade(entrada)
        is None
    )


# ==========================================================
# PERÍODO
# ==========================================================

@pytest.mark.parametrize(
    (
        "entrada",
        "esperado",
    ),
    [
        (
            "Só posso pela manhã",
            "manhã",
        ),
        (
            "Prefiro à tarde",
            "tarde",
        ),
        (
            "Tenho horário à noite",
            "noite",
        ),
        (
            "Período matutino",
            "manhã",
        ),
        (
            "Período vespertino",
            "tarde",
        ),
        (
            "Horário noturno",
            "noite",
        ),
    ],
)
def test_identificar_periodo(
    entrada: str,
    esperado: str,
) -> None:
    assert (
        identificar_periodo(entrada)
        == esperado
    )


def test_identificar_periodo_invalido() -> None:
    assert (
        identificar_periodo(
            "Qualquer horário serve"
        )
        is None
    )


# ==========================================================
# DIA
# ==========================================================

@pytest.mark.parametrize(
    (
        "entrada",
        "esperado",
    ),
    [
        (
            "segunda",
            "segunda-feira",
        ),
        (
            "terça-feira",
            "terça-feira",
        ),
        (
            "quarta à noite",
            "quarta-feira",
        ),
        (
            "quinta seria melhor",
            "quinta-feira",
        ),
        (
            "sexta",
            "sexta-feira",
        ),
        (
            "sábado pela manhã",
            "sábado",
        ),
        (
            "domingo",
            "domingo",
        ),
    ],
)
def test_identificar_dia(
    entrada: str,
    esperado: str,
) -> None:
    assert (
        identificar_dia(entrada)
        == esperado
    )


def test_identificar_dia_invalido() -> None:
    assert (
        identificar_dia(
            "Ainda não decidi"
        )
        is None
    )


# ==========================================================
# NOME
# ==========================================================

@pytest.mark.parametrize(
    (
        "entrada",
        "esperado",
    ),
    [
        (
            "Jader Gonçalves",
            "Jader Gonçalves",
        ),
        (
            "Meu nome é Maria da Silva",
            "Maria Da Silva",
        ),
        (
            "Eu me chamo João Souza",
            "João Souza",
        ),
    ],
)
def test_identificar_nome_valido(
    entrada: str,
    esperado: str,
) -> None:
    assert (
        identificar_nome(entrada)
        == esperado
    )


@pytest.mark.parametrize(
    "entrada",
    [
        "",
        "12",
        "A",
    ],
)
def test_identificar_nome_invalido(
    entrada: str,
) -> None:
    assert identificar_nome(entrada) is None


# ==========================================================
# WHATSAPP
# ==========================================================

@pytest.mark.parametrize(
    (
        "entrada",
        "esperado",
    ),
    [
        (
            "71999999999",
            "71999999999",
        ),
        (
            "(71) 99999-9999",
            "71999999999",
        ),
        (
            "+55 71 99999-9999",
            "71999999999",
        ),
        (
            "7133334444",
            "7133334444",
        ),
    ],
)
def test_identificar_whatsapp_valido(
    entrada: str,
    esperado: str,
) -> None:
    assert (
        identificar_whatsapp(entrada)
        == esperado
    )


@pytest.mark.parametrize(
    "entrada",
    [
        "123",
        "719999",
        "telefone",
        "",
    ],
)
def test_identificar_whatsapp_invalido(
    entrada: str,
) -> None:
    assert (
        identificar_whatsapp(entrada)
        is None
    )


# ==========================================================
# E-MAIL
# ==========================================================

@pytest.mark.parametrize(
    "entrada",
    [
        "usuario@email.com",
        "nome.sobrenome@gmail.com",
        "usuario+teste@dominio.com.br",
    ],
)
def test_identificar_email_valido(
    entrada: str,
) -> None:
    assert (
        identificar_email(entrada)
        == entrada.lower()
    )


def test_email_e_convertido_para_minusculas() -> None:
    assert (
        identificar_email(
            "Usuario@Email.COM"
        )
        == "usuario@email.com"
    )


@pytest.mark.parametrize(
    "entrada",
    [
        "email",
        "usuario@",
        "@dominio.com",
        "usuario@email",
        "",
    ],
)
def test_identificar_email_invalido(
    entrada: str,
) -> None:
    assert identificar_email(entrada) is None


# ==========================================================
# MOTIVO
# ==========================================================

def test_identificar_motivo_valido() -> None:
    motivo = (
        "Quero iniciar acompanhamento "
        "por causa da ansiedade."
    )

    assert identificar_motivo(motivo) == motivo


@pytest.mark.parametrize(
    "entrada",
    [
        "",
        "oi",
        "não",
    ],
)
def test_identificar_motivo_curto(
    entrada: str,
) -> None:
    assert identificar_motivo(entrada) is None


# ==========================================================
# ATUALIZAÇÃO DO ESTADO
# ==========================================================

def test_atualizar_modalidade_no_estado() -> None:
    estado = criar_estado_inicial()

    estado.etapa_atual = (
        "perguntar_modalidade"
    )

    resultado = atualizar_estado_com_resposta(
        estado,
        "Prefiro online",
    )

    assert resultado["sucesso"] is True
    assert resultado["campo"] == "modalidade"
    assert resultado["valor"] == "online"
    assert estado.modalidade == "online"


@pytest.mark.parametrize(
    (
        "etapa",
        "resposta",
        "campo",
        "valor_esperado",
        "atributo_estado",
    ),
    [
        (
            "perguntar_periodo",
            "Prefiro pela manhã",
            "periodo",
            "manhã",
            "periodo",
        ),
        (
            "perguntar_dia",
            "Quinta-feira",
            "dia_preferido",
            "quinta-feira",
            "dia_preferido",
        ),
        (
            "perguntar_nome",
            "Maria da Silva",
            "nome",
            "Maria Da Silva",
            "nome",
        ),
        (
            "perguntar_whatsapp",
            "(71) 99999-9999",
            "whatsapp",
            "71999999999",
            "whatsapp",
        ),
        (
            "perguntar_email",
            "Maria@Email.com",
            "email",
            "maria@email.com",
            "email",
        ),
        (
            "perguntar_motivo",
            (
                "Quero iniciar acompanhamento "
                "por ansiedade."
            ),
            "motivo",
            (
                "Quero iniciar acompanhamento "
                "por ansiedade."
            ),
            "motivo",
        ),
    ],
)
def test_atualizar_estado_com_respostas_validas(
    etapa: str,
    resposta: str,
    campo: str,
    valor_esperado: str,
    atributo_estado: str,
) -> None:
    estado = criar_estado_inicial()
    estado.etapa_atual = etapa

    resultado = atualizar_estado_com_resposta(
        estado,
        resposta,
    )

    assert resultado["sucesso"] is True
    assert resultado["campo"] == campo
    assert resultado["valor"] == valor_esperado

    assert (
        getattr(
            estado,
            atributo_estado,
        )
        == valor_esperado
    )


@pytest.mark.parametrize(
    (
        "etapa",
        "resposta",
        "campo",
        "atributo_estado",
    ),
    [
        (
            "perguntar_modalidade",
            "Não sei",
            "modalidade",
            "modalidade",
        ),
        (
            "perguntar_periodo",
            "Qualquer hora",
            "periodo",
            "periodo",
        ),
        (
            "perguntar_dia",
            "Ainda não decidi",
            "dia_preferido",
            "dia_preferido",
        ),
        (
            "perguntar_nome",
            "12",
            "nome",
            "nome",
        ),
        (
            "perguntar_whatsapp",
            "12345",
            "whatsapp",
            "whatsapp",
        ),
        (
            "perguntar_email",
            "email inválido",
            "email",
            "email",
        ),
        (
            "perguntar_motivo",
            "oi",
            "motivo",
            "motivo",
        ),
    ],
)
def test_atualizar_estado_com_respostas_invalidas(
    etapa: str,
    resposta: str,
    campo: str,
    atributo_estado: str,
) -> None:
    estado = criar_estado_inicial()
    estado.etapa_atual = etapa

    resultado = atualizar_estado_com_resposta(
        estado,
        resposta,
    )

    assert resultado["sucesso"] is False
    assert resultado["campo"] == campo

    assert (
        getattr(
            estado,
            atributo_estado,
        )
        is None
    )


def test_rejeitar_resposta_invalida_na_etapa() -> None:
    estado = criar_estado_inicial()

    estado.etapa_atual = (
        "perguntar_email"
    )

    resultado = atualizar_estado_com_resposta(
        estado,
        "email inválido",
    )

    assert resultado["sucesso"] is False
    assert resultado["campo"] == "email"
    assert estado.email is None


def test_resposta_em_etapa_nao_reconhecida() -> None:
    estado = criar_estado_inicial()

    estado.etapa_atual = (
        "etapa_inexistente"
    )

    resultado = atualizar_estado_com_resposta(
        estado,
        "Qualquer resposta",
    )

    assert resultado["sucesso"] is False
    assert resultado["campo"] is None

    assert (
        "não está aguardando"
        in resultado["mensagem"]
    )