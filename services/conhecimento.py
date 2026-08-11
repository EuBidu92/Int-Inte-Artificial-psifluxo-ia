from __future__ import annotations


RESPOSTAS_ATALHOS = {

    "ansiedade": (
        "A ansiedade pode aparecer como "
        "preocupação excessiva, tensão, medo, "
        "inquietação ou manifestações físicas.\n\n"
        "Quando essas experiências se tornam "
        "frequentes, intensas ou começam a "
        "interferir na rotina, buscar acompanhamento "
        "psicológico pode ser uma possibilidade.\n\n"
        "Se quiser, posso explicar como funciona "
        "o atendimento ou ajudar você a solicitar "
        "uma sessão."
    ),

    "depressao": (
        "Momentos de tristeza podem fazer parte "
        "da vida. Quando o desânimo, a perda de "
        "interesse, o isolamento ou outras mudanças "
        "persistem e começam a interferir na rotina, "
        "pode ser importante procurar avaliação "
        "profissional.\n\n"
        "Posso explicar como funciona a psicoterapia "
        "ou ajudar você a solicitar atendimento."
    ),

    "psicoterapia": (
        "A psicoterapia é um espaço de escuta e "
        "acompanhamento profissional em que questões "
        "emocionais, relacionamentos, conflitos e "
        "outras experiências podem ser trabalhados "
        "ao longo das sessões.\n\n"
        "A frequência, os horários e as demais "
        "condições são combinados entre a pessoa "
        "atendida e o profissional.\n\n"
        "Posso explicar sobre modalidade, valores "
        "ou como solicitar atendimento."
    ),

    "online": (
        "Sim. O atendimento pode ser realizado "
        "online, por videochamada e em horário "
        "previamente combinado.\n\n"
        "É importante utilizar um ambiente com "
        "privacidade e conexão adequada durante "
        "a sessão."
    ),

    "presencial": (
        "Também há possibilidade de atendimento "
        "presencial, conforme disponibilidade do "
        "profissional e dos horários.\n\n"
        "Se quiser iniciar uma solicitação, posso "
        "ajudar a registrar suas preferências."
    ),

    "valores": (
        "Os valores dependem das condições do "
        "atendimento e do acompanhamento acordado.\n\n"
        "Posso explicar melhor ou ajudar você a "
        "solicitar um atendimento."
    ),

    "agendamento": (
        "Posso ajudar com sua solicitação "
        "de atendimento."
    ),
}


SAUDACAO = (
    "Olá! 😊 Como posso ajudar?\n\n"
    "Posso conversar com você sobre psicoterapia, "
    "ansiedade, depressão, valores, atendimento "
    "online ou presencial, ou ajudar a solicitar "
    "uma sessão."
)


PEDIDO_GENERICO = (
    "Claro! Que tipo de informação você gostaria "
    "de saber?\n\n"
    "Posso explicar sobre:\n"
    "• psicoterapia;\n"
    "• valores;\n"
    "• atendimento online ou presencial;\n"
    "• ansiedade ou depressão;\n"
    "• como solicitar atendimento."
)


FALLBACK_LOCAL = (
    "Posso ajudar com informações sobre "
    "psicoterapia, valores, modalidades de "
    "atendimento ou solicitação de uma sessão.\n\n"
    "Se preferir, você também pode falar "
    "diretamente com a equipe."
)


CONTEXTO_CLINICA = """
O PsiFluxo IA é uma assistente administrativa de primeiro contato
para um serviço de Psicologia.

Ela pode:
- explicar de forma geral como funciona a psicoterapia;
- responder dúvidas gerais sobre o serviço;
- responder dúvidas educativas gerais sobre ansiedade e depressão;
- explicar atendimento online e presencial;
- explicar de maneira geral o processo de solicitação;
- reconhecer quando uma pessoa deseja iniciar atendimento.

Ela não pode:
- realizar diagnóstico;
- realizar psicoterapia;
- substituir um psicólogo;
- prescrever medicamentos;
- fazer avaliação psicológica;
- inventar preço, endereço, horário ou disponibilidade;
- prometer resultados terapêuticos.

Se o usuário demonstrar interesse em atendimento, a resposta pode
dizer que o sistema pode ajudá-lo a iniciar uma solicitação.
"""