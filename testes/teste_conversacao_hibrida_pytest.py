from unittest.mock import patch

import pytest

from ia.agente import criar_estado_inicial
from services.conversacao import (
    processar_conversa,
)


def test_oi_usa_pre_roteador() -> None:
    estado = criar_estado_inicial()

    resultado = processar_conversa(
        estado=estado,
        mensagem_usuario="Oi",
        historico=[],
        limite_confianca=0.40,
    )

    assert resultado["origem"] == "pre_roteador"
    assert resultado["acao"] == "saudacao"


def test_bom_dia_nao_vira_remarcacao() -> None:
    estado = criar_estado_inicial()

    resultado = processar_conversa(
        estado=estado,
        mensagem_usuario="Bom dia",
        historico=[],
        limite_confianca=0.40,
    )

    assert resultado["origem"] == "pre_roteador"

    assert resultado["acao"] != (
        "encaminhar_remarcacao"
    )


def test_pedido_generico_nao_inicia_agendamento() -> None:
    estado = criar_estado_inicial()

    resultado = processar_conversa(
        estado=estado,
        mensagem_usuario=(
            "Gostaria de algumas informações"
        ),
        historico=[],
        limite_confianca=0.40,
    )

    assert (
        resultado["origem"]
        == "pre_roteador"
    )

    assert (
        resultado["acao"]
        == "informacao_generica"
    )


def test_interesse_explicito_inicia_agendamento() -> None:
    estado = criar_estado_inicial()

    resultado = processar_conversa(
        estado=estado,
        mensagem_usuario=(
            "Quero começar terapia"
        ),
        historico=[],
        limite_confianca=0.40,
    )

    assert (
        resultado["origem"]
        == "interesse_atendimento"
    )

    assert estado.intencao == "agendamento"

    assert estado.etapa_atual in {
        "perguntar_modalidade",
        "modalidade",
    }


@patch(
    "services.conversacao.responder_com_groq"
)
@patch(
    "services.conversacao.classificar_mensagem"
)
def test_mensagem_livre_usa_groq(
    mock_classificador,
    mock_groq,
) -> None:

    estado = criar_estado_inicial()

    mock_classificador.return_value = {
        "intencao": "nao_compreendida",
        "intencao_prevista": "funcionamento",
        "confianca": 0.31,
        "encaminhar_humano": True,
        "top_3": [],
    }

    mock_groq.return_value = (
        "Resposta natural gerada pela Groq."
    )

    resultado = processar_conversa(
        estado=estado,
        mensagem_usuario=(
            "Tenho ficado ansioso e queria "
            "entender melhor isso."
        ),
        historico=[],
        limite_confianca=0.40,
    )

    assert resultado["origem"] == "groq"
    assert resultado["acao"] == "conversa_ia"

    assert (
        resultado["mensagem"]
        == "Resposta natural gerada pela Groq."
    )

    mock_groq.assert_called_once()


@patch(
    "services.conversacao.responder_com_groq"
)
def test_fluxo_ativo_nao_chama_groq(
    mock_groq,
) -> None:

    estado = criar_estado_inicial()

    estado.intencao = "agendamento"
    estado.etapa_atual = (
        "perguntar_modalidade"
    )

    resultado = processar_conversa(
        estado=estado,
        mensagem_usuario="Online",
        historico=[],
        limite_confianca=0.40,
    )

    assert (
        resultado["origem"]
        == "fluxo_deterministico"
    )

    mock_groq.assert_not_called()