from typing import Any

from ia.agente import EstadoAtendimento
from ia.classificador_ml import classificar_mensagem
from ia.interpretador_respostas import (
    atualizar_estado_com_resposta,
)
from ia.motor_regras import definir_proxima_acao


ETAPAS_QUE_AGUARDAM_RESPOSTA = {
    "perguntar_modalidade",
    "perguntar_periodo",
    "perguntar_dia",
    "perguntar_nome",
    "perguntar_whatsapp",
    "perguntar_email",
    "perguntar_motivo",
}


def processar_mensagem(
    estado: EstadoAtendimento,
    mensagem_usuario: str,
    limite_confianca: float = 0.40,
) -> dict[str, Any]:
    """
    Coordena classificador, interpretador
    e motor de regras.
    """

    if not isinstance(
        mensagem_usuario,
        str,
    ):
        mensagem_usuario = str(
            mensagem_usuario
        )

    mensagem_usuario = mensagem_usuario.strip()

    if not mensagem_usuario:
        return {
            "sucesso": False,
            "mensagem": (
                "Por favor, escreva uma mensagem "
                "para que eu possa ajudar."
            ),
            "estado": estado,
        }

    if estado.etapa_atual in ETAPAS_QUE_AGUARDAM_RESPOSTA:
        interpretacao = atualizar_estado_com_resposta(
            estado,
            mensagem_usuario,
        )

        if not interpretacao["sucesso"]:
            return {
                "sucesso": False,
                "origem_decisao": "interpretador_respostas",
                "interpretacao": interpretacao,
                "mensagem": interpretacao["mensagem"],
                "estado": estado,
            }

        proxima_acao = definir_proxima_acao(
            estado
        )

        return {
            "sucesso": True,
            "origem_decisao": "interpretador_respostas",
            "interpretacao": interpretacao,
            "acao": proxima_acao["acao"],
            "mensagem": proxima_acao["mensagem"],
            "estado": estado,
        }

    classificacao = classificar_mensagem(
        mensagem_usuario,
        limite_confianca=limite_confianca,
    )

    estado.intencao = classificacao["intencao"]

    estado.encaminhar_humano = classificacao[
        "encaminhar_humano"
    ]

    proxima_acao = definir_proxima_acao(
        estado
    )

    return {
        "sucesso": True,
        "origem_decisao": "classificador_ml",
        "classificacao": classificacao,
        "acao": proxima_acao["acao"],
        "mensagem": proxima_acao["mensagem"],
        "estado": estado,
    }


def reiniciar_estado(
    estado: EstadoAtendimento,
) -> EstadoAtendimento:
    estado.intencao = None

    estado.modalidade = None
    estado.periodo = None
    estado.dia_preferido = None

    estado.nome = None
    estado.whatsapp = None
    estado.email = None
    estado.motivo = None

    estado.etapa_atual = "inicio"

    estado.pronto_para_envio = False
    estado.concluido = False
    estado.encaminhar_humano = False

    return estado