from typing import Any

from ia.agente import EstadoAtendimento


def definir_proxima_acao(
    estado: EstadoAtendimento,
) -> dict[str, Any]:
    """
    Decide a próxima ação com base
    nos dados existentes no estado.
    """

    if estado.encaminhar_humano:
        estado.etapa_atual = "encaminhamento_humano"

        return {
            "acao": "encaminhar_humano",
            "mensagem": (
                "Não consegui compreender completamente "
                "sua solicitação. Você pode usar o botão "
                "do WhatsApp para falar com a equipe."
            ),
        }

    if not estado.intencao:
        estado.etapa_atual = "identificar_intencao"

        return {
            "acao": "identificar_intencao",
            "mensagem": "Como posso ajudar você?",
        }

    if estado.intencao == "valores":
        estado.etapa_atual = "responder_valores"
        estado.concluido = True

        return {
            "acao": "responder_valores",
            "mensagem": (
                "Os valores podem variar conforme a modalidade "
                "e a disponibilidade de atendimento social. "
                "Para receber informações específicas, fale "
                "com a equipe pelo WhatsApp."
            ),
        }

    if estado.intencao == "modalidade":
        estado.etapa_atual = "responder_modalidade"
        estado.concluido = True

        return {
            "acao": "responder_modalidade",
            "mensagem": (
                "A clínica oferece atendimento online "
                "e presencial, conforme disponibilidade."
            ),
        }

    if estado.intencao == "funcionamento":
        estado.etapa_atual = "responder_funcionamento"
        estado.concluido = True

        return {
            "acao": "responder_funcionamento",
            "mensagem": (
                "O acompanhamento ocorre em sessões combinadas "
                "entre a pessoa atendida e o profissional. "
                "Frequência, horários e demais condições são "
                "acordados no início do processo."
            ),
        }

    if estado.intencao == "remarcacao":
        estado.etapa_atual = "encaminhar_remarcacao"
        estado.concluido = True

        return {
            "acao": "encaminhar_remarcacao",
            "mensagem": (
                "Para remarcar ou cancelar uma sessão, "
                "entre em contato diretamente com a equipe "
                "responsável pelo seu atendimento."
            ),
        }

    if estado.intencao == "agendamento":
        return fluxo_agendamento(
            estado
        )

    estado.etapa_atual = "encaminhamento_humano"
    estado.encaminhar_humano = True

    return {
        "acao": "encaminhar_humano",
        "mensagem": (
            "Sua solicitação precisa ser verificada "
            "pela equipe responsável."
        ),
    }


def fluxo_agendamento(
    estado: EstadoAtendimento,
) -> dict[str, Any]:
    """
    Executa todas as etapas necessárias
    para enviar uma solicitação de atendimento.
    """

    if not estado.modalidade:
        estado.etapa_atual = "perguntar_modalidade"

        return {
            "acao": "perguntar_modalidade",
            "mensagem": (
                "Você prefere atendimento online "
                "ou presencial?"
            ),
        }

    if not estado.periodo:
        estado.etapa_atual = "perguntar_periodo"

        return {
            "acao": "perguntar_periodo",
            "mensagem": (
                "Qual período é mais adequado: "
                "manhã, tarde ou noite?"
            ),
        }

    if not estado.dia_preferido:
        estado.etapa_atual = "perguntar_dia"

        return {
            "acao": "perguntar_dia",
            "mensagem": (
                "Qual dia da semana é mais adequado "
                "para você?"
            ),
        }

    if not estado.nome:
        estado.etapa_atual = "perguntar_nome"

        return {
            "acao": "perguntar_nome",
            "mensagem": (
                "Agora preciso de alguns dados para enviar "
                "sua solicitação. Qual é o seu nome completo?"
            ),
        }

    if not estado.whatsapp:
        estado.etapa_atual = "perguntar_whatsapp"

        return {
            "acao": "perguntar_whatsapp",
            "mensagem": (
                "Qual é o seu número de WhatsApp com DDD?"
            ),
        }

    if not estado.email:
        estado.etapa_atual = "perguntar_email"

        return {
            "acao": "perguntar_email",
            "mensagem": (
                "Qual é o seu endereço de e-mail?"
            ),
        }

    if not estado.motivo:
        estado.etapa_atual = "perguntar_motivo"

        return {
            "acao": "perguntar_motivo",
            "mensagem": (
                "Em poucas palavras, qual é o principal "
                "motivo da procura por atendimento?"
            ),
        }

    estado.etapa_atual = "confirmar_envio"
    estado.pronto_para_envio = True

    return {
        "acao": "confirmar_envio",
        "mensagem": (
            "Pronto! Reuni todas as informações necessárias. "
            "Confira o resumo abaixo e clique em "
            "“Enviar solicitação” para encaminhar os dados "
            "à equipe responsável."
        ),
    }