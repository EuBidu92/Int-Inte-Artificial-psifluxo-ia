from __future__ import annotations

import csv
import hmac
import logging
import os
import smtplib
import threading
from dataclasses import dataclass
from datetime import datetime
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from flask import (
    Flask,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from flask_login import (
    LoginManager,
    UserMixin,
    login_required,
    login_user,
    logout_user,
)

from ia.agente import (
    estado_de_dict,
    estado_para_dict,
)
from services.conversacao import (
    processar_conversa,
)
from services.roteador_conversa import (
    responder_atalho,
)


# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DADOS_DIR = BASE_DIR / "dados"

LEADS_CSV = DADOS_DIR / "leads.csv"
CLASSIFICACOES_CSV = (
    DADOS_DIR
    / "classificacoes.csv"
)

EXPORTACAO_XLSX = (
    BASE_DIR
    / "leads_export.xlsx"
)


CABECALHO_LEADS = [
    "Data",
    "Nome",
    "WhatsApp",
    "Email",
    "Motivo",
    "Preferencia",
    "Periodo",
    "DiaPreferido",
]


CABECALHO_CLASSIFICACOES = [
    "data",
    "intencao",
    "etapa",
    "acao",
    "origem",
    "concluido",
    "pronto_para_envio",
]


LIMITE_CONFIANCA = 0.40


SECRET_KEY = os.getenv(
    "SECRET_KEY"
)

ADMIN_USER = os.getenv(
    "ADMIN_USER"
)

ADMIN_PASS = os.getenv(
    "ADMIN_PASS"
)

EMAIL_REMETENTE = os.getenv(
    "EMAIL_REMETENTE"
)

EMAIL_SENHA = os.getenv(
    "EMAIL_SENHA"
)

EMAIL_DESTINATARIO = os.getenv(
    "EMAIL_DESTINATARIO"
)


VARIAVEIS_OBRIGATORIAS = {
    "SECRET_KEY": SECRET_KEY,
    "ADMIN_USER": ADMIN_USER,
    "ADMIN_PASS": ADMIN_PASS,
}


variaveis_ausentes = [
    nome
    for nome, valor
    in VARIAVEIS_OBRIGATORIAS.items()
    if not valor
]


if variaveis_ausentes:
    raise RuntimeError(
        "Variáveis de ambiente obrigatórias "
        "ausentes: "
        + ", ".join(
            variaveis_ausentes
        )
    )


DADOS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger(
    __name__
)


# ==========================================================
# FLASK
# ==========================================================

app = Flask(
    __name__
)


app.config.update(
    SECRET_KEY=SECRET_KEY,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
)


# ==========================================================
# LOGIN
# ==========================================================

login_manager = LoginManager()

login_manager.init_app(
    app
)

login_manager.login_view = (
    "login"
)

login_manager.login_message = (
    "Faça login para acessar "
    "esta página."
)


class User(UserMixin):

    def __init__(
        self,
        user_id: str,
    ) -> None:
        self.id = user_id


@login_manager.user_loader
def load_user(
    user_id: str,
) -> User:
    return User(
        user_id
    )


# ==========================================================
# MODELO DE LEAD
# ==========================================================

@dataclass(
    frozen=True
)
class Lead:

    nome: str
    whatsapp: str
    email: str
    motivo: str
    preferencia: str
    periodo: str
    dia_preferido: str
    data: str

    def para_linha_csv(
        self,
    ) -> list[str]:

        return [
            self.data,
            self.nome,
            self.whatsapp,
            self.email,
            self.motivo,
            self.preferencia,
            self.periodo,
            self.dia_preferido,
        ]


# ==========================================================
# ARQUIVOS
# ==========================================================

def _arquivo_tem_conteudo(
    caminho: Path,
) -> bool:

    return (
        caminho.exists()
        and caminho.stat().st_size > 0
    )


def _validar_cabecalho_csv(
    caminho: Path,
    cabecalho_esperado: list[str],
) -> None:

    if not _arquivo_tem_conteudo(
        caminho
    ):
        return

    with caminho.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as arquivo:

        leitor = csv.reader(
            arquivo
        )

        cabecalho_atual = next(
            leitor,
            [],
        )

    if (
        cabecalho_atual
        != cabecalho_esperado
    ):
        raise RuntimeError(
            f"O arquivo {caminho.name} "
            "possui um cabeçalho incompatível. "
            "Renomeie ou apague o arquivo antigo."
        )


# ==========================================================
# LEADS
# ==========================================================

def salvar_lead_csv(
    lead: Lead,
) -> None:

    _validar_cabecalho_csv(
        LEADS_CSV,
        CABECALHO_LEADS,
    )

    arquivo_existe = (
        _arquivo_tem_conteudo(
            LEADS_CSV
        )
    )

    with LEADS_CSV.open(
        "a",
        encoding="utf-8-sig",
        newline="",
    ) as arquivo:

        escritor = csv.writer(
            arquivo
        )

        if not arquivo_existe:
            escritor.writerow(
                CABECALHO_LEADS
            )

        escritor.writerow(
            lead.para_linha_csv()
        )


def criar_lead_do_estado(
    estado: Any,
) -> Lead:

    dados = {
        "nome": estado.nome,
        "whatsapp": estado.whatsapp,
        "email": estado.email,
        "motivo": estado.motivo,
        "preferencia": estado.modalidade,
        "periodo": estado.periodo,
        "dia_preferido": (
            estado.dia_preferido
        ),
    }

    campos_ausentes = [
        campo
        for campo, valor
        in dados.items()
        if not valor
    ]

    if campos_ausentes:
        raise ValueError(
            "Informações incompletas: "
            + ", ".join(
                campos_ausentes
            )
        )

    return Lead(
        nome=str(
            dados["nome"]
        ),
        whatsapp=str(
            dados["whatsapp"]
        ),
        email=str(
            dados["email"]
        ),
        motivo=str(
            dados["motivo"]
        ),
        preferencia=str(
            dados["preferencia"]
        ),
        periodo=str(
            dados["periodo"]
        ),
        dia_preferido=str(
            dados["dia_preferido"]
        ),
        data=datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S"
        ),
    )


# ==========================================================
# LOG DE CLASSIFICAÇÕES
# ==========================================================

def registrar_classificacao(
    *,
    estado: Any,
    acao: str | None,
    origem: str | None = None,
) -> None:

    _validar_cabecalho_csv(
        CLASSIFICACOES_CSV,
        CABECALHO_CLASSIFICACOES,
    )

    arquivo_existe = (
        _arquivo_tem_conteudo(
            CLASSIFICACOES_CSV
        )
    )

    with CLASSIFICACOES_CSV.open(
        "a",
        encoding="utf-8-sig",
        newline="",
    ) as arquivo:

        escritor = csv.writer(
            arquivo
        )

        if not arquivo_existe:
            escritor.writerow(
                CABECALHO_CLASSIFICACOES
            )

        escritor.writerow(
            [
                datetime.now().strftime(
                    "%d/%m/%Y %H:%M:%S"
                ),
                estado.intencao,
                estado.etapa_atual,
                acao,
                origem,
                estado.concluido,
                estado.pronto_para_envio,
            ]
        )


# ==========================================================
# NOTIFICAÇÃO POR E-MAIL
# ==========================================================

def enviar_email_lead(
    lead: Lead,
) -> None:

    if not (
        EMAIL_REMETENTE
        and EMAIL_SENHA
        and EMAIL_DESTINATARIO
    ):
        logger.warning(
            "Notificação por e-mail "
            "desativada: configuração "
            "incompleta."
        )
        return

    corpo = (
        "Nova solicitação recebida:\n\n"
        f"Nome: {lead.nome}\n"
        f"WhatsApp: {lead.whatsapp}\n"
        f"E-mail: {lead.email}\n"
        f"Motivo: {lead.motivo}\n"
        f"Preferência: {lead.preferencia}\n"
        f"Período: {lead.periodo}\n"
        f"Dia: {lead.dia_preferido}\n"
        f"Data: {lead.data}\n"
    )

    mensagem = MIMEText(
        corpo,
        _charset="utf-8",
    )

    mensagem[
        "Subject"
    ] = "Nova solicitação de atendimento"

    mensagem[
        "From"
    ] = EMAIL_REMETENTE

    mensagem[
        "To"
    ] = EMAIL_DESTINATARIO

    with smtplib.SMTP(
        "smtp.gmail.com",
        587,
        timeout=15,
    ) as servidor:

        servidor.starttls()

        servidor.login(
            EMAIL_REMETENTE,
            EMAIL_SENHA,
        )

        servidor.sendmail(
            EMAIL_REMETENTE,
            EMAIL_DESTINATARIO,
            mensagem.as_string(),
        )


def notificar_lead(
    lead: Lead,
) -> None:

    try:
        enviar_email_lead(
            lead
        )

    except Exception:
        logger.exception(
            "Falha ao enviar "
            "notificação por e-mail."
        )


def iniciar_notificacao(
    lead: Lead,
) -> None:

    threading.Thread(
        target=notificar_lead,
        args=(lead,),
        daemon=True,
    ).start()


# ==========================================================
# SESSÃO DO CHAT
# ==========================================================

def limpar_sessao_chat() -> None:

    session.pop(
        "historico_chat",
        None,
    )

    session.pop(
        "estado_atendimento",
        None,
    )

    session.pop(
        "mostrar_botao_lead",
        None,
    )


def inicializar_sessao_chat() -> None:

    if (
        "historico_chat"
        not in session
    ):

        session[
            "historico_chat"
        ] = [
            {
                "tipo": "bot",
                "texto": (
                    "Olá! 😊 Sou a assistente virtual "
                    "da Saúde Mental Psicologia.\n\n"
                    "Posso ajudar com informações sobre "
                    "psicoterapia, ansiedade, depressão, "
                    "valores, modalidades de atendimento "
                    "ou ajudar você a solicitar uma sessão.\n\n"
                    "Como posso ajudar?"
                ),
            }
        ]

    if (
        "estado_atendimento"
        not in session
    ):

        session[
            "estado_atendimento"
        ] = estado_para_dict(
            estado_de_dict(
                None
            )
        )

    session.setdefault(
        "mostrar_botao_lead",
        False,
    )


# ==========================================================
# PRIVACIDADE
# ==========================================================

def mascarar_whatsapp(
    whatsapp: str,
) -> str:

    digitos = "".join(
        caractere
        for caractere
        in str(whatsapp)
        if caractere.isdigit()
    )

    if len(
        digitos
    ) < 8:
        return "***"

    return (
        f"({digitos[:2]}) "
        f"*****-**{digitos[-2:]}"
    )


def mascarar_email(
    email: str,
) -> str:

    email = str(
        email
    ).strip().lower()

    if "@" not in email:
        return "***"

    usuario, dominio = (
        email.split(
            "@",
            maxsplit=1,
        )
    )

    if len(usuario) <= 2:
        usuario_mascarado = (
            usuario[:1]
            + "***"
        )

    else:
        usuario_mascarado = (
            usuario[:2]
            + "***"
            + usuario[-1:]
        )

    return (
        f"{usuario_mascarado}"
        f"@{dominio}"
    )


# ==========================================================
# LOGIN
# ==========================================================

@app.route(
    "/login",
    methods=[
        "GET",
        "POST",
    ],
)
def login():

    erro = None

    if request.method == "POST":

        username = request.form.get(
            "username",
            "",
        ).strip()

        password = request.form.get(
            "password",
            "",
        )

        usuario_valido = (
            hmac.compare_digest(
                username,
                ADMIN_USER,
            )
        )

        senha_valida = (
            hmac.compare_digest(
                password,
                ADMIN_PASS,
            )
        )

        if (
            usuario_valido
            and senha_valida
        ):

            login_user(
                User(
                    username
                )
            )

            return redirect(
                url_for(
                    "listar_leads"
                )
            )

        logger.warning(
            "Tentativa de login "
            "administrativo inválida."
        )

        erro = (
            "Usuário ou senha inválidos."
        )

        return (
            render_template(
                "login.html",
                erro=erro,
            ),
            401,
        )

    return render_template(
        "login.html",
        erro=erro,
    )


# ==========================================================
# CHAT
# ==========================================================

@app.route(
    "/",
    methods=[
        "GET",
        "POST",
    ],
)
def inicio():

    inicializar_sessao_chat()

    conversa = session[
        "historico_chat"
    ]

    if request.method == "POST":

        # ==================================================
        # BOTÕES / ATALHOS
        # ==================================================

        atalho = request.form.get(
            "atalho",
            "",
        ).strip()

        if atalho:

            resposta = responder_atalho(
                atalho
            )

            if not resposta:
                return redirect(
                    url_for(
                        "inicio"
                    )
                )

            conversa.append(
                {
                    "tipo": "usuario",
                    "texto": (
                        atalho
                        .replace(
                            "_",
                            " ",
                        )
                        .capitalize()
                    ),
                }
            )

            estado = estado_de_dict(
                session.get(
                    "estado_atendimento"
                )
            )

            # ----------------------------------------------
            # ATALHO DE AGENDAMENTO
            # ----------------------------------------------

            if (
                atalho
                == "agendamento"
            ):

                resultado = (
                    processar_conversa(
                        estado=estado,
                        mensagem_usuario=(
                            "Quero solicitar "
                            "atendimento"
                        ),
                        historico=conversa,
                        limite_confianca=(
                            LIMITE_CONFIANCA
                        ),
                    )
                )

                resposta = resultado[
                    "mensagem"
                ]

                origem = resultado.get(
                    "origem",
                    "atalho",
                )

                acao = resultado.get(
                    "acao"
                )

            else:

                origem = "atalho"

                acao = (
                    f"atalho_{atalho}"
                )

            conversa.append(
                {
                    "tipo": "bot",
                    "texto": resposta,
                }
            )

            session[
                "historico_chat"
            ] = conversa

            session[
                "estado_atendimento"
            ] = estado_para_dict(
                estado
            )

            session[
                "mostrar_botao_lead"
            ] = (
                acao
                == "confirmar_envio"
            )

            session.modified = True

            try:
                registrar_classificacao(
                    estado=estado,
                    acao=acao,
                    origem=origem,
                )

            except Exception:
                logger.exception(
                    "Falha ao registrar "
                    "o atalho."
                )

            return redirect(
                url_for(
                    "inicio"
                )
            )

        # ==================================================
        # MENSAGEM DIGITADA
        # ==================================================

        pergunta = request.form.get(
            "pergunta",
            "",
        ).strip()

        if not pergunta:
            return redirect(
                url_for(
                    "inicio"
                )
            )

        estado = estado_de_dict(
            session.get(
                "estado_atendimento"
            )
        )

        resultado = processar_conversa(
            estado=estado,
            mensagem_usuario=pergunta,
            historico=conversa,
            limite_confianca=(
                LIMITE_CONFIANCA
            ),
        )

        resposta = resultado.get(
            "mensagem",
            (
                "Não consegui responder agora. "
                "Tente novamente."
            ),
        )

        conversa.extend(
            [
                {
                    "tipo": "usuario",
                    "texto": pergunta,
                },
                {
                    "tipo": "bot",
                    "texto": resposta,
                },
            ]
        )

        session[
            "historico_chat"
        ] = conversa

        session[
            "estado_atendimento"
        ] = estado_para_dict(
            estado
        )

        session[
            "mostrar_botao_lead"
        ] = (
            resultado.get(
                "acao"
            )
            == "confirmar_envio"
        )

        session.modified = True

        try:
            registrar_classificacao(
                estado=estado,
                acao=resultado.get(
                    "acao"
                ),
                origem=resultado.get(
                    "origem"
                ),
            )

        except Exception:
            logger.exception(
                "Falha ao registrar "
                "classificação."
            )

    estado_atual = estado_de_dict(
        session.get(
            "estado_atendimento"
        )
    )

    return render_template(
        "index.html",
        conversa=session[
            "historico_chat"
        ],
        mostrar_botao_lead=session.get(
            "mostrar_botao_lead",
            False,
        ),
        estado_atendimento=(
            estado_para_dict(
                estado_atual
            )
        ),
    )


# ==========================================================
# ENVIO DA SOLICITAÇÃO
# ==========================================================

@app.route(
    "/enviar_solicitacao",
    methods=["POST"],
)
def enviar_solicitacao():

    estado = estado_de_dict(
        session.get(
            "estado_atendimento"
        )
    )

    if not estado.pronto_para_envio:

        return (
            "A solicitação ainda não está "
            "completa.<br><br>"
            f"<a href='{url_for('inicio')}'>"
            "Voltar ao chat"
            "</a>",
            400,
        )

    try:

        lead = criar_lead_do_estado(
            estado
        )

        salvar_lead_csv(
            lead
        )

    except ValueError as erro:

        return (
            f"{erro}.<br><br>"
            f"<a href='{url_for('inicio')}'>"
            "Voltar ao chat"
            "</a>",
            400,
        )

    except Exception:

        logger.exception(
            "Falha ao salvar "
            "a solicitação."
        )

        return (
            "Não foi possível salvar a "
            "solicitação agora. "
            "Tente novamente.<br><br>"
            f"<a href='{url_for('inicio')}'>"
            "Voltar ao chat"
            "</a>",
            500,
        )

    iniciar_notificacao(
        lead
    )

    logger.info(
        "Solicitação registrada "
        "com sucesso."
    )

    limpar_sessao_chat()

    return render_template(
        "obrigado.html"
    )


# ==========================================================
# PAINEL
# ==========================================================

@app.route(
    "/leads"
)
@login_required
def listar_leads():

    leads: list[
        dict[str, str]
    ] = []

    pesquisa = request.args.get(
        "q",
        "",
    ).strip().lower()

    filtro_modalidade = (
        request.args.get(
            "modalidade",
            "",
        )
        .strip()
        .lower()
    )

    filtro_periodo = (
        request.args.get(
            "periodo",
            "",
        )
        .strip()
        .lower()
    )

    total = 0
    online = 0
    presencial = 0
    manha = 0
    tarde = 0
    noite = 0

    if _arquivo_tem_conteudo(
        LEADS_CSV
    ):

        _validar_cabecalho_csv(
            LEADS_CSV,
            CABECALHO_LEADS,
        )

        with LEADS_CSV.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as arquivo:

            registros = list(
                csv.DictReader(
                    arquivo
                )
            )

        total = len(
            registros
        )

        for registro in registros:

            preferencia = (
                registro.get(
                    "Preferencia",
                    "",
                )
                .strip()
                .lower()
            )

            periodo = (
                registro.get(
                    "Periodo",
                    "",
                )
                .strip()
                .lower()
            )

            online += int(
                preferencia
                == "online"
            )

            presencial += int(
                preferencia
                == "presencial"
            )

            manha += int(
                periodo
                in {
                    "manhã",
                    "manha",
                }
            )

            tarde += int(
                periodo
                == "tarde"
            )

            noite += int(
                periodo
                == "noite"
            )

        for registro in reversed(
            registros
        ):

            nome = registro.get(
                "Nome",
                "",
            )

            whatsapp = registro.get(
                "WhatsApp",
                "",
            )

            email = registro.get(
                "Email",
                "",
            )

            preferencia = (
                registro.get(
                    "Preferencia",
                    "",
                )
            )

            periodo = registro.get(
                "Periodo",
                "",
            )

            texto_pesquisa = (
                " ".join(
                    [
                        nome,
                        whatsapp,
                        email,
                        registro.get(
                            "Motivo",
                            "",
                        ),
                    ]
                )
                .lower()
            )

            if (
                pesquisa
                and pesquisa
                not in texto_pesquisa
            ):
                continue

            if (
                filtro_modalidade
                and preferencia.lower()
                != filtro_modalidade
            ):
                continue

            if (
                filtro_periodo
                and periodo.lower()
                != filtro_periodo
            ):
                continue

            lead_exibicao = dict(
                registro
            )

            lead_exibicao[
                "WhatsAppMascarado"
            ] = mascarar_whatsapp(
                whatsapp
            )

            lead_exibicao[
                "EmailMascarado"
            ] = mascarar_email(
                email
            )

            leads.append(
                lead_exibicao
            )

    return render_template(
        "leads.html",
        leads=leads,
        total=total,
        online=online,
        presencial=presencial,
        manha=manha,
        tarde=tarde,
        noite=noite,
        pesquisa=pesquisa,
        filtro_modalidade=(
            filtro_modalidade
        ),
        filtro_periodo=(
            filtro_periodo
        ),
        quantidade_filtrada=(
            len(leads)
        ),
    )


# ==========================================================
# EXPORTAÇÃO
# ==========================================================

@app.route(
    "/exportar"
)
@login_required
def exportar():

    if not _arquivo_tem_conteudo(
        LEADS_CSV
    ):
        return (
            "Nenhum lead encontrado.",
            404,
        )

    _validar_cabecalho_csv(
        LEADS_CSV,
        CABECALHO_LEADS,
    )

    dataframe = pd.read_csv(
        LEADS_CSV,
        encoding="utf-8-sig",
    )

    dataframe.to_excel(
        EXPORTACAO_XLSX,
        index=False,
    )

    return send_file(
        EXPORTACAO_XLSX,
        as_attachment=True,
        download_name=(
            "leads_export.xlsx"
        ),
    )


# ==========================================================
# LOGOUT
# ==========================================================

@app.route(
    "/logout"
)
@login_required
def logout():

    logout_user()

    return redirect(
        url_for(
            "login"
        )
    )


# ==========================================================
# NOVA CONVERSA
# ==========================================================

@app.route(
    "/limpar"
)
def limpar():

    limpar_sessao_chat()

    return redirect(
        url_for(
            "inicio"
        )
    )


# ==========================================================
# INICIALIZAÇÃO
# ==========================================================

if __name__ == "__main__":

    logger.info(
        "Aplicação iniciada."
    )

    logger.info(
        "Rotas: %s",
        app.url_map,
    )

    app.run(
        debug=False,
        host="127.0.0.1",
        port=5000,
    )
