from ia.agente import (
    criar_estado_inicial,
    estado_para_dict,
)
from ia.motor_regras import definir_proxima_acao


estado = criar_estado_inicial()

estado.intencao = "agendamento"

print("=" * 60)
print("ESTADO INICIAL")
print(estado_para_dict(estado))

resultado = definir_proxima_acao(
    estado
)

print("\nPRÓXIMA AÇÃO")
print(resultado)
print("\nESTADO ATUALIZADO")
print(estado_para_dict(estado))


estado.modalidade = "online"

resultado = definir_proxima_acao(
    estado
)

print("\n" + "=" * 60)
print("MODALIDADE INFORMADA")
print(resultado)
print(estado_para_dict(estado))


estado.periodo = "noite"

resultado = definir_proxima_acao(
    estado
)

print("\n" + "=" * 60)
print("PERÍODO INFORMADO")
print(resultado)
print(estado_para_dict(estado))


estado.dia_preferido = "quinta-feira"

resultado = definir_proxima_acao(
    estado
)

print("\n" + "=" * 60)
print("DIA INFORMADO")
print(resultado)
print(estado_para_dict(estado))