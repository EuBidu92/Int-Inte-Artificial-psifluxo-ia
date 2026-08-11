from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# ==========================================================
# CARREGAMENTO DO .ENV
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(
    BASE_DIR / ".env"
)

from services.conhecimento import (
    CONTEXTO_CLINICA,
    FALLBACK_LOCAL,
)


logger = logging.getLogger(
    __name__
)


GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile",
)


INSTRUCOES = f"""
Você é a assistente virtual administrativa do PsiFluxo IA.

{CONTEXTO_CLINICA}

REGRAS:

1. Responda em português brasileiro.
2. Seja acolhedora, clara e objetiva.
3. Use respostas curtas, preferencialmente de 1 a 3 parágrafos.
4. Não diagnostique.
5. Não realize psicoterapia.
6. Não prescreva medicamentos.
7. Não diga que alguém possui determinada condição clínica.
8. Não invente valores, horários, endereços ou disponibilidade.
9. Não solicite nome, telefone ou e-mail.
10. Não peça dados pessoais.
11. A coleta de dados é responsabilidade de outro módulo.
12. Quando perceber interesse em atendimento, informe apenas que
    pode ajudar a iniciar a solicitação.
13. Não afirme que substitui acompanhamento profissional.
14. Evite respostas excessivamente técnicas.
15. Não prolongue a conversa desnecessariamente.
"""


def groq_disponivel() -> bool:

    return bool(
        GROQ_API_KEY
    )


def criar_cliente() -> OpenAI:

    return OpenAI(
        api_key=GROQ_API_KEY,
        base_url=(
            "https://api.groq.com/openai/v1"
        ),
    )


def montar_historico(
    historico: list[dict] | None,
) -> str:

    if not historico:
        return ""

    linhas: list[str] = []

    for item in historico[
        -6:
    ]:

        texto = str(
            item.get(
                "texto",
                "",
            )
        ).strip()

        if not texto:
            continue

        tipo = item.get(
            "tipo"
        )

        if tipo == "usuario":
            papel = "Usuário"
        else:
            papel = "Assistente"

        linhas.append(
            f"{papel}: {texto}"
        )

    return "\n".join(
        linhas
    )


def responder_com_groq(
    mensagem: str,
    historico: list[dict] | None = None,
) -> str:

    if not groq_disponivel():

        logger.warning(
            "Groq indisponível: "
            "GROQ_API_KEY não definida."
        )

        return FALLBACK_LOCAL

    try:

        cliente = criar_cliente()

        historico_texto = (
            montar_historico(
                historico
            )
        )

        mensagens = [
            {
                "role": "system",
                "content": INSTRUCOES,
            }
        ]

        if historico_texto:

            mensagens.append(
                {
                    "role": "system",
                    "content": (
                        "Histórico recente "
                        "da conversa:\n"
                        + historico_texto
                    ),
                }
            )

        mensagens.append(
            {
                "role": "user",
                "content": mensagem,
            }
        )

        resposta = (
            cliente.chat.completions.create(
                model=GROQ_MODEL,
                messages=mensagens,
                temperature=0.35,
                max_tokens=350,
            )
        )

        texto = (
            resposta
            .choices[0]
            .message
            .content
        )

        if not texto:
            return FALLBACK_LOCAL

        return texto.strip()

    except Exception:

        logger.exception(
            "Falha ao consultar a Groq."
        )

        return FALLBACK_LOCAL