from pathlib import Path
from time import perf_counter

import pandas as pd
import pytest

from ia.classificador_ml import (
    CAMINHO_DADOS,
    CAMINHO_MODELO,
    carregar_dados,
    carregar_modelo,
    classificar_mensagem,
    criar_pipeline,
    treinar_modelo,
)


# ==========================================================
# VALIDAÇÃO DA BASE DE DADOS
# ==========================================================

def test_base_de_dados_existe() -> None:
    assert CAMINHO_DADOS.exists()
    assert CAMINHO_DADOS.is_file()


def test_base_possui_500_registros() -> None:
    dados = carregar_dados()

    assert len(dados) == 500


def test_base_possui_colunas_obrigatorias() -> None:
    dados = carregar_dados()

    assert "texto" in dados.columns
    assert "intencao" in dados.columns


def test_base_nao_possui_valores_vazios() -> None:
    dados = carregar_dados()

    assert dados["texto"].isna().sum() == 0
    assert dados["intencao"].isna().sum() == 0


def test_base_nao_possui_textos_duplicados() -> None:
    dados = carregar_dados()

    assert dados["texto"].duplicated().sum() == 0


def test_base_possui_cinco_classes() -> None:
    dados = carregar_dados()

    classes = sorted(
        dados["intencao"].unique()
    )

    assert classes == [
        "agendamento",
        "funcionamento",
        "modalidade",
        "remarcacao",
        "valores",
    ]


def test_classes_estao_balanceadas() -> None:
    dados = carregar_dados()

    distribuicao = (
        dados["intencao"]
        .value_counts()
        .to_dict()
    )

    assert distribuicao == {
        "agendamento": 100,
        "funcionamento": 100,
        "modalidade": 100,
        "remarcacao": 100,
        "valores": 100,
    }


# ==========================================================
# PIPELINE E MODELO
# ==========================================================

def test_pipeline_possui_componentes_esperados() -> None:
    pipeline = criar_pipeline()

    assert "tfidf" in pipeline.named_steps
    assert "classificador" in pipeline.named_steps


def test_modelo_salvo_existe() -> None:
    assert CAMINHO_MODELO.exists()
    assert CAMINHO_MODELO.is_file()


def test_modelo_pode_ser_carregado() -> None:
    carregar_modelo.cache_clear()

    modelo = carregar_modelo()

    assert hasattr(modelo, "predict")
    assert hasattr(modelo, "predict_proba")

    carregar_modelo.cache_clear()


# ==========================================================
# CLASSIFICAÇÕES PRINCIPAIS
# ==========================================================

@pytest.mark.parametrize(
    (
        "mensagem",
        "intencao_esperada",
    ),
    [
        (
            "Quero começar terapia com um psicólogo",
            "agendamento",
        ),
        (
            "Qual é o preço do atendimento?",
            "valores",
        ),
        (
            "Vocês fazem consulta por videochamada?",
            "modalidade",
        ),
        (
            "Como funciona uma sessão de psicoterapia?",
            "funcionamento",
        ),
        (
            "Preciso mudar minha consulta para sexta",
            "remarcacao",
        ),
    ],
)
def test_classificacoes_principais(
    mensagem: str,
    intencao_esperada: str,
) -> None:
    resultado = classificar_mensagem(
        mensagem,
        limite_confianca=0.40,
    )

    assert (
        resultado["intencao"]
        == intencao_esperada
    )

    assert (
        resultado["intencao_prevista"]
        == intencao_esperada
    )

    assert (
        resultado["encaminhar_humano"]
        is False
    )

    assert resultado["confianca"] >= 0.40


def test_mensagem_ambigua_encaminha_humano() -> None:
    resultado = classificar_mensagem(
        "Boa tarde",
        limite_confianca=0.40,
    )

    assert (
        resultado["intencao"]
        == "nao_compreendida"
    )

    assert (
        resultado["intencao_prevista"]
        in {
            "agendamento",
            "funcionamento",
            "modalidade",
            "remarcacao",
            "valores",
        }
    )

    assert (
        resultado["encaminhar_humano"]
        is True
    )

    assert resultado["confianca"] < 0.40


def test_mensagem_vazia() -> None:
    resultado = classificar_mensagem(
        "",
        limite_confianca=0.40,
    )

    assert (
        resultado["intencao"]
        == "nao_compreendida"
    )

    assert (
        resultado["intencao_prevista"]
        is None
    )

    assert resultado["confianca"] == 0.0

    assert (
        resultado["encaminhar_humano"]
        is True
    )

    assert resultado["top_3"] == []


def test_mensagem_nao_textual_e_convertida() -> None:
    resultado = classificar_mensagem(
        12345,
        limite_confianca=0.40,
    )

    assert "intencao" in resultado
    assert "intencao_prevista" in resultado
    assert "confianca" in resultado
    assert "encaminhar_humano" in resultado
    assert "top_3" in resultado


@pytest.mark.parametrize(
    "limite_invalido",
    [
        -0.01,
        1.01,
        -1.0,
        2.0,
    ],
)
def test_limite_de_confianca_invalido(
    limite_invalido: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="entre 0.0 e 1.0",
    ):
        classificar_mensagem(
            "Quero atendimento",
            limite_confianca=limite_invalido,
        )


# ==========================================================
# PROBABILIDADES
# ==========================================================

def test_top_3_possui_tres_resultados() -> None:
    resultado = classificar_mensagem(
        "Quero marcar uma consulta",
        limite_confianca=0.40,
    )

    assert len(resultado["top_3"]) == 3

    for item in resultado["top_3"]:
        assert "intencao" in item
        assert "probabilidade" in item


def test_probabilidades_estao_entre_zero_e_um() -> None:
    resultado = classificar_mensagem(
        "Quero atendimento online",
        limite_confianca=0.40,
    )

    for item in resultado["top_3"]:
        assert (
            0.0
            <= item["probabilidade"]
            <= 1.0
        )


def test_top_3_esta_em_ordem_decrescente() -> None:
    resultado = classificar_mensagem(
        "Quero saber o valor da consulta",
        limite_confianca=0.40,
    )

    probabilidades = [
        item["probabilidade"]
        for item in resultado["top_3"]
    ]

    assert probabilidades == sorted(
        probabilidades,
        reverse=True,
    )


# ==========================================================
# DESEMPENHO
# ==========================================================

def test_tempo_medio_de_inferencia() -> None:
    mensagens = [
        "Quero marcar uma consulta",
        "Qual o valor da sessão?",
        "Vocês atendem online?",
        "Como funciona a psicoterapia?",
        "Preciso remarcar meu horário",
    ]

    carregar_modelo.cache_clear()

    # Primeiro carregamento fora da medição.
    carregar_modelo()

    inicio = perf_counter()

    for _ in range(20):
        for mensagem in mensagens:
            classificar_mensagem(
                mensagem,
                limite_confianca=0.40,
            )

    duracao_total = (
        perf_counter()
        - inicio
    )

    quantidade = (
        20
        * len(mensagens)
    )

    tempo_medio = (
        duracao_total
        / quantidade
    )

    print(
        "\nTempo médio de inferência: "
        f"{tempo_medio * 1000:.3f} ms"
    )

    assert tempo_medio < 0.10


def test_cache_do_modelo() -> None:
    carregar_modelo.cache_clear()

    primeiro_modelo = carregar_modelo()
    segundo_modelo = carregar_modelo()

    informacoes_cache = (
        carregar_modelo.cache_info()
    )

    assert primeiro_modelo is segundo_modelo
    assert informacoes_cache.misses == 1
    assert informacoes_cache.hits >= 1
    assert informacoes_cache.currsize == 1

    carregar_modelo.cache_clear()


# ==========================================================
# TREINAMENTO
# ==========================================================

def test_treinamento_mantem_acuracia_minima(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    caminho_temporario = (
        tmp_path
        / "modelo_teste.joblib"
    )

    carregar_modelo.cache_clear()

    monkeypatch.setattr(
        "ia.classificador_ml.CAMINHO_MODELO",
        caminho_temporario,
    )

    resultados = treinar_modelo()

    assert (
        resultados["quantidade_registros"]
        == 500
    )

    assert (
        resultados["quantidade_treino"]
        == 400
    )

    assert (
        resultados["quantidade_teste"]
        == 100
    )

    assert resultados["acuracia"] >= 0.80

    assert resultados["classes"] == [
        "agendamento",
        "funcionamento",
        "modalidade",
        "remarcacao",
        "valores",
    ]

    assert caminho_temporario.exists()

    assert (
        resultados["modelo_salvo_em"]
        == str(caminho_temporario)
    )

    carregar_modelo.cache_clear()


# ==========================================================
# TRATAMENTO DE ERROS
# ==========================================================

def test_carregar_dados_arquivo_inexistente(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    caminho_inexistente = (
        tmp_path
        / "nao_existe.csv"
    )

    monkeypatch.setattr(
        "ia.classificador_ml.CAMINHO_DADOS",
        caminho_inexistente,
    )

    with pytest.raises(
        FileNotFoundError
    ):
        carregar_dados()


def test_carregar_dados_sem_colunas_obrigatorias(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    caminho = (
        tmp_path
        / "dados_invalidos.csv"
    )

    pd.DataFrame(
        {
            "mensagem": [
                "Quero atendimento"
            ],
            "classe": [
                "agendamento"
            ],
        }
    ).to_csv(
        caminho,
        index=False,
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "ia.classificador_ml.CAMINHO_DADOS",
        caminho,
    )

    with pytest.raises(
        ValueError,
        match="colunas",
    ):
        carregar_dados()


def test_carregar_dados_base_vazia(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    caminho = (
        tmp_path
        / "dados_vazios.csv"
    )

    pd.DataFrame(
        {
            "texto": [],
            "intencao": [],
        }
    ).to_csv(
        caminho,
        index=False,
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "ia.classificador_ml.CAMINHO_DADOS",
        caminho,
    )

    with pytest.raises(
        ValueError,
        match="vazia",
    ):
        carregar_dados()


def test_carregar_dados_com_uma_unica_classe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    caminho = (
        tmp_path
        / "uma_classe.csv"
    )

    pd.DataFrame(
        {
            "texto": [
                "Quero terapia",
                "Quero uma consulta",
            ],
            "intencao": [
                "agendamento",
                "agendamento",
            ],
        }
    ).to_csv(
        caminho,
        index=False,
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "ia.classificador_ml.CAMINHO_DADOS",
        caminho,
    )

    with pytest.raises(
        ValueError,
        match="duas intenções",
    ):
        carregar_dados()


def test_carregar_modelo_inexistente(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    carregar_modelo.cache_clear()

    caminho_inexistente = (
        tmp_path
        / "modelo_inexistente.joblib"
    )

    monkeypatch.setattr(
        "ia.classificador_ml.CAMINHO_MODELO",
        caminho_inexistente,
    )

    with pytest.raises(
        FileNotFoundError
    ):
        carregar_modelo()

    carregar_modelo.cache_clear()