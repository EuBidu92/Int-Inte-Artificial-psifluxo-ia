import re
import unicodedata
from typing import Optional

from ia.agente import EstadoAtendimento


DIAS_SEMANA = {
    "segunda": "segunda-feira",
    "segunda feira": "segunda-feira",
    "terca": "terça-feira",
    "terça": "terça-feira",
    "terca feira": "terça-feira",
    "terça feira": "terça-feira",
    "quarta": "quarta-feira",
    "quarta feira": "quarta-feira",
    "quinta": "quinta-feira",
    "quinta feira": "quinta-feira",
    "sexta": "sexta-feira",
    "sexta feira": "sexta-feira",
    "sabado": "sábado",
    "sábado": "sábado",
    "domingo": "domingo",
}


def remover_acentos(
    texto: str,
) -> str:
    texto_normalizado = unicodedata.normalize(
        "NFKD",
        texto,
    )

    return "".join(
        caractere
        for caractere in texto_normalizado
        if not unicodedata.combining(
            caractere
        )
    )


def normalizar_texto(
    texto: str,
) -> str:
    texto = texto.strip().lower()
    texto = remover_acentos(texto)

    return " ".join(
        texto.split()
    )


def identificar_modalidade(
    texto: str,
) -> Optional[str]:
    texto_normalizado = normalizar_texto(
        texto
    )

    termos_online = {
        "online",
        "on line",
        "remoto",
        "remota",
        "video",
        "videochamada",
        "chamada de video",
        "pela internet",
    }

    termos_presencial = {
        "presencial",
        "consultorio",
        "clinica",
        "no local",
        "pessoalmente",
    }

    if any(
        termo in texto_normalizado
        for termo in termos_online
    ):
        return "online"

    if any(
        termo in texto_normalizado
        for termo in termos_presencial
    ):
        return "presencial"

    return None


def identificar_periodo(
    texto: str,
) -> Optional[str]:
    texto_normalizado = normalizar_texto(
        texto
    )

    if any(
        termo in texto_normalizado
        for termo in {
            "manha",
            "pela manha",
            "de manha",
            "matutino",
        }
    ):
        return "manhã"

    if any(
        termo in texto_normalizado
        for termo in {
            "tarde",
            "pela tarde",
            "de tarde",
            "vespertino",
        }
    ):
        return "tarde"

    if any(
        termo in texto_normalizado
        for termo in {
            "noite",
            "pela noite",
            "a noite",
            "noturno",
        }
    ):
        return "noite"

    return None


def identificar_dia(
    texto: str,
) -> Optional[str]:
    texto_normalizado = normalizar_texto(
        texto
    )

    for termo, dia_padronizado in DIAS_SEMANA.items():
        termo_normalizado = normalizar_texto(
            termo
        )

        if termo_normalizado in texto_normalizado:
            return dia_padronizado

    return None


def identificar_nome(
    texto: str,
) -> Optional[str]:
    """
    Validação simples para nome.
    """

    nome = " ".join(
        texto.strip().split()
    )

    prefixos = [
        "meu nome é ",
        "meu nome e ",
        "eu me chamo ",
        "sou o ",
        "sou a ",
    ]

    nome_normalizado = normalizar_texto(
        nome
    )

    for prefixo in prefixos:
        prefixo_normalizado = normalizar_texto(
            prefixo
        )

        if nome_normalizado.startswith(
            prefixo_normalizado
        ):
            quantidade = len(prefixo)

            nome = nome[quantidade:].strip()
            break

    possui_letra = any(
        caractere.isalpha()
        for caractere in nome
    )

    if len(nome) < 3 or not possui_letra:
        return None

    return nome.title()


def identificar_whatsapp(
    texto: str,
) -> Optional[str]:
    """
    Mantém somente os números e exige
    DDD mais número.
    """

    numeros = "".join(
        caractere
        for caractere in texto
        if caractere.isdigit()
    )

    if numeros.startswith("55") and len(numeros) > 11:
        numeros = numeros[2:]

    if not 10 <= len(numeros) <= 11:
        return None

    return numeros


def identificar_email(
    texto: str,
) -> Optional[str]:
    email = texto.strip().lower()

    padrao = re.compile(
        r"^[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+"
        r"\.[A-Za-z]{2,}$"
    )

    if not padrao.match(email):
        return None

    return email


def identificar_motivo(
    texto: str,
) -> Optional[str]:
    motivo = " ".join(
        texto.strip().split()
    )

    if len(motivo) < 5:
        return None

    return motivo


def atualizar_estado_com_resposta(
    estado: EstadoAtendimento,
    resposta_usuario: str,
) -> dict:
    """
    Interpreta uma resposta conforme
    a etapa atual da conversa.
    """

    if estado.etapa_atual == "perguntar_modalidade":
        modalidade = identificar_modalidade(
            resposta_usuario
        )

        if modalidade is None:
            return {
                "sucesso": False,
                "campo": "modalidade",
                "mensagem": (
                    "Não consegui identificar a modalidade. "
                    "Responda online ou presencial."
                ),
            }

        estado.modalidade = modalidade

        return {
            "sucesso": True,
            "campo": "modalidade",
            "valor": modalidade,
        }

    if estado.etapa_atual == "perguntar_periodo":
        periodo = identificar_periodo(
            resposta_usuario
        )

        if periodo is None:
            return {
                "sucesso": False,
                "campo": "periodo",
                "mensagem": (
                    "Não consegui identificar o período. "
                    "Responda manhã, tarde ou noite."
                ),
            }

        estado.periodo = periodo

        return {
            "sucesso": True,
            "campo": "periodo",
            "valor": periodo,
        }

    if estado.etapa_atual == "perguntar_dia":
        dia = identificar_dia(
            resposta_usuario
        )

        if dia is None:
            return {
                "sucesso": False,
                "campo": "dia_preferido",
                "mensagem": (
                    "Não consegui identificar o dia. "
                    "Informe um dia da semana."
                ),
            }

        estado.dia_preferido = dia

        return {
            "sucesso": True,
            "campo": "dia_preferido",
            "valor": dia,
        }

    if estado.etapa_atual == "perguntar_nome":
        nome = identificar_nome(
            resposta_usuario
        )

        if nome is None:
            return {
                "sucesso": False,
                "campo": "nome",
                "mensagem": (
                    "Não consegui identificar seu nome. "
                    "Informe seu nome completo."
                ),
            }

        estado.nome = nome

        return {
            "sucesso": True,
            "campo": "nome",
            "valor": nome,
        }

    if estado.etapa_atual == "perguntar_whatsapp":
        whatsapp = identificar_whatsapp(
            resposta_usuario
        )

        if whatsapp is None:
            return {
                "sucesso": False,
                "campo": "whatsapp",
                "mensagem": (
                    "O número parece incompleto. "
                    "Informe o WhatsApp com DDD."
                ),
            }

        estado.whatsapp = whatsapp

        return {
            "sucesso": True,
            "campo": "whatsapp",
            "valor": whatsapp,
        }

    if estado.etapa_atual == "perguntar_email":
        email = identificar_email(
            resposta_usuario
        )

        if email is None:
            return {
                "sucesso": False,
                "campo": "email",
                "mensagem": (
                    "O e-mail parece inválido. "
                    "Digite no formato nome@exemplo.com."
                ),
            }

        estado.email = email

        return {
            "sucesso": True,
            "campo": "email",
            "valor": email,
        }

    if estado.etapa_atual == "perguntar_motivo":
        motivo = identificar_motivo(
            resposta_usuario
        )

        if motivo is None:
            return {
                "sucesso": False,
                "campo": "motivo",
                "mensagem": (
                    "Descreva brevemente o motivo "
                    "da procura por atendimento."
                ),
            }

        estado.motivo = motivo

        return {
            "sucesso": True,
            "campo": "motivo",
            "valor": motivo,
        }

    return {
        "sucesso": False,
        "campo": None,
        "mensagem": (
            "O sistema não está aguardando "
            "esse tipo de informação."
        ),
    }