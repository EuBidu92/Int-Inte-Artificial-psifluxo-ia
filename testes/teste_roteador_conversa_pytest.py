import pytest

from services.roteador_conversa import (
    identificar_interesse_atendimento,
    identificar_pedido_generico,
    identificar_saudacao,
    responder_atalho,
)


@pytest.mark.parametrize(
    "mensagem",
    [
        "Oi",
        "Olá",
        "Bom dia",
        "Boa tarde",
        "Boa noite",
    ],
)
def test_identificar_saudacoes(
    mensagem: str,
) -> None:
    assert identificar_saudacao(
        mensagem
    ) is True


@pytest.mark.parametrize(
    "mensagem",
    [
        "Gostaria de algumas informações",
        "Quero algumas informações",
        "Queria saber mais",
    ],
)
def test_pedido_generico(
    mensagem: str,
) -> None:
    assert identificar_pedido_generico(
        mensagem
    ) is True


@pytest.mark.parametrize(
    "mensagem",
    [
        "Quero começar terapia",
        "Quero fazer terapia",
        "Gostaria de marcar uma consulta",
        "Preciso de atendimento",
        "Quero um psicólogo",
    ],
)
def test_interesse_em_atendimento(
    mensagem: str,
) -> None:
    assert identificar_interesse_atendimento(
        mensagem
    ) is True


def test_informacao_nao_inicia_atendimento() -> None:
    assert (
        identificar_interesse_atendimento(
            "O que é ansiedade?"
        )
        is False
    )


@pytest.mark.parametrize(
    "atalho",
    [
        "ansiedade",
        "depressao",
        "psicoterapia",
        "online",
        "presencial",
        "agendamento",
    ],
)
def test_atalhos_possuem_resposta(
    atalho: str,
) -> None:
    resposta = responder_atalho(
        atalho
    )

    assert resposta
    assert isinstance(
        resposta,
        str,
    )