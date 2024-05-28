'''
#• links relevantes:
#• ex.   → https://www.youtube.com/watch?v=QkDiBWJ8Row
#• docs. → https://firebase.google.com/docs/reference/rest/database?hl=pt
'''

import requests
import json

link = 'https://predito-85975-default-rtdb.firebaseio.com'

#* Edita os dados *#
def editarDados():
    ultimaPredicao = {'ultimo': 'disfuncional'}
    requisicao_editar = requests.patch(f'{link}/Predito/.json', data = json.dumps(ultimaPredicao)) #! parâmetro "data" necesário para a função editar dados de acordo

    print(requisicao_editar) # retorna o status da requisição
    print(requisicao_editar.text) # retorna o conteúdo da requisição

#* Retorna dados como um dicionário python *#
def pegarDados():
    requisicao_pegar = requests.get(f'{link}/.json') #! parâmetros desnecessários para pegar dados

    print(requisicao_pegar)
    print(requisicao_pegar.text)
    print(requisicao_pegar.json()) #! json() retorna o conteúdo como dicionário Python

    # print(requisicao_pegar.text['Predito']['ultimo']) #? .json() tem que ser passado para ser tratado como dicionário
    print(requisicao_pegar.json()['Predito']['ultimo'])
    
    return requisicao_pegar.json()


editarDados()
pegarDados()