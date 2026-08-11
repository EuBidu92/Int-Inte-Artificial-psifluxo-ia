import services.groq_service as groq


def test_fallback_sem_chave(
    monkeypatch,
) -> None:

    monkeypatch.setattr(
        groq,
        "GROQ_API_KEY",
        None,
    )

    resposta = (
        groq.responder_com_groq(
            "Quero informações"
        )
    )

    assert isinstance(
        resposta,
        str,
    )

    assert len(
        resposta
    ) > 20