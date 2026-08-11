import pytest

from ia.agente import criar_estado_inicial
from ia.motor_regras import (
    definir_proxima_acao,
    fluxo_agendamento,
)


def test_sem_intencao_pede_identificacao() -> None:
    estado = criar_estado_inicial()

    resultado = definir_proxima_acao(estado)

    assert resultado["acao"] == "identificar_intencao"
    assert estado.etapa_atual == "identificar_intencao"


def test_encaminhamento_humano_tem_prioridade() -> None:
    estado = criar_estado_inicial()
    estado.intencao = "agendamento"
    estado.encaminhar_humano = True

    resultado = definir_proxima_acao(estado)

    assert resultado["acao"] == "encaminhar_humano"
    assert estado.etapa_atual == "encaminhamento_humano"


@pytest.mark.parametrize(
    ("intencao", "acao_esperada", "etapa_esperada"),
    [
        (
            "valores",
            "responder_valores",
            "responder_valores",
        ),
        (
            "modalidade",
            "responder_modalidade",
            "responder_modalidade",
        ),
        (
            "funcionamento",
            "responder_funcionamento",
            "responder_funcionamento",
        ),
        (
            "remarcacao",
            "encaminhar_remarcacao",
            "encaminhar_remarcacao",
        ),
    ],
)
def test_intencoes_informativas(
    intencao: str,
    acao_esperada: str,
    etapa_esperada: str,
) -> None:
    estado = criar_estado_inicial()
    estado.intencao = intencao

    resultado = definir_proxima_acao(estado)

    assert resultado["acao"] == acao_esperada
    assert estado.etapa_atual == etapa_esperada
    assert estado.concluido is True


def test_intencao_desconhecida_encaminha_humano() -> None:
    estado = criar_estado_inicial()
    estado.intencao = "outra_intencao"

    resultado = definir_proxima_acao(estado)

    assert resultado["acao"] == "encaminhar_humano"
    assert estado.encaminhar_humano is True
    assert estado.etapa_atual == "encaminhamento_humano"


@pytest.mark.parametrize(
    (
        "atributos",
        "acao_esperada",
        "etapa_esperada",
    ),
    [
        (
            {},
            "perguntar_modalidade",
            "perguntar_modalidade",
        ),
        (
            {
                "modalidade": "online",
            },
            "perguntar_periodo",
            "perguntar_periodo",
        ),
        (
            {
                "modalidade": "online",
                "periodo": "noite",
            },
            "perguntar_dia",
            "perguntar_dia",
        ),
        (
            {
                "modalidade": "online",
                "periodo": "noite",
                "dia_preferido": "quinta-feira",
            },
            "perguntar_nome",
            "perguntar_nome",
        ),
        (
            {
                "modalidade": "online",
                "periodo": "noite",
                "dia_preferido": "quinta-feira",
                "nome": "Maria Silva",
            },
            "perguntar_whatsapp",
            "perguntar_whatsapp",
        ),
        (
            {
                "modalidade": "online",
                "periodo": "noite",
                "dia_preferido": "quinta-feira",
                "nome": "Maria Silva",
                "whatsapp": "71999999999",
            },
            "perguntar_email",
            "perguntar_email",
        ),
        (
            {
                "modalidade": "online",
                "periodo": "noite",
                "dia_preferido": "quinta-feira",
                "nome": "Maria Silva",
                "whatsapp": "71999999999",
                "email": "maria@email.com",
            },
            "perguntar_motivo",
            "perguntar_motivo",
        ),
    ],
)
def test_etapas_do_fluxo_agendamento(
    atributos: dict[str, str],
    acao_esperada: str,
    etapa_esperada: str,
) -> None:
    estado = criar_estado_inicial()
    estado.intencao = "agendamento"

    for atributo, valor in atributos.items():
        setattr(
            estado,
            atributo,
            valor,
        )

    resultado = fluxo_agendamento(estado)

    assert resultado["acao"] == acao_esperada
    assert estado.etapa_atual == etapa_esperada
    assert estado.pronto_para_envio is False


def test_fluxo_completo_fica_pronto_para_envio() -> None:
    estado = criar_estado_inicial()
    estado.intencao = "agendamento"
    estado.modalidade = "online"
    estado.periodo = "noite"
    estado.dia_preferido = "quinta-feira"
    estado.nome = "Maria Silva"
    estado.whatsapp = "71999999999"
    estado.email = "maria@email.com"
    estado.motivo = (
        "Quero iniciar acompanhamento "
        "por ansiedade."
    )

    resultado = fluxo_agendamento(estado)

    assert resultado["acao"] == "confirmar_envio"
    assert estado.etapa_atual == "confirmar_envio"
    assert estado.pronto_para_envio is True


def test_definir_proxima_acao_chama_fluxo_agendamento() -> None:
    estado = criar_estado_inicial()
    estado.intencao = "agendamento"

    resultado = definir_proxima_acao(estado)

    assert resultado["acao"] == "perguntar_modalidade"
    assert estado.etapa_atual == "perguntar_modalidade"