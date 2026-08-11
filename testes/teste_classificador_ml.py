from ia.classificador_ml import classificar_mensagem


mensagens_teste = [
    "Quero começar terapia com um psicólogo",
    "Qual é o preço do atendimento?",
    "Vocês fazem consulta por chamada de vídeo?",
    "Como funciona uma sessão de análise?",
    "Preciso mudar minha consulta para sexta",
    "Boa tarde",
]


for mensagem in mensagens_teste:
    resultado = classificar_mensagem(
        mensagem,
        limite_confianca=0.40,
    )

    print("-" * 60)
    print(f"Mensagem: {mensagem}")
    print(f"Intenção: {resultado['intencao']}")
    print(f"Confiança: {resultado['confianca']:.2%}")

    print(
        "Encaminhar para humano:",
        resultado["encaminhar_humano"],
    )

    print("Três maiores probabilidades:")

    for item in resultado["top_3"]:
        print(
            f"  {item['intencao']}: "
            f"{item['probabilidade']:.2%}"
        )