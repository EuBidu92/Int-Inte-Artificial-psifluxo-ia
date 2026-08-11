from dataclasses import asdict, dataclass
from typing import Any, Optional


@dataclass
class EstadoAtendimento:
    """
    Representa todos os dados e etapas
    da conversa administrativa.
    """

    intencao: Optional[str] = None

    modalidade: Optional[str] = None
    periodo: Optional[str] = None
    dia_preferido: Optional[str] = None

    nome: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    motivo: Optional[str] = None

    etapa_atual: str = "inicio"

    pronto_para_envio: bool = False
    concluido: bool = False
    encaminhar_humano: bool = False


def criar_estado_inicial() -> EstadoAtendimento:
    """
    Cria um estado vazio para uma nova conversa.
    """

    return EstadoAtendimento()


def estado_para_dict(
    estado: EstadoAtendimento,
) -> dict[str, Any]:
    """
    Converte o estado para um dicionário
    que pode ser armazenado na sessão Flask.
    """

    return asdict(estado)


def estado_de_dict(
    dados: dict[str, Any] | None,
) -> EstadoAtendimento:
    """
    Reconstrói o estado salvo na sessão.
    """

    if not dados:
        return criar_estado_inicial()

    campos_validos = {
        "intencao",
        "modalidade",
        "periodo",
        "dia_preferido",
        "nome",
        "whatsapp",
        "email",
        "motivo",
        "etapa_atual",
        "pronto_para_envio",
        "concluido",
        "encaminhar_humano",
    }

    dados_filtrados = {
        chave: valor
        for chave, valor in dados.items()
        if chave in campos_validos
    }

    return EstadoAtendimento(
        **dados_filtrados
    )