import streamlit as sl
import tensorflow
# from tensorflow import keras #? dando erro ao chamar dessa forma (?)
import keras
import pandas as pd # **Biblioteca para tratar dados**


# **Verificar dados**
# caminho_do_arquivo = r".\Next2024\poseidonTratado.csv" # mudar caminho do arquivo


# choose file
if sl.button('Escolher arquivo'):
  from tkinter import Tk, filedialog

  root = Tk()
  root.title('Escolha o arquivo')

  caminho_do_arquivo = filedialog.askopenfilename(initialdir='/', title='Selecione o arquivo', filetypes=(('todos os arquivos', '*.*'),))

else:
  caminho_do_arquivo = r".\Next2024\poseidonTratado.csv"
  "Rodando arquivo de exemplo (default)"

# json
if caminho_do_arquivo.split('.')[-1] == 'json':
  print('json')
  dados = pd.read_json(caminho_do_arquivo)
  
# csv
else:
  print('csv')
  
  dados = pd.read_csv(caminho_do_arquivo)


'Variáveis'
'Nível de Água:'
sl.line_chart(dados['nivel_de_agua'])
'Distância:'
sl.line_chart(dados['ultrassom'])
'Infravermelho:'
sl.line_chart(dados['infravermelho'])
'Infravermelho2:'
sl.line_chart(dados['infravermelho2'])


# **Reduzir variáveis dos dados**
dados = dados.drop('Unnamed: 0', axis = 1) # por padrão tira coluna criada pelo google #? talvez tenha de remover se não estiver pelo colab

# Remove colunas digitadas
desconsideradas = []

resposta = sl.text_input('Adicionar colunas a desconsiderar? (s | n)').lower()

etapa = 0 # declara variável das etapas do processo

# Função que verifica input do usuário sobre desconsiderar colunas
def desconsiderarColunas():
  global etapa
  
  if (len(dados.columns) < 3 or resposta not in ['sim', 's']) and resposta != '': # base de dados precisa pelo menos de uma coluna de input e uma de resultado (por isso se é menor que 3 para)
    '_Operação de desconsideração terminada_'
    etapa = 2 # escolher colunas alvo
    
  elif len(dados.columns) > 3 and resposta in ['sim', 's'] and resposta != '':
    etapa = 1 # escolher colunas a desconsiderar


def exibirColunasAtuais():
  #
  # printar colunas atuais
  f'_ Colunas atuais: _' #? esta linha não aparece sem f (f'') na frente (?) 
  for coluna in dados:
    f'| {coluna} |'


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
      '_ Colunas desconsideradas: _'
      for c in desconsideradas:
        f'| {c} | '
      
      etapa = 2

    if len(naoEncontradas) > 0:
      '_ Colunas não encontradas: _'
      for c in naoEncontradas:
        f'| {c} | '
    
    exibirColunasAtuais()


# Perguntar se usário deseja adicionar colunas a serem desconsideradas
desconsiderarColunas()

if etapa == 1: # se o usuário quiser desconsiderar mais colunas
  exibirColunasAtuais()
  
  selecionarColunas()

# # DEBUG
# dados = dados.drop(['Unnamed: 0', 'created_at', 'entry_id'], axis = 1)


# **Verificação de variáveis**
if etapa == 2:
  '--Dados--'
  
  for coluna in dados:
    exibir = ''
    vars = []

    for var in dados[coluna]:
      if var not in vars:
        vars.append(var)

    exibir += f'{coluna}: {len(vars)} variáveis '
    
    if len(vars) < 11:
      exibir += f'{vars}'

    f'{exibir}'


  # **Tratar variáveis dos dados**
  resultados = sl.text_input('Defina a coluna de resultados: ')

  try:
    inputDados = dados.drop(resultados, axis = 1)
    outputDados = dados[resultados]

    f'Coluna ´{resultados}´ definida como alvo'
    
    '__Input__'
    for coluna in inputDados:
      f'{coluna} | '

    f'__Output__'
    f'| {resultados} |'
    
    etapa = 3

  except:
    'Digite uma Coluna existente na base de dados'
    
    # 'Coluna não encontrada, usando última coluna como resultado'
    # input = dados.drop(dados.keys()[len(dados.keys())-1], axis = 1)
    # output = dados[dados.keys()[len(dados.keys())-1]]


# # DEBUG
# input = dados.drop('Estado', axis = 1)
# output = dados['Estado']

# ! Armazenar valores antes da normalização para testes manuais com valores reais !
if etapa == 3:
  maximos = []
  minimos = []

  ': debug :'
  for i, coluna in enumerate(inputDados):
    f'{i}, {coluna}' # debug (retirar no final)

    maximos.append((max(inputDados[coluna])))
    minimos.append(min(inputDados[coluna]))

  f'max: {maximos} ~ min:, {minimos}'

  # **Normalização**
  'Máximos e mínimos das variáveis antes da normalização'

  '_______Original_______'
  for i, coluna in enumerate(inputDados):
    f'{coluna}: {minimos[i]} ~ {maximos[i]}' # valores originais

  '___Após normalização___'
  for i, coluna in enumerate(inputDados):
    inputDados[coluna] = [valor/(maximos[i] - minimos[i]) for valor in inputDados[coluna]]

    f'{coluna}: {min(inputDados[coluna])} ~ {max(inputDados[coluna])}' # valores após normalização


  outputStr2Int = {'funcional': 0,
                'problema encontrado': 1,
                'disfuncional': 2} # oque predict retorna

  outputDados = outputDados.replace(outputStr2Int)

  outputDados = pd.DataFrame(outputDados)

  from sklearn.model_selection import train_test_split

  treino, teste, respostas_treino, respostas_teste = train_test_split(inputDados, outputDados, stratify = outputDados, test_size = .15, random_state = 5)

  # **Criação, compilação e treino do modelo**
  camadas = 256 # n de neurônios

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
  
  'Treino do modelo'
  sl.line_chart(h['accuracy'])
  'Dados treinados com sucesso'

  import numpy as np
  from numpy import argmax

  # teste do modelo
  guesses = modelo.predict(teste)

  erros = 0
  for i, valor in enumerate(guesses):
    estado_predito = argmax(valor)
    estado_real = respostas_teste['Estado'].iloc[i] # get value's index
    if estado_predito != estado_real:
      erros += 1

  f'Acertos do modelo = {100 - erros/100}%'


  # **Testar modelo**
  # valores_teste = [10, -1, 0, 0] # [nlvDeÁgua, Distância(Cm), 0b, 0b]
  
  colunas = ''
  
  # exibir dados a serem simulados
  'Colunas:'
  for colunaDeDados in inputDados:
    colunas += str(colunaDeDados) + ' | '
  
  f'| {colunas}'
    
  valores_teste = sl.text_input('Testar modelo:').replace(' ', '').split(',')

  if valores_teste != '':
    try:
      valores_teste = [float(v) for v in valores_teste]
      
      for i, coluna in enumerate(inputDados):
        f'{i}, {coluna}' # debug (retirar no final)

        valores_teste[i] = valores_teste[i]/(maximos[i] - minimos[i])

      f'Valores de teste normalizados: {valores_teste}'

      guess = np.array(valores_teste)  # Replace with your some value
      guess_reshape = np.expand_dims(guess, axis=0)  # Add a batch dimension

      estado_predito = modelo.predict(guess_reshape)

      classe_predita = argmax(estado_predito[0])  # Assuming categorical output
      
      predito_teste = list(outputStr2Int.keys())[classe_predita]

      f"Predição do teste: '{predito_teste}'" # se 2 valores do dicionário são iguais, mostra o primeiro

      # **Salvar e carregar modelo**
      modelo.save('modelo.h5')

      from tensorflow.keras.models import load_model #type: ignore #? informa erro mas é funcional (?)

      modelo_salvo = load_model(r'.\Next2024\modelo (1).h5')

      # #** re-testando o modelo salvo **
      # teste_modelo_salvo = modelo_salvo.predict(teste)

      # erros = 0
      # for i, valor in enumerate(teste_modelo_salvo):
      #   estado_predito = argmax(valor)
      #   estado_real = respostas_teste['Estado'].iloc[i] # get value's index
      #   if estado_predito != estado_real:
      #     erros += 1

      # f'Acertos = {100 - erros/100}%'

      # Make prediction
      estado_predito = modelo_salvo.predict(guess_reshape)

      # f'{estado_predito}' # debug (retirar no final)  # mostra as probabilidades de cada classe

      # Process the prediction (argmax for categorical output)
      classe_predita = argmax(estado_predito[0])  # Assuming categorical output
      # f'{classe_predita}'
      
      predito_modelo = list(outputStr2Int.keys())[classe_predita]

      # Print the predicted class based on your dictionary
      f'Predição do modelo salvo: "{predito_modelo}"' # se 2 valores do dicionário são iguais, mostra o primeiro

    except:
      'digite valores coerentes de teste para cada coluna, separados por ´,´'

  # ** Notificar usuários em tempo real em caso de problema **
  # from pushbullet import Pushbullet #? problema pra rodar pushbullet no script com streamlit
  import pywhatkit as wp
  from time import sleep as delay
  import requests

  def pegarUltimosDados():
    urlTSultimoResultado = f'https://api.thingspeak.com/channels/2127654/feeds.json?api_key=MZB0IDFGQR9AQVBW&results=1'

    resposta = requests.get(urlTSultimoResultado)

    if resposta.status_code == 200:
      return resposta.json()
    else:
      f'Erro na requisição'
      return {}
    
  def avisar():
    # esta função retorna o valor mais atual do banco de dados
    ultDados = pegarUltimosDados()['feeds'][0]

    # normalização  debug: Tornar dinâmico (com drop de dados etc.)
    dados_prever = [ultDados['field1'], ultDados['field2'], ultDados['field3'], ultDados['field4']]
    dados_prever = [float(v) for v in dados_prever]

    f'{dados_prever}' # debug (retirar no final)

    for i, coluna in enumerate(inputDados):
      dados_prever[i] = dados_prever[i]/(maximos[i] - minimos[i])

    f'{dados_prever}' # debug (retirar no final)

    dado_prever = np.array(dados_prever)  # Replace with your some value
    dado_reshape = np.expand_dims(dado_prever, axis=0)  # Add a batch dimension

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
