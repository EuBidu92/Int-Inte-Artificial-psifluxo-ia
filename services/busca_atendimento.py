from pathlib import Path
from typing import Any
import unicodedata

import pandas as pd


RAIZ_PROJETO = Path(__file__).resolve().parent.parent

CAMINHO_PROFISSIONAIS = (
    RAIZ_PROJETO
    / "dados"
    / "profissionais.csv"
)


def normalizar_texto(texto: Any) -> str:
    """
    Padroniza textos para facilitar comparações.
    """

    if texto is None:
        return ""

    texto = str(texto).strip().lower()

    texto = unicodedata.normalize(
        "NFKD",
        texto,
    )

    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(
            caractere
        )
    )

    return " ".join(
        texto.split()
    )


def carregar_profissionais() -> pd.DataFrame:
    """
    Carrega e valida a base de profissionais
    e horários disponíveis.
    """

    if not CAMINHO_PROFISSIONAIS.exists():
        raise FileNotFoundError(
            "A base de profissionais não foi encontrada: "
            f"{CAMINHO_PROFISSIONAIS}"
        )

    dados = pd.read_csv(
        CAMINHO_PROFISSIONAIS,
        encoding="utf-8",
    )

    colunas_obrigatorias = {
        "id",
        "nome",
        "modalidade",
        "dia",
        "periodo",
        "especialidade",
        "valor_social",
        "ativo",
    }

    colunas_ausentes = (
        colunas_obrigatorias
        - set(dados.columns)
    )

    if colunas_ausentes:
        raise ValueError(
            "A base de profissionais não possui "
            "as colunas obrigatórias: "
            + ", ".join(
                sorted(colunas_ausentes)
            )
        )

    dados = dados.dropna(
        subset=[
            "id",
            "nome",
            "modalidade",
            "dia",
            "periodo",
        ]
    ).copy()

    for coluna in [
        "modalidade",
        "dia",
        "periodo",
        "especialidade",
        "valor_social",
        "ativo",
    ]:
        dados[coluna] = (
            dados[coluna]
            .apply(normalizar_texto)
        )

    dados = dados[
        dados["ativo"] == "sim"
    ].copy()

    return dados


def pontuar_opcao(
    linha: pd.Series,
    modalidade: str,
    periodo: str,
    dia_preferido: str,
    motivo: str = "",
) -> tuple[int, list[str]]:
    """
    Calcula a compatibilidade de um horário.

    Pontuação:
    - modalidade igual: 4 pontos;
    - período igual: 3 pontos;
    - dia igual: 3 pontos;
    - especialidade relacionada ao motivo: 2 pontos.
    """

    pontos = 0
    criterios = []

    modalidade = normalizar_texto(
        modalidade
    )

    periodo = normalizar_texto(
        periodo
    )

    dia_preferido = normalizar_texto(
        dia_preferido
    )

    motivo = normalizar_texto(
        motivo
    )

    if linha["modalidade"] == modalidade:
        pontos += 4
        criterios.append(
            "modalidade compatível"
        )

    if linha["periodo"] == periodo:
        pontos += 3
        criterios.append(
            "período compatível"
        )

    if linha["dia"] == dia_preferido:
        pontos += 3
        criterios.append(
            "dia compatível"
        )

    especialidade = normalizar_texto(
        linha["especialidade"]
    )

    palavras_especialidade = [
        palavra
        for palavra in especialidade.split()
        if len(palavra) >= 4
    ]

    if motivo and any(
        palavra in motivo
        for palavra in palavras_especialidade
    ):
        pontos += 2
        criterios.append(
            "especialidade relacionada"
        )

    return pontos, criterios


def buscar_opcoes(
    modalidade: str,
    periodo: str,
    dia_preferido: str,
    motivo: str = "",
    limite: int = 3,
) -> list[dict[str, Any]]:
    """
    Retorna as opções mais compatíveis,
    ordenadas pela pontuação.
    """

    if limite < 1:
        raise ValueError(
            "O limite precisa ser maior que zero."
        )

    profissionais = carregar_profissionais()

    resultados = []

    for _, linha in profissionais.iterrows():
        pontuacao, criterios = pontuar_opcao(
            linha=linha,
            modalidade=modalidade,
            periodo=periodo,
            dia_preferido=dia_preferido,
            motivo=motivo,
        )

        resultados.append(
            {
                "id": int(linha["id"]),
                "nome": str(linha["nome"]),
                "modalidade": str(
                    linha["modalidade"]
                ),
                "dia": str(linha["dia"]),
                "periodo": str(
                    linha["periodo"]
                ),
                "especialidade": str(
                    linha["especialidade"]
                ),
                "valor_social": (
                    linha["valor_social"]
                    == "sim"
                ),
                "pontuacao": pontuacao,
                "criterios": criterios,
            }
        )

    resultados.sort(
        key=lambda opcao: (
            opcao["pontuacao"],
            opcao["valor_social"],
        ),
        reverse=True,
    )

    return resultados[:limite]