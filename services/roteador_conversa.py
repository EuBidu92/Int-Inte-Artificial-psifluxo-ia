from __future__ import annotations

import re
import unicodedata

from services.conhecimento import (
    PEDIDO_GENERICO,
    RESPOSTAS_ATALHOS,
    SAUDACAO,
)


def normalizar(
    texto: str,
) -> str:

    texto = (
        str(texto)
        .strip()
        .lower()
    )

    texto = "".join(
        caractere
        for caractere
        in unicodedata.normalize(
            "NFD",
            texto,
        )
        if unicodedata.category(
            caractere
        ) != "Mn"
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto,
    )

    return texto


SAUDACOES = {
    "oi",
    "ola",
    "oie",
    "ola tudo bem",
    "oi tudo bem",
    "bom dia",
    "boa tarde",
    "boa noite",
    "e ai",
    "eai",
}


PEDIDOS_GENERICOS = {
    "gostaria de algumas informacoes",
    "gostaria de informacoes",
    "quero algumas informacoes",
    "quero informacoes",
    "preciso de informacoes",
    "queria algumas informacoes",
    "queria saber mais",
    "quero saber mais",
    "pode me passar informacoes",
    "pode me dar algumas informacoes",
}


PADROES_INTERESSE = (

    r"\bquero comecar terapia\b",

    r"\bquero iniciar terapia\b",

    r"\bquero fazer terapia\b",

    r"\bquero comecar psicoterapia\b",

    r"\bquero iniciar psicoterapia\b",

    r"\bquero marcar uma consulta\b",

    r"\bquero agendar uma consulta\b",

    r"\bquero marcar uma sessao\b",

    r"\bquero agendar uma sessao\b",

    r"\bgostaria de marcar uma consulta\b",

    r"\bgostaria de agendar uma consulta\b",

    r"\bgostaria de iniciar terapia\b",

    r"\bpreciso de atendimento\b",

    r"\bquero atendimento\b",

    r"\bgostaria de atendimento\b",

    r"\bpreciso de um psicologo\b",

    r"\bquero um psicologo\b",

    r"\bcomo faco para agendar\b",

    r"\bcomo faco para marcar\b",
)


def identificar_saudacao(
    texto: str,
) -> bool:

    return (
        normalizar(texto)
        in SAUDACOES
    )


def identificar_pedido_generico(
    texto: str,
) -> bool:

    return (
        normalizar(texto)
        in PEDIDOS_GENERICOS
    )


def identificar_interesse_atendimento(
    texto: str,
) -> bool:

    texto = normalizar(
        texto
    )

    return any(
        re.search(
            padrao,
            texto,
        )
        for padrao
        in PADROES_INTERESSE
    )


def responder_atalho(
    atalho: str,
) -> str | None:

    return RESPOSTAS_ATALHOS.get(
        normalizar(
            atalho
        )
    )


def resposta_pre_roteada(
    texto: str,
) -> dict[str, str] | None:

    if identificar_saudacao(
        texto
    ):

        return {
            "tipo": "saudacao",
            "mensagem": SAUDACAO,
        }

    if identificar_pedido_generico(
        texto
    ):

        return {
            "tipo": (
                "informacao_generica"
            ),
            "mensagem": (
                PEDIDO_GENERICO
            ),
        }

    return None