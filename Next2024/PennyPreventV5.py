import streamlit as sl
from io import StringIO
import pandas as pd


# **Carregar dados**
uploaded_file = sl.file_uploader("Escolher arquivo", type=['csv', 'json'])
if uploaded_file is not None:
  # To read file as bytes:
  bytes_data = uploaded_file.getvalue()
  # To convert to a string based IO:
  stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
  
  if uploaded_file.name.split('.')[-1] == 'json':  #! json
    dados = pd.read_json(stringio)
  
  elif uploaded_file.name.split('.')[-1] == 'csv': #! csv
    dados = pd.read_csv(stringio)

else:
  dados = pd.read_csv(r".\Next2024\poseidonTratado+.csv")
  "Rodando arquivo de exemplo (default)"


'Current Columns'
for dado in dados.columns:
  f'{dado}'
  
  try:
    dadosGraf = [float(valor) for valor in dados[dado]]
    sl.line_chart(dadosGraf)
  except:
    '10 primeiros valores'
    sl.line_chart(dados[dado].head(10))


# **Reduzir variáveis dos dados**
if '' in dados.columns:
  dados = dados.drop('', axis = 1)

desconsideradas = []

resposta = sl.text_input('Adicionar colunas a desconsiderar? (s | n)').lower()

etapa = 0 # variável das etapas do processo (se faz necessário no streamlit)

# função que define as colunas a serem desconsideradas por input do usuário
def desconsiderarColunas():
  global etapa
  
  if (len(dados.columns) < 3 or resposta not in ['sim', 's']) and resposta != '': # base de dados precisa pelo menos de uma coluna de input e uma de resultado (por isso se é menor que 3 para)
    etapa = 2 # escolher colunas alvo
    
  elif len(dados.columns) > 3 and resposta in ['sim', 's'] and resposta != '':
    etapa = 1 # escolher colunas a desconsiderar


# função que exibe colunas atuais
def exibirColunasAtuais():
  f'_ Colunas atuais: _' #? esta linha não aparece sem f (f'') na frente (?) 
  cols = ''
  for coluna in dados:
    cols += f'| {coluna} |'
  
  sl.write(cols)


# função que redefine e exibe os dados após a desconsideração das colunas escolhidas
def selecionarColunas():
  global dados
  global etapa
  
  colunasDel = sl.text_input('Especifique as colunas a serem desconsideradas (separadas por ´,´):').replace(' ', '').split(',') # tira espaços e separa inputs

  naoEncontradas = []

  if colunasDel != '':
    for coluna in colunasDel:
      if coluna in dados:
        desconsideradas.append(coluna)
        dados = dados.drop(coluna, axis = 1)

      else:
        naoEncontradas.append(coluna)

    if len(desconsideradas) > 0:
      colsDes = ''
      
      '_ Colunas desconsideradas: _'
      for c in desconsideradas:
        colsDes += f'| {c} |'
      
      sl.write(colsDes)
      
      etapa = 2

    if len(naoEncontradas) > 0:
      colsNao = ''
      
      '_ Colunas não encontradas: _'
      for c in naoEncontradas:
        colsNao += f'| {c} |'
      
      sl.write(colsNao)
    
    exibirColunasAtuais()


desconsiderarColunas()

if etapa == 1: # se o usuário quiser desconsiderar mais colunas
  selecionarColunas()


if etapa == 2:
  # **Tratar variáveis dos dados**
  resultados = sl.text_input('Defina a coluna de resultados: ')

  try:
    inputDados = dados.drop(resultados, axis = 1)
    outputDados = dados[resultados]

    f'Coluna ´{resultados}´ definida como alvo'

    etapa = 3

  except:
    'Digite uma Coluna existente na base de dados'

# !Armazena valores antes da normalização para testes manuais com valores reais!
if etapa == 3:
  maximos = []
  minimos = []

  for i, coluna in enumerate(inputDados):
    maximos.append((max(inputDados[coluna])))
    minimos.append(min(inputDados[coluna]))

  # **Normalização**
  for i, coluna in enumerate(inputDados):
    inputDados[coluna] = [valor/(maximos[i] - minimos[i]) for valor in inputDados[coluna]]

  # **resignificar resultados**
  outputStr2Int = {} # definindo dicionário de resultados
  
  n = 0
  for key in outputDados:
      if key not in outputStr2Int:
          outputStr2Int[key] = n
          n += 1

  outputDados = outputDados.replace(outputStr2Int)

  outputDados = pd.DataFrame(outputDados)

  from sklearn.model_selection import train_test_split

  treino, teste, respostas_treino, respostas_teste = train_test_split(inputDados, outputDados, stratify = outputDados, test_size = .15, random_state = 5)

  # **Criação, compilação e treino do modelo**
  camadas = 256 # n de neurônios

  import tensorflow
  # from tensorflow import keras #? dando erro ao chamar dessa forma (?)
  import keras

  modelo = keras.Sequential(
      [
          keras.layers.Input(shape=(len(inputDados.columns),)),
          keras.layers.Dense(camadas, activation = tensorflow.nn.selu),
          keras.layers.Dropout(.15),
          keras.layers.Dense(3, activation = tensorflow.nn.softmax)
      ]
  )

  'Treinando modelo...'
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
  
  'Resultados do modelo'
  sl.line_chart(h['accuracy'])

  import numpy as np
  from numpy import argmax

  # **Teste do modelo**
  guesses = modelo.predict(teste)

  erros = 0
  for i, valor in enumerate(guesses):
    estado_predito = argmax(valor)
    estado_real = respostas_teste['Estado'].iloc[i] # get value's index
    if estado_predito != estado_real:
      erros += 1

  f'Acertos do modelo = {100 - erros/len(guesses)*100}%'


  # **Testar modelo com valores manuais**
  colunas = ''
  
  # exibir dados a serem simulados
  'Colunas a simular:'
  for colunaDeDados in inputDados:
    colunas += str(colunaDeDados) + ' | '
  
  f'| {colunas}'

  valores_teste = sl.text_input('Testar modelo:').replace(' ', '').split(',')

  if valores_teste != '':
    try:
      valores_teste = [float(v) for v in valores_teste]
      
      for i, coluna in enumerate(inputDados):
        valores_teste[i] = valores_teste[i]/(maximos[i] - minimos[i])

      guess = np.array(valores_teste)  # Replace with your some value
      guess_reshape = np.expand_dims(guess, axis=0)  # Add a batch dimension

      estado_predito = modelo.predict(guess_reshape)

      classe_predita = argmax(estado_predito[0])  # Assuming categorical output
      
      predito_teste = list(outputStr2Int.keys())[classe_predita]

      f"Predição do teste manual: '{predito_teste}'" # se 2 valores do dicionário são iguais, mostra o primeiro

      #. # **Salvar e carregar modelo**
      #. modelo.save('modelo.h5')

      #. from tensorflow.keras.models import load_model #type: ignore #? informa erro mas é funcional (?)

      #. modelo_salvo = load_model(r'.\Next2024\modelo (1).h5')

      #. # #** re-testando o modelo salvo **
      #. # teste_modelo_salvo = modelo_salvo.predict(teste)

      #. # erros = 0
      #. # for i, valor in enumerate(teste_modelo_salvo):
      #. #   estado_predito = argmax(valor)
      #. #   estado_real = respostas_teste['Estado'].iloc[i] # get value's index
      #. #   if estado_predito != estado_real:
      #. #     erros += 1

      #. # f'Acertos = {100 - erros/len(teste_modelo_salvo)*100}%'

      #. # Make prediction
      #. estado_predito = modelo_salvo.predict(guess_reshape)

      #. # f'{estado_predito}' # debug (retirar no final)  # mostra as probabilidades de cada classe

      #. # Process the prediction (argmax for categorical output)
      #. classe_predita = argmax(estado_predito[0])  # Assuming categorical output
      #. # f'{classe_predita}'
      
      #. predito_modelo = list(outputStr2Int.keys())[classe_predita]

      #. # Print the predicted class based on your dictionary
      #. f'Predição do modelo salvo: "{predito_modelo}"' # se 2 valores do dicionário são iguais, mostra o primeiro


    except:
      'digite valores coerentes de teste para cada coluna, separados por ´,´'

  # ** Notificar usuários em tempo real em caso de problema **
  # from pushbullet import Pushbullet #? problema pra rodar pushbullet no script com streamlit
  import pywhatkit as wp
  from time import sleep as delay
  import requests

  # função que retorna o valor mais atual do banco de dados
  def pegarUltimosDados():
    ultimosDados = f'https://predito-85975-default-rtdb.firebaseio.com/Dados/.json'

    return requests.get(ultimosDados).json()
    
  def avisar():
    dados_prever = pegarUltimosDados()
    
    f'{dados_prever}'

    for atributo in dados_prever:
      dados_prever[atributo] = float(dados_prever[atributo])

    f'Prevendo os dados: {dados_prever}' # debug (retirar no final)

    dados_isolados = []
    for valor in dados_prever:
      dados_isolados.append(dados_prever[valor])

    for i, coluna in enumerate(inputDados):
      dados_isolados[i] = dados_isolados[i]/(maximos[i] - minimos[i])

    dados_isolados = np.array(dados_isolados)  # Replace with your some value
    dado_reshape = np.expand_dims(dados_isolados, axis=0)  # Add a batch dimension

    predito = modelo.predict(dado_reshape)

    dados_classe_predita = argmax(predito[0])  # Assuming categorical output #
    
    predicao_atual = list(outputStr2Int.keys())[dados_classe_predita]

    f"Predição em tempo real: '{predicao_atual}'" # se 2 valores do dicionário são iguais, mostra o primeiro


    # if volume < 30: # 30000:
    
    # #* Pegar dados do output
    # for coluna in dados:
    #   exibir = ''
    #   vars = []

    #   for var in dados[coluna]:
    #     if var not in vars:
    #       vars.append(var)

    #   exibir += f'{coluna}: {len(vars)} variáveis '
      
    #   if len(vars) < 11:
    #     exibir += f'{vars}'

    # f'{exibir}'
    
    
    if predicao_atual in ['placeHolder']:#['disfuncional', 'problema encontrado']:
      pb_usuarios = ['o.9CYuBlpove3ErChfkLDjcmkNcjquJ1oz']
      wp_usuarios = ['+5511996568160']
      
      # titulo, mensagem = '⚠️Aviso⚠️', f'⚠ O sistema【𝟭】atingiu o limite de volume ⚠\nAtualmente em: {57- volume} cm'
      titulo, mensagem = '⚠️Aviso⚠️', f'Foi previsto que o sistema 【𝟭】 está {predicao_atual}'

      for usuario in pb_usuarios:
        # pbt = Pushbullet(usuario)
        # pbt.push_note(titulo, mensagem)
        pass
      
      for usuario in wp_usuarios:
        wp.sendwhatmsg_instantly(usuario, titulo+'\n'+mensagem, 15) #True, 15) #type: ignore


  with open('relat.txt', 'w') as modelo_config:
    modelo_config.write(f'{maximos},{minimos}')


  while True:
    avisar()

    delay(16)

# '\nAnálise do chatbot'
# import openai

# chave_api = "sk-proj-rRLYbZUUdPvgnU6HCGz6T3BlbkFJOb9GRbnSdSZcjX1Cjts1"

# openai.api_key = chave_api

# def enviar_conversa(mensagem, lista_mensagens=[]):

#     lista_mensagens.append(
#         {"role":"user", "content": mensagem}
#         )

#     resposta = openai.chat.completions.create(
#         model = "gpt-3.5-turbo",
#         messages = lista_mensagens,
#     )
#     return resposta.choices[0].message.content

# lista_mensagens = []
# texto = f'Analise esses dados:\n{debug}\n'
# texto += f'valores_teste = [10, -1, 0, 0]\n'
# texto += f'Predição do teste: {list(outputStr2Int.keys())[classe_predita]}'
# resposta = enviar_conversa(texto, lista_mensagens)
# lista_mensagens.append({'role': 'user', 'content': resposta})

# print(resposta)
# f'{resposta}'