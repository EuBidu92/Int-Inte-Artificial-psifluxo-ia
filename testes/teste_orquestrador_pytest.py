from typing import Any

import pytest

from ia.agente import criar_estado_inicial
from ia.orquestrador import (
    processar_mensagem,
    reiniciar_estado,
)


def classificacao_falsa(
    intencao: str,
    confianca: float = 0.90,
    encaminhar_humano: bool = False,
) -> dict[str, Any]:
    """
    Cria uma resposta simulada do classificador.
    """

    return {
        "intencao": intencao,
        "confianca": confianca,
        "encaminhar_humano": encaminhar_humano,
        "top_3": [
            {
                "intencao": intencao,
                "probabilidade": confianca,
            }
        ],
    }


def test_mensagem_vazia() -> None:
    estado = criar_estado_inicial()

    resultado = processar_mensagem(
        estado=estado,
        mensagem_usuario="   ",
    )

    assert resultado["sucesso"] is False
    assert "escreva uma mensagem" in resultado["mensagem"]
    assert resultado["estado"] is estado


def test_converte_mensagem_nao_string(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    estado = criar_estado_inicial()

    monkeypatch.setattr(
        "ia.orquestrador.classificar_mensagem",
        lambda texto, limite_confianca: (
            classificacao_falsa(
                intencao="valores",
            )
        ),
    )

    resultado = processar_mensagem(
        estado=estado,
        mensagem_usuario=12345,
    )

    assert resultado["sucesso"] is True
    assert resultado["acao"] == "responder_valores"


def test_primeira_mensagem_agendamento(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    estado = criar_estado_inicial()

    def classificador_simulado(
        texto: str,
        limite_confianca: float,
    ) -> dict[str, Any]:
        assert texto == "Quero começar terapia"
        assert limite_confianca == 0.40

        return classificacao_falsa(
            intencao="agendamento",
        )

    monkeypatch.setattr(
        "ia.orquestrador.classificar_mensagem",
        classificador_simulado,
    )

    resultado = processar_mensagem(
        estado=estado,
        mensagem_usuario="Quero começar terapia",
        limite_confianca=0.40,
    )

    assert resultado["sucesso"] is True
    assert resultado["origem_decisao"] == "classificador_ml"
    assert resultado["acao"] == "perguntar_modalidade"
    assert estado.intencao == "agendamento"
    assert estado.etapa_atual == "perguntar_modalidade"
    assert estado.encaminhar_humano is False


@pytest.mark.parametrize(
    (
        "intencao",
        "acao_esperada",
    ),
    [
        (
            "valores",
            "responder_valores",
        ),
        (
            "modalidade",
            "responder_modalidade",
        ),
        (
            "funcionamento",
            "responder_funcionamento",
        ),
        (
            "remarcacao",
            "encaminhar_remarcacao",
        ),
    ],
)
def test_intencoes_informativas(
    monkeypatch: pytest.MonkeyPatch,
    intencao: str,
    acao_esperada: str,
) -> None:
    estado = criar_estado_inicial()

    monkeypatch.setattr(
        "ia.orquestrador.classificar_mensagem",
        lambda texto, limite_confianca: (
            classificacao_falsa(
                intencao=intencao,
            )
        ),
    )

    resultado = processar_mensagem(
        estado=estado,
        mensagem_usuario="Mensagem de teste",
    )

    assert resultado["sucesso"] is True
    assert resultado["origem_decisao"] == "classificador_ml"
    assert resultado["acao"] == acao_esperada
    assert estado.intencao == intencao
    assert estado.concluido is True


def test_baixa_confianca_encaminha_humano(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    estado = criar_estado_inicial()

    monkeypatch.setattr(
        "ia.orquestrador.classificar_mensagem",
        lambda texto, limite_confianca: (
            classificacao_falsa(
                intencao="nao_compreendida",
                confianca=0.20,
                encaminhar_humano=True,
            )
        ),
    )

    resultado = processar_mensagem(
        estado=estado,
        mensagem_usuario="Mensagem ambígua",
    )

    assert resultado["sucesso"] is True
    assert resultado["acao"] == "encaminhar_humano"
    assert estado.encaminhar_humano is True
    assert estado.etapa_atual == "encaminhamento_humano"


def test_resposta_valida_de_modalidade() -> None:
    estado = criar_estado_inicial()
    estado.intencao = "agendamento"
    estado.etapa_atual = "perguntar_modalidade"

    resultado = processar_mensagem(
        estado=estado,
        mensagem_usuario="Prefiro online",
    )

    assert resultado["sucesso"] is True
    assert (
        resultado["origem_decisao"]
        == "interpretador_respostas"
    )
    assert resultado["acao"] == "perguntar_periodo"
    assert resultado["interpretacao"]["sucesso"] is True
    assert resultado["interpretacao"]["campo"] == "modalidade"
    assert estado.modalidade == "online"
    assert estado.etapa_atual == "perguntar_periodo"


def test_resposta_invalida_de_modalidade() -> None:
    estado = criar_estado_inicial()
    estado.intencao = "agendamento"
    estado.etapa_atual = "perguntar_modalidade"

    resultado = processar_mensagem(
        estado=estado,
        mensagem_usuario="Ainda não sei",
    )

    assert resultado["sucesso"] is False
    assert (
        resultado["origem_decisao"]
        == "interpretador_respostas"
    )
    assert resultado["interpretacao"]["sucesso"] is False
    assert resultado["interpretacao"]["campo"] == "modalidade"
    assert estado.modalidade is None
    assert estado.etapa_atual == "perguntar_modalidade"


@pytest.mark.parametrize(
    (
        "etapa",
        "resposta",
        "atributo",
        "valor_esperado",
        "acao_esperada",
    ),
    [
        (
            "perguntar_periodo",
            "Prefiro à noite",
            "periodo",
            "noite",
            "perguntar_dia",
        ),
        (
            "perguntar_dia",
            "Quinta-feira",
            "dia_preferido",
            "quinta-feira",
            "perguntar_nome",
        ),
        (
            "perguntar_nome",
            "Maria da Silva",
            "nome",
            "Maria Da Silva",
            "perguntar_whatsapp",
        ),
        (
            "perguntar_whatsapp",
            "(71) 99999-9999",
            "whatsapp",
            "71999999999",
            "perguntar_email",
        ),
        (
            "perguntar_email",
            "maria@email.com",
            "email",
            "maria@email.com",
            "perguntar_motivo",
        ),
        (
            "perguntar_motivo",
            "Quero acompanhamento por ansiedade.",
            "motivo",
            "Quero acompanhamento por ansiedade.",
            "confirmar_envio",
        ),
    ],
)
def test_etapas_validas_do_fluxo(
    etapa: str,
    resposta: str,
    atributo: str,
    valor_esperado: str,
    acao_esperada: str,
) -> None:
    estado = criar_estado_inicial()
    estado.intencao = "agendamento"

    estado.modalidade = "online"

    if etapa in {
        "perguntar_dia",
        "perguntar_nome",
        "perguntar_whatsapp",
        "perguntar_email",
        "perguntar_motivo",
    }:
        estado.periodo = "noite"

    if etapa in {
        "perguntar_nome",
        "perguntar_whatsapp",
        "perguntar_email",
        "perguntar_motivo",
    }:
        estado.dia_preferido = "quinta-feira"

    if etapa in {
        "perguntar_whatsapp",
        "perguntar_email",
        "perguntar_motivo",
    }:
        estado.nome = "Maria Da Silva"

    if etapa in {
        "perguntar_email",
        "perguntar_motivo",
    }:
        estado.whatsapp = "71999999999"

    if etapa == "perguntar_motivo":
        estado.email = "maria@email.com"

    estado.etapa_atual = etapa

    resultado = processar_mensagem(
        estado=estado,
        mensagem_usuario=resposta,
    )

    assert resultado["sucesso"] is True
    assert resultado["acao"] == acao_esperada

    assert getattr(
        estado,
        atributo,
    ) == valor_esperado


def test_fluxo_completo_por_mensagens(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    estado = criar_estado_inicial()

    monkeypatch.setattr(
        "ia.orquestrador.classificar_mensagem",
        lambda texto, limite_confianca: (
            classificacao_falsa(
                intencao="agendamento",
            )
        ),
    )

    mensagens = [
        (
            "Quero começar terapia",
            "perguntar_modalidade",
        ),
        (
            "Online",
            "perguntar_periodo",
        ),
        (
            "Noite",
            "perguntar_dia",
        ),
        (
            "Quinta-feira",
            "perguntar_nome",
        ),
        (
            "Maria da Silva",
            "perguntar_whatsapp",
        ),
        (
            "71999999999",
            "perguntar_email",
        ),
        (
            "maria@email.com",
            "perguntar_motivo",
        ),
        (
            "Quero acompanhamento por ansiedade.",
            "confirmar_envio",
        ),
    ]

    for mensagem, acao_esperada in mensagens:
        resultado = processar_mensagem(
            estado=estado,
            mensagem_usuario=mensagem,
        )

        assert resultado["sucesso"] is True
        assert resultado["acao"] == acao_esperada

    assert estado.intencao == "agendamento"
    assert estado.modalidade == "online"
    assert estado.periodo == "noite"
    assert estado.dia_preferido == "quinta-feira"
    assert estado.nome == "Maria Da Silva"
    assert estado.whatsapp == "71999999999"
    assert estado.email == "maria@email.com"
    assert (
        estado.motivo
        == "Quero acompanhamento por ansiedade."
    )
    assert estado.pronto_para_envio is True
    assert estado.etapa_atual == "confirmar_envio"


def test_reiniciar_estado() -> None:
    estado = criar_estado_inicial()

    estado.intencao = "agendamento"
    estado.modalidade = "online"
    estado.periodo = "noite"
    estado.dia_preferido = "quinta-feira"
    estado.nome = "Maria Silva"
    estado.whatsapp = "71999999999"
    estado.email = "maria@email.com"
    estado.motivo = "Ansiedade"
    estado.etapa_atual = "confirmar_envio"
    estado.pronto_para_envio = True
    estado.concluido = True
    estado.encaminhar_humano = True

    estado_reiniciado = reiniciar_estado(
        estado
    )

    assert estado_reiniciado is estado
    assert estado.intencao is None
    assert estado.modalidade is None
    assert estado.periodo is None
    assert estado.dia_preferido is None
    assert estado.nome is None
    assert estado.whatsapp is None
    assert estado.email is None
    assert estado.motivo is None
    assert estado.etapa_atual == "inicio"
    assert estado.pronto_para_envio is False
    assert estado.concluido is False
    assert estado.encaminhar_humano is False