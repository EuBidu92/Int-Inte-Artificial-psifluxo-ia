from ia.agente import (
    criar_estado_inicial,
    estado_para_dict,
)
from ia.orquestrador import processar_mensagem


estado = criar_estado_inicial()

mensagens = [
    "Quero começar terapia com um psicólogo",
    "Prefiro online",
    "Só posso à noite",
    "Quinta-feira seria melhor",
]


for numero, mensagem in enumerate(
    mensagens,
    start=1,
):
    print("\n" + "=" * 70)
    print(f"MENSAGEM {numero}: {mensagem}")

    resultado = processar_mensagem(
        estado,
        mensagem,
        limite_confianca=0.40,
    )

    print("\nRESPOSTA DO SISTEMA:")
    print(resultado["mensagem"])

    print("\nAÇÃO:")
    print(resultado.get("acao"))

    print("\nORIGEM DA DECISÃO:")
    print(resultado.get("origem_decisao"))

    if "classificacao" in resultado:
        classificacao = resultado["classificacao"]

        print("\nCLASSIFICAÇÃO:")
        print(
            "Intenção prevista:",
            classificacao["intencao_prevista"],
        )
        print(
            "Intenção final:",
            classificacao["intencao"],
        )
        print(
            "Confiança:",
            f"{classificacao['confianca']:.2%}",
        )

    if "interpretacao" in resultado:
        print("\nINTERPRETAÇÃO:")
        print(resultado["interpretacao"])

    print("\nESTADO:")
    print(
        estado_para_dict(estado)
    )