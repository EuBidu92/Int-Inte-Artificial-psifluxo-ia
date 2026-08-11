from __future__ import annotations

from typing import Any

from ia.classificador_ml import (
    classificar_mensagem,
)
from ia.motor_regras import (
    definir_proxima_acao,
)
from ia.orquestrador import (
    processar_mensagem,
)
from services.groq_service import (
    responder_com_groq,
)
from services.roteador_conversa import (
    identificar_interesse_atendimento,
    resposta_pre_roteada,
)


ETAPAS_FLUXO_ATIVO = {
    "perguntar_modalidade",
    "perguntar_periodo",
    "perguntar_dia",
    "perguntar_nome",
    "perguntar_whatsapp",
    "perguntar_email",
    "perguntar_motivo",
    "confirmar_envio",
}


INTENCOES_OPERACIONAIS = {
    "agendamento",
    "valores",
    "modalidade",
    "funcionamento",
    "remarcacao",
}


def fluxo_esta_ativo(
    estado: Any,
) -> bool:

    return (
        getattr(
            estado,
            "etapa_atual",
            None,
        )
        in ETAPAS_FLUXO_ATIVO
    )


def iniciar_agendamento(
    estado: Any,
) -> dict[str, Any]:

    estado.intencao = (
        "agendamento"
    )

    estado.encaminhar_humano = (
        False
    )

    estado.etapa_atual = (
        "inicio"
    )

    acao = definir_proxima_acao(
        estado
    )

    return {
        "mensagem": acao[
            "mensagem"
        ],
        "acao": acao[
            "acao"
        ],
        "origem": (
            "interesse_atendimento"
        ),
    }


def processar_conversa(
    *,
    estado: Any,
    mensagem_usuario: str,
    historico: list[dict] | None = None,
    limite_confianca: float = 0.40,
) -> dict[str, Any]:

    mensagem_usuario = str(
        mensagem_usuario
    ).strip()

    if not mensagem_usuario:

        return {
            "mensagem": (
                "Digite uma mensagem "
                "para que eu possa ajudar."
            ),
            "acao": (
                "mensagem_vazia"
            ),
            "origem": (
                "pre_roteador"
            ),
        }

    # ======================================================
    # 1. FLUXO ATIVO
    # ======================================================

    if fluxo_esta_ativo(
        estado
    ):

        resultado = (
            processar_mensagem(
                estado=estado,
                mensagem_usuario=(
                    mensagem_usuario
                ),
                limite_confianca=(
                    limite_confianca
                ),
            )
        )

        resultado[
            "origem"
        ] = (
            "fluxo_deterministico"
        )

        return resultado

    # ======================================================
    # 2. SAUDAÇÕES / PEDIDOS GENÉRICOS
    # ======================================================

    resposta_local = (
        resposta_pre_roteada(
            mensagem_usuario
        )
    )

    if resposta_local:

        return {
            "mensagem": (
                resposta_local[
                    "mensagem"
                ]
            ),
            "acao": (
                resposta_local[
                    "tipo"
                ]
            ),
            "origem": (
                "pre_roteador"
            ),
        }

    # ======================================================
    # 3. INTERESSE CLARO EM ATENDIMENTO
    # ======================================================

    if identificar_interesse_atendimento(
        mensagem_usuario
    ):

        return iniciar_agendamento(
            estado
        )

    # ======================================================
    # 4. CLASSIFICADOR
    # ======================================================

    classificacao = (
        classificar_mensagem(
            mensagem_usuario,
            limite_confianca=(
                limite_confianca
            ),
        )
    )

    intencao = classificacao.get(
        "intencao"
    )

    confianca = float(
        classificacao.get(
            "confianca",
            0.0,
        )
    )

    # Para decisões operacionais exigimos
    # confiança maior que o limite geral.
    limite_operacional = max(
        limite_confianca,
        0.55,
    )

    if (
        intencao
        in INTENCOES_OPERACIONAIS
        and confianca
        >= limite_operacional
    ):

        resultado = (
            processar_mensagem(
                estado=estado,
                mensagem_usuario=(
                    mensagem_usuario
                ),
                limite_confianca=(
                    limite_confianca
                ),
            )
        )

        resultado[
            "origem"
        ] = (
            "classificador_ml"
        )

        return resultado

    # ======================================================
    # 5. CONVERSA LIVRE
    # ======================================================

    resposta = responder_com_groq(
        mensagem_usuario,
        historico=historico,
    )

    return {
        "mensagem": resposta,
        "acao": "conversa_ia",
        "origem": "groq",
        "classificacao": classificacao,
    }