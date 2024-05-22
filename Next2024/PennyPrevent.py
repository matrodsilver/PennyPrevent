'''
link do colab:
https://colab.research.google.com/drive/1HWflE9BZzIpapgP2--twCMPz0A_geABv#scrollTo=q8z6Kkb36TNA&uniqifier=1
'''

# import streamlit as sl

import streamlit as sl

import tensorflow
from tensorflow import keras

# **Biblioteca para tratar dados**

import pandas as pd

dados = pd.read_csv(r".\Next2024\poseidonTratado.csv")
'Variáveis'
'Nível de Água: '
sl.line_chart(dados['nivel_de_agua'])
'Distância: '
sl.line_chart(dados['ultrassom'])
'Infravermelho: '
sl.line_chart(dados['infravermelho'])
'Infravermelho2: '
sl.line_chart(dados['infravermelho2'])

# **Reduzir variáveis dos dados**

# dados = dados.drop('Unnamed: 0', axis = 1) # por padrão tira coluna criada pelo google


# # Remove colunas digitadas
# desconsideradas = []
# while True:
#   if len(dados.columns) < 3 or input('\nAdicionar colunas a desconsiderar? (s | n)\n').lower() not in ['sim', 's']: # base de dados precisa pelo menos de uma coluna de input e uma de resultado
#     print('_Operação terminada_\n')
#     break

#   # printar colunas atuais
#   print(end='\n| ') # para formatação ficar enclausurada melhor
#   for coluna in dados:
#     print(coluna, end=' | ')

#   colunasDel = sl.text_input('\nEspecifique as colunas a serem desconsideradas (separadas por ´,´):\n').replace(' ', '').split(',') # tira espaços e separa inputs

#   naoEncontradas = []

#   for coluna in colunasDel:
#     if coluna in dados:
#       desconsideradas.append(coluna)
#       dados = dados.drop(coluna, axis = 1)

#     else:
#       naoEncontradas.append(coluna)

#   if len(desconsideradas) > 0:
#     print('\nColunas Desconsideradas:\n| ', end='')
#     for c in desconsideradas:
#       print(c, end= ' | ')

#   if len(naoEncontradas) > 0:
#     print('\nColunas não encontradas:\n| ', end='')
#     for c in naoEncontradas:
#       print(c, end= ' | ')


# DEBUG
dados = dados.drop(['Unnamed: 0', 'created_at', 'entry_id'], axis = 1)

# **Verificação de variáveis**

for coluna in dados:
  debug = ''
  vars = []

  for var in dados[coluna]:
    if var not in vars:
      vars.append(var)

  debug += f'{coluna}: {len(vars)} variáveis'
  
  if len(vars) < 11:
    debug += f'{vars}\n'

f'Dados: {debug}'

# **Tratar variáveis dos dados**

# while True:
#   resultados = sl.text_input('Defina a coluna de resultados: ')

#   if resultados in dados:
#     input = dados.drop(resultados, axis = 1)
#     output = dados[resultados]

#     print(f'\nColuna ´{resultados}´ definida como alvo\n')

#     break

#   else:
#     print('Coluna não encontrada\n')


# print('Input:', end='\n| ')
# for coluna in input:
#   print(coluna, end=' | ')

# print('\n\nOutput:')
# print('|', resultados, '|')


# DEBUG
input = dados.drop('Estado', axis = 1)
output = dados['Estado']

# **Armazenar valores antes da normalização para testes manuais com valores reais**

maximos = []
minimos = []

for i, coluna in enumerate(input):
  print(i, coluna)

  maximos.append((max(input[coluna])))
  minimos.append(min(input[coluna]))

print('max:', maximos,'\nmin:', minimos)

# **Normalização**
'Máximos e mínimos das variáveis antes da normalização\n'

print('_______Original_______')
for i, coluna in enumerate(input):
  f'{coluna}: {minimos[i]} ~ {maximos[i]}' # valores originais
'\n'

'___Após normalização___'
for i, coluna in enumerate(input):
  input[coluna] = [valor/(maximos[i] - minimos[i]) for valor in input[coluna]]

  f'{coluna}: {min(input[coluna])} ~ {max(input[coluna])}' # valores após normalização


outputStr2Int = {'funcional': 0,
              'problema encontrado': 1,
              'disfuncional': 2} # oque predict retorna

output = output.replace(outputStr2Int)

output = pd.DataFrame(output)

from sklearn.model_selection import train_test_split

treino, teste, respostas_treino, respostas_teste = train_test_split(input, output, stratify = output, test_size = .15, random_state = 5)

# **Criação, compilação e treino do modelo**

camadas = 256 # n de neurônios

modelo = keras.Sequential(
    [
        keras.layers.Input(shape=(4,)),
        keras.layers.Dense(camadas, activation = tensorflow.nn.selu),
        keras.layers.Dropout(.15),
        keras.layers.Dense(3, activation = tensorflow.nn.softmax)
    ]
)

modelo.compile(optimizer = 'adam', loss = 'sparse_categorical_crossentropy', metrics = ['accuracy'])

historico = modelo.fit(treino, respostas_treino, epochs = 16, validation_split = 0.15) # , batch_size = 96)

import matplotlib.pyplot as plt

h = historico.history

plt.plot(h['accuracy'])
plt.plot(h['val_accuracy'])
plt.title('Accuracy/Epoch')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend(['treino', 'validação'])

plt.plot(h['loss'])
plt.plot(h['val_loss'])
plt.title('Loss/Epoch')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend(['treino', 'validação'])

import numpy as np
from numpy import argmax

guesses = modelo.predict(teste)

erros = 0
for i, valor in enumerate(guesses):
  estado_predito = argmax(valor)
  estado_real = respostas_teste['Estado'].iloc[i] # get value's index
  if estado_predito != estado_real:
    erros += 1

f'acertos = {100 - erros/100}%'

valores_teste = [10, -1, 0, 0] # [nlvDeÁgua, Distância(Cm), 0b, 0b]

for i, coluna in enumerate(input):
  print(i, coluna)

  valores_teste[i] = valores_teste[i]/(maximos[i] - minimos[i])

f'Valores de teste: {valores_teste}'

'Treino do modelo'
sl.line_chart(h['accuracy'])
'Dados treinados com sucesso'

# **Prova de valores**

guess = np.array(valores_teste)  # Replace with your some value
guess_reshape = np.expand_dims(guess, axis=0)  # Add a batch dimension

estado_predito = modelo.predict(guess_reshape)

classe_predita = argmax(estado_predito[0])  # Assuming categorical output

f"Predição do modelo:\n{list(outputStr2Int.keys())[classe_predita]}" # se 2 valores do dicionário são iguais, mostra o primeiro

# **Salvar e carregar modelo**

modelo.save('modelo.h5')

from tensorflow.keras.models import load_model

modelo_salvo = load_model(r'.\Next2024\modelo (1).h5')

teste_modelo_salvo = modelo_salvo.predict(teste)

erros = 0
for i, valor in enumerate(teste_modelo_salvo):
  estado_predito = argmax(valor)
  estado_real = respostas_teste['Estado'].iloc[i] # get value's index
  if estado_predito != estado_real:
    erros += 1

print('Acertos =', 100 - erros/100,'%')

# Make prediction
estado_predito = modelo_salvo.predict(guess_reshape)

print(estado_predito)

# Process the prediction (argmax for categorical output)
classe_predita = argmax(estado_predito[0])  # Assuming categorical output
print(classe_predita)

# Print the predicted class based on your dictionary
print(f"Predição:\n{list(outputStr2Int.keys())[classe_predita]}") # se 2 valores do dicionário são iguais, mostra o primeiro

# **Prever em tempo real**

# from pushbullet import Pushbullet
import requests
# import time

# esta função retorna o valor mais atual do banco de dados
def pegarUltimosDados():
  urlTSultimoResultado = f'https://api.thingspeak.com/channels/2127654/feeds.json?api_key=<token>results=1'

  resposta = requests.get(urlTSultimoResultado)

  if resposta.status_code == 200:
    return resposta.json()
  else:
    print('Erro na requisição')
    return {}

# while True: # debug: fazer loop
ultDados = pegarUltimosDados()['feeds'][0]

# normalização  debug: Tornar dinâmico (com drop de dados etc.)
dados_prever = [ultDados['field1'], ultDados['field2'], ultDados['field3'], ultDados['field4']]
dados_prever = [float(v) for v in dados_prever]

print(dados_prever)

for i, coluna in enumerate(input):
  dados_prever[i] = dados_prever[i]/(maximos[i] - minimos[i])

print(dados_prever)

dado_prever = np.array(dados_prever)  # Replace with your some value
dado_reshape = np.expand_dims(dado_prever, axis=0)  # Add a batch dimension

predito = modelo.predict(dado_reshape)

dados_classe_predita = argmax(predito[0])  # Assuming categorical output

f"Predição em tempo real:\n{list(outputStr2Int.keys())[dados_classe_predita]}" # se 2 valores do dicionário são iguais, mostra o primeiro

# # caso o valor mais atual do banco de dados seja maior que um volume determinado, esta função envia uma notificação de aviso
# def avisar():

#   volume = float(pegarUltimosDados()['feeds'][0]['field2'])

#   if volume < 30:

#     eu = '<token>'  # <token> é substituído pelo valor do token no código

#     usuarios = [eu]

#     for usuario in usuarios:
#       pbt = Pushbullet(usuario)
#       pbt.push_note(
#           '⚠️Aviso⚠️', f'⚠ O sistema【𝟭】atingiu o limite de volume ⚠\nAtualmente em: {57- volume} cm')


# while True:
#   avisar()

#   time.sleep(20)

'\nAnálise do chatbot'
import openai

chave_api = "sk-proj-rRLYbZUUdPvgnU6HCGz6T3BlbkFJOb9GRbnSdSZcjX1Cjts1"

openai.api_key = chave_api

def enviar_conversa(mensagem, lista_mensagens=[]):

    lista_mensagens.append(
        {"role":"user", "content": mensagem}
        )

    resposta = openai.chat.completions.create(
        model = "gpt-3.5-turbo",
        messages = lista_mensagens,
    )
    return resposta.choices[0].message.content

lista_mensagens = []
texto = f'Analise esses dados:\n{debug}\n'
texto += f'valores_teste = [10, -1, 0, 0]\n'
texto += f'Predição do teste: {list(outputStr2Int.keys())[classe_predita]}'
resposta = enviar_conversa(texto, lista_mensagens)
lista_mensagens.append({'role': 'user', 'content': resposta})

print(resposta)
f'{resposta}'
