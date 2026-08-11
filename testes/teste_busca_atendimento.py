from services.busca_atendimento import (
    buscar_opcoes,
)


opcoes = buscar_opcoes(
    modalidade="online",
    periodo="noite",
    dia_preferido="quinta-feira",
    motivo=(
        "Quero iniciar acompanhamento "
        "por ansiedade"
    ),
    limite=3,
)


print("\nMELHORES OPÇÕES")
print("=" * 60)

for posicao, opcao in enumerate(
    opcoes,
    start=1,
):
    print(
        f"\n{posicao}. {opcao['nome']}"
    )

    print(
        "Modalidade:",
        opcao["modalidade"],
    )

    print(
        "Dia:",
        opcao["dia"],
    )

    print(
        "Período:",
        opcao["periodo"],
    )

    print(
        "Especialidade:",
        opcao["especialidade"],
    )

    print(
        "Valor social:",
        opcao["valor_social"],
    )

    print(
        "Pontuação:",
        opcao["pontuacao"],
    )

    print(
        "Critérios:",
        ", ".join(
            opcao["criterios"]
        ),
    )