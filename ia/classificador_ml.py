from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


# ==========================================================
# CAMINHOS
# ==========================================================

RAIZ_PROJETO = Path(__file__).resolve().parent.parent

CAMINHO_DADOS = (
    RAIZ_PROJETO
    / "dados"
    / "intencoes.csv"
)

CAMINHO_MODELO = (
    RAIZ_PROJETO
    / "modelos"
    / "classificador_intencoes.joblib"
)


# ==========================================================
# CARREGAMENTO E VALIDAÇÃO DOS DADOS
# ==========================================================

def carregar_dados() -> pd.DataFrame:
    """
    Carrega e valida a base de mensagens e intenções.
    """

    if not CAMINHO_DADOS.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {CAMINHO_DADOS}"
        )

    dados = pd.read_csv(
        CAMINHO_DADOS,
        encoding="utf-8",
    )

    colunas_obrigatorias = {
        "texto",
        "intencao",
    }

    if not colunas_obrigatorias.issubset(
        dados.columns
    ):
        raise ValueError(
            "O CSV precisa conter as colunas "
            "'texto' e 'intencao'."
        )

    dados = dados.dropna(
        subset=[
            "texto",
            "intencao",
        ]
    ).copy()

    dados["texto"] = (
        dados["texto"]
        .astype(str)
        .str.strip()
    )

    dados["intencao"] = (
        dados["intencao"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    dados = dados[
        dados["texto"].str.len() > 0
    ]

    dados = dados.drop_duplicates(
        subset=["texto"]
    )

    if dados.empty:
        raise ValueError(
            "A base de treinamento está vazia."
        )

    quantidade_classes = (
        dados["intencao"].nunique()
    )

    if quantidade_classes < 2:
        raise ValueError(
            "A base precisa conter pelo menos "
            "duas intenções diferentes."
        )

    return dados


# ==========================================================
# PIPELINE DE MACHINE LEARNING
# ==========================================================

def criar_pipeline() -> Pipeline:
    """
    Cria o pipeline de vetorização e classificação.
    """

    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    strip_accents="unicode",
                    ngram_range=(1, 2),
                    min_df=1,
                    sublinear_tf=True,
                ),
            ),
            (
                "classificador",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )


# ==========================================================
# TREINAMENTO
# ==========================================================

def treinar_modelo() -> dict[str, Any]:
    """
    Treina, avalia e salva o modelo.
    """

    dados = carregar_dados()

    entradas = dados["texto"]
    alvos = dados["intencao"]

    x_treino, x_teste, y_treino, y_teste = (
        train_test_split(
            entradas,
            alvos,
            test_size=0.20,
            random_state=42,
            stratify=alvos,
        )
    )

    modelo = criar_pipeline()

    modelo.fit(
        x_treino,
        y_treino,
    )

    previsoes = modelo.predict(
        x_teste
    )

    acuracia = accuracy_score(
        y_teste,
        previsoes,
    )

    relatorio = classification_report(
        y_teste,
        previsoes,
        zero_division=0,
    )

    matriz = confusion_matrix(
        y_teste,
        previsoes,
        labels=modelo.classes_,
    )

    CAMINHO_MODELO.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        modelo,
        CAMINHO_MODELO,
    )

    # Caso o modelo já estivesse carregado em memória,
    # limpa o cache para que a próxima classificação
    # utilize a versão recém-treinada.
    carregar_modelo.cache_clear()

    return {
        "quantidade_registros": len(dados),
        "quantidade_treino": len(x_treino),
        "quantidade_teste": len(x_teste),
        "classes": list(modelo.classes_),
        "acuracia": acuracia,
        "relatorio": relatorio,
        "matriz_confusao": matriz,
        "modelo_salvo_em": str(
            CAMINHO_MODELO
        ),
    }


# ==========================================================
# CARREGAMENTO DO MODELO
# ==========================================================

@lru_cache(maxsize=1)
def carregar_modelo() -> Pipeline:
    """
    Carrega o modelo treinado.

    O cache evita reler o arquivo joblib
    a cada nova classificação.
    """

    if not CAMINHO_MODELO.exists():
        raise FileNotFoundError(
            "O modelo ainda não foi treinado. "
            "Execute o comando: "
            "python -m ia.classificador_ml"
        )

    return joblib.load(
        CAMINHO_MODELO
    )


# ==========================================================
# CLASSIFICAÇÃO
# ==========================================================

def classificar_mensagem(
    texto: str,
    limite_confianca: float = 0.55,
) -> dict[str, Any]:
    """
    Classifica uma mensagem.

    Retorna:
    - intenção final;
    - intenção originalmente prevista;
    - confiança da previsão;
    - indicação de encaminhamento humano;
    - três maiores probabilidades.
    """

    if not isinstance(
        texto,
        str,
    ):
        texto = str(
            texto
        )

    texto = texto.strip()

    if not texto:
        return {
            "intencao": "nao_compreendida",
            "intencao_prevista": None,
            "confianca": 0.0,
            "encaminhar_humano": True,
            "top_3": [],
        }

    if not 0.0 <= limite_confianca <= 1.0:
        raise ValueError(
            "O limite de confiança deve estar "
            "entre 0.0 e 1.0."
        )

    modelo = carregar_modelo()

    probabilidades = modelo.predict_proba(
        [texto]
    )[0]

    classes = modelo.classes_

    ranking = sorted(
        zip(
            classes,
            probabilidades,
        ),
        key=lambda item: item[1],
        reverse=True,
    )

    top_3 = [
        {
            "intencao": str(
                classe
            ),
            "probabilidade": round(
                float(probabilidade),
                4,
            ),
        }
        for classe, probabilidade
        in ranking[:3]
    ]

    indice_maior = int(
        probabilidades.argmax()
    )

    intencao_prevista = str(
        classes[indice_maior]
    )

    confianca = float(
        probabilidades[indice_maior]
    )

    encaminhar_humano = (
        confianca < limite_confianca
    )

    if encaminhar_humano:
        intencao_final = (
            "nao_compreendida"
        )
    else:
        intencao_final = (
            intencao_prevista
        )

    return {
        "intencao": intencao_final,
        "intencao_prevista": intencao_prevista,
        "confianca": round(
            confianca,
            4,
        ),
        "encaminhar_humano": encaminhar_humano,
        "top_3": top_3,
    }


# ==========================================================
# EXECUÇÃO DIRETA
# ==========================================================

if __name__ == "__main__":
    resultados = treinar_modelo()

    print(
        "\nTREINAMENTO CONCLUÍDO"
    )
    print("=" * 60)

    print(
        "Registros:",
        resultados[
            "quantidade_registros"
        ],
    )

    print(
        "Treino:",
        resultados[
            "quantidade_treino"
        ],
    )

    print(
        "Teste:",
        resultados[
            "quantidade_teste"
        ],
    )

    print(
        "Classes:",
        resultados["classes"],
    )

    print(
        f"Acurácia: "
        f"{resultados['acuracia']:.2%}"
    )

    print(
        "\nRelatório de classificação:"
    )
    print(
        resultados["relatorio"]
    )

    print(
        "Matriz de confusão:"
    )
    print(
        resultados[
            "matriz_confusao"
        ]
    )

    print(
        "\nModelo salvo em:",
        resultados[
            "modelo_salvo_em"
        ],
    )