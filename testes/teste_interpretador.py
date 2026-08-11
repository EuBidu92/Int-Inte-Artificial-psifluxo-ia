from ia.agente import (
    criar_estado_inicial,
    estado_para_dict,
)
from ia.interpretador_respostas import (
    atualizar_estado_com_resposta,
)
from ia.motor_regras import definir_proxima_acao


estado = criar_estado_inicial()
estado.intencao = "agendamento"


def mostrar_estado(titulo: str) -> None:
    print("\n" + "=" * 60)
    print(titulo)
    print(estado_para_dict(estado))


mostrar_estado(
    "ESTADO INICIAL"
)

proxima_acao = definir_proxima_acao(
    estado
)

print("\nAÇÃO:")
print(proxima_acao)


resultado = atualizar_estado_com_resposta(
    estado,
    "Prefiro atendimento online",
)

print("\nINTERPRETAÇÃO:")
print(resultado)

proxima_acao = definir_proxima_acao(
    estado
)

print("\nAÇÃO:")
print(proxima_acao)

mostrar_estado(
    "APÓS MODALIDADE"
)


resultado = atualizar_estado_com_resposta(
    estado,
    "Só posso à noite",
)

print("\nINTERPRETAÇÃO:")
print(resultado)

proxima_acao = definir_proxima_acao(
    estado
)

print("\nAÇÃO:")
print(proxima_acao)

mostrar_estado(
    "APÓS PERÍODO"
)


resultado = atualizar_estado_com_resposta(
    estado,
    "Quinta-feira seria melhor",
)

print("\nINTERPRETAÇÃO:")
print(resultado)

proxima_acao = definir_proxima_acao(
    estado
)

print("\nAÇÃO:")
print(proxima_acao)

mostrar_estado(
    "APÓS DIA"
)