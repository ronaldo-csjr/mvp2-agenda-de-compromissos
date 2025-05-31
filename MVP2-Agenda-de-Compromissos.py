import calendar
import datetime
import string
import random
from tabulate import tabulate
from time import sleep

def gera_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def obter_data_valida(mensagem_input="Digite a data (DD/MM/AAAA): ", formato="%d/%m/%Y"):
    """
    Solicita ao usuário uma data até que um input válido seja fornecido.

    Args:
        mensagem_input (str): A mensagem a ser exibida ao solicitar a data.
        formato (str): O formato esperado da data.

    Returns:
        datetime.date: O objeto datetime.date da data válida inserida pelo usuário.
    """
    # Inicia um loop infinito que só será quebrado quando uma data válida for fornecida
    while True:
        data_str = input(mensagem_input)

        # Inicia um bloco try-except para tentar converter a string em uma data
        try:
            # Tenta converter a string 'data_str' para um objeto datetime,
            # usando o 'formato' especificado (ex: "%d/%m/%Y").
            # Se a string não corresponder ao formato, um ValueError será levantado.
            data_obj = datetime.datetime.strptime(data_str, formato)

            # Se a conversão for bem-sucedida, a função retorna apenas a parte da data
            # (sem a hora), usando .date(), e sai do loop.
            return data_obj.strftime("%d/%m/%Y")

        # Se um ValueError for levantado (indicando que a string não é uma data válida no formato)
        except ValueError:
            # Exibe uma mensagem de erro informando ao usuário que a data é inválida
            # e pede para tentar novamente. O loop 'while True' continua, solicitando
            # uma nova entrada.
            print(f"Erro: '{data_str}' não é uma data válida no formato '{formato}'. Tente novamente.")

def obter_hora_valida(mensagem_input="Digite a hora (HH:MM): ", formato_entrada="%H:%M"):
    """
    Solicita ao usuário uma hora até que um input válido seja fornecido
    e retorna a hora formatada como string "HH:MM".

    Args:
        mensagem_input (str): A mensagem a ser exibida ao solicitar a hora.
        formato_entrada (str): O formato esperado da hora na entrada do usuário.

    Returns:
        str: A hora válida inserida pelo usuário, formatada como "HH:MM".
    """
    while True:
        hora_str = input(mensagem_input)
        try:
            # Tenta converter a string de entrada para um objeto datetime.
            # Se a string não corresponder ao formato, um ValueError será levantado.
            hora_obj = datetime.datetime.strptime(hora_str, formato_entrada)

            # Formata o objeto datetime para a string "HH:MM".
            # %H: Hora (24 horas) como um número decimal (00-23)
            # %M: Minuto como um número decimal (00-59)
            return hora_obj.strftime("%H:%M")

        except ValueError:
            print(f"Erro: '{hora_str}' não é uma hora válida no formato '{formato_entrada}'. Tente novamente.")

def exibe_agenda():
    cont = 0
    agenda_com_indice = []

    cabecalho = ("ID", "Data", "Hora", "Descrição")
    print('Lista de Compromissos')

    for i in agenda:
        agenda_com_indice.append([cont] + i)
        cont += 1

    print('Lista de Compromissos: ')
    print(tabulate(agenda_com_indice, headers=cabecalho, tablefmt="simple_grid"))

meses_do_ano = {
 1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}

# Gerando a data (mês/ano) para o calendário;
data = datetime.datetime.now()
ano = data.year
mes = data.month
mes_extenso = meses_do_ano[mes]

# Gerando o Calendário
calendario = calendar.month(ano, mes)
print(f"Calendário de {mes_extenso} de {ano}")
print(calendario)

# Construindo Menu
agenda = []
data_cal = []
hora_cal = []
desc_cal = []

opção = 0
while opção != 5:
    print("""\tMenu
[1] Listar Compromissos
[2] Agendar um Compromisso
[3] Alterar um Compromisso
[4] Excluir Compromisso
[5] Sair""")
    opção = int(input('>>> O que deseja fazer? '))

    if opção == 1: # [1] Listar Compromissos
        if len(agenda) > 0:
            exibe_agenda()
        else:
            print('Nenhum Compromisso cadastrado')
    elif opção == 2: # [2] Agendar um Compromisso
        print("\t=-=-=-=-=-=-=- AGENDA -=-=-=-=-=-=-=")

        # Chama a função novamente para obter uma data de evento,
        #data_evento = obter_data_valida("Digite a data do evento (dd/mm/aaaa): ")
        data_cal = obter_data_valida("Digite a data do evento (dd/mm/aaaa): ")
        # Obtendo uma hora de início
        hora_cal = obter_hora_valida("Por favor, digite a hora de início (HH:MM): ")
        desc_cal = str(input('Descrição da agenda: ')).strip()
        id_cal  = gera_id()
        agenda_in = [id_cal, data_cal, hora_cal, desc_cal]
        agenda.append(agenda_in)

    elif opção == 3: # [3] Alterar um Compromisso
        exibe_agenda()
        opc = int(input("Informe o indíce do compromisso que deseja alterar [ 999 - para voltar]: "))
        tam_opc = len(agenda)
        if opc > tam_opc:
            print("Nenhum Compromisso cadastrado")
        elif opc == 999:
            break
        else:
            opc2 = ''
            while opc2 != 0:
                print("""\tO que deseja alterar:
        [1] Data
        [2] Hora
        [3] Descrição
        [0] Sair""")
                opc2 = int(input('>>> O que deseja fazer? '))
                if opc2 == 0:
                    break
                elif opc2 == 1:
                    agenda[opc][opc2] = obter_data_valida("Digite a data do evento (dd/mm/aaaa): ")
                elif opc2 == 2:
                    agenda[opc][opc2] = obter_hora_valida("Por favor, digite a hora de início (HH:MM): ")
                elif opc2 == 3:
                    agenda[opc][opc2] = str(input('Descrição da agenda: ')).strip()
                exibe_agenda()

    elif opção == 4: # [4] Excluir Compromisso
        exibe_agenda()
        opc = int(input("Informe o indíce do compromisso que deseja apagar [ 999 - para voltar]: "))
        tam_opc = len(agenda)
        if opc > tam_opc:
            print(f'Nenhum Compromisso com o índice {opc} cadastrado')
        elif opc == 999:
            break
        else:
            del agenda[opc]
        exibe_agenda()

    elif opção == 5:
        print('Finalizando...')
    else:
        print('Opção inválida. Tente novamente.')
    print('=-' * 10)
    sleep(1)
print('Fim do programa! Volte sempre!')