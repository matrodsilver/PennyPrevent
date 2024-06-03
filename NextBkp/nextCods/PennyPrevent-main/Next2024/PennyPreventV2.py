import streamlit as sl
import tensorflow
# from tensorflow import keras #? dando erro ao chamar dessa forma (?)
import keras
import pandas as pd # **Biblioteca para tratar dados**

gui = "D:/Next/nextCods/PennyPrevent-main/Next2024/fotos/gui.jpeg" # mudar caminho da foto
bizon = "D:/Next/nextCods/PennyPrevent-main/Next2024/fotos/bizon.jpeg" # mudar caminho da foto
couto = "D:/Next/nextCods/PennyPrevent-main/Next2024/fotos/couto.jpeg" # mudar caminho da foto
mat = "D:/Next/nextCods/PennyPrevent-main/Next2024/fotos/mat.jpeg" # mudar caminho da foto

# **Verificar dados**
# caminho_do_arquivo = r".\Next2024\poseidonTratado.csv" # mudar caminho do arquivo

sl.set_page_config(layout="wide")
tab1, tab2, tab3 = sl.tabs(["Home", "Dashboard/IA", "Equipe"])

in_out = ''
testes = ''
exibir = ''
valores_de_teste_inputados = ''
valor_predicao = ''

dados_tempo_real = None

with tab2:
   
  sl.markdown("<br>", unsafe_allow_html=True)
  sl.markdown("<br>", unsafe_allow_html=True)

  # choose file
  if sl.button('Escolher arquivo'):
    from tkinter import Tk, filedialog

    root = Tk()
    root.title('Escolha o arquivo')

    caminho_do_arquivo = filedialog.askopenfilename(initialdir='/', title='Selecione o arquivo', filetypes=(('todos os arquivos', '*.*'),))

  else:
    caminho_do_arquivo = r"D:/Next/nextCods/PennyPrevent-main/Next2024/poseidonTratado.csv" # mudar caminho
    "Rodando arquivo de exemplo (default)"

  sl.markdown("<br>", unsafe_allow_html=True)
  sl.markdown("<br>", unsafe_allow_html=True)

  sl.markdown('<div style="font-weight: bold; font-size: 30px"> Dashboard <div/>', unsafe_allow_html=True)
  sl.markdown("<br>", unsafe_allow_html=True)
  # json
  if caminho_do_arquivo.split('.')[-1] == 'json':
    print('json')
    dados = pd.read_json(caminho_do_arquivo)
    
  # csv
  else:
    print('csv')
    caminho_do_arquivo = r"D:/Next/nextCods/PennyPrevent-main/Next2024/poseidonTratado.csv" # mudar caminho do arquivo
    dados = pd.read_csv(caminho_do_arquivo)

  col1, col2  = sl.columns(2) 
  

  with col1:
    sl.markdown('<div > Nível de Água: <div/>', unsafe_allow_html=True)
    sl.markdown('<div style=" background-color: #82c9ff; color: white; width: 92px; height: 3px;"> <div/>', unsafe_allow_html=True)
    sl.line_chart(dados['nivel_de_agua'])
            
    sl.markdown('<div style=""> Distância: <div/>', unsafe_allow_html=True)
    sl.markdown('<div style=" background-color: #82c9ff; color: white; width: 61px; height: 3px;"> <div/>', unsafe_allow_html=True)
    sl.line_chart(dados['ultrassom'])

  with col2:  
    sl.markdown('<div style=""> Infravermelho: <div/>', unsafe_allow_html=True)
    sl.markdown('<div style=" background-color: #82c9ff; color: white; width: 95px; height: 3px;"> <div/>', unsafe_allow_html=True)
    sl.line_chart(dados['infravermelho'])
            
    sl.markdown('<div style=""> Infravermelho 2: <div/>', unsafe_allow_html=True)
    sl.markdown('<div style=" background-color: #82c9ff; color: white; width: 105px; height: 3px;"> <div/>', unsafe_allow_html=True)
    sl.line_chart(dados['infravermelho2'])


  # **Reduzir variáveis dos dados**
  
  with col1:
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
        
        vars = []

        for var in dados[coluna]:
          if var not in vars:
            vars.append(var)

        exibir += f'''{coluna}: {len(vars)} variáveis
        
        '''
        
        if len(vars) < 11:
          exibir += f'{vars}\n'
        else:
          exibir += f'primeiros 10 valores: {vars[:11]}\n'

      f'{exibir}'


      # **Tratar variáveis dos dados**
      resultados = sl.text_input('Defina a coluna de resultados: ')

      try:
        inputDados = dados.drop(resultados, axis = 1)
        outputDados = dados[resultados]

        in_out += f'Coluna ´{resultados}´ definida como coluna alvo'
        
        in_out += '\nInput:\n|'
        for coluna in inputDados:
          in_out += f'{coluna} | '

        in_out += f'\n\nOutput:\n|'
        in_out += f'{resultados} | '
        
        f'{in_out}'

        
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
        testes += f'{i}: {coluna}\n'
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
              keras.layers.Input(shape=(4,)),
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
      
      sl.markdown('<div style=""> Treino do modelo<div/>', unsafe_allow_html=True)
      sl.markdown('<div style=" background-color: #82c9ff; color: white; width: 115px; height: 3px;"> <div/>', unsafe_allow_html=True)
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
      

## IA
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

      


      if valores_teste != '':
      

        try:
          valores_de_teste_inputados = str(valores_teste)
          
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

          valor_predicao = predito_teste

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

      lista_mensagens = []
      texto = f'Analise esses dados:\n{exibir}\n'    
      texto += f'{in_out}\n'
      texto += f'{valores_de_teste_inputados}'
      texto += f'Predição do teste: {valor_predicao}'
      resposta = enviar_conversa(texto, lista_mensagens)
      lista_mensagens.append({'role': 'user', 'content': resposta})

    ##colocar na coluna 2
      print(resposta)
      f'{resposta}'
      
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
        global dados_tempo_real
        # esta função retorna o valor mais atual do banco de dados
        ultDados = pegarUltimosDados()['feeds'][0]

        # normalização  debug: Tornar dinâmico (com drop de dados etc.)
        dados_prever = [ultDados['field1'], ultDados['field2'], ultDados['field3'], ultDados['field4']]
        dados_prever = [float(v) for v in dados_prever]

        if dados_prever != dados_tempo_real:
          f'{dados_prever}' # debug (retirar no final)

          for i, coluna in enumerate(inputDados):
            dados_prever[i] = dados_prever[i]/(maximos[i] - minimos[i])

          f'{dados_prever}' # debug (retirar no final)
          
          dados_tempo_real = dados_prever

        dado_prever = np.array(dados_prever)  # Replace with your some value
        dado_reshape = np.expand_dims(dado_prever, axis=0)  # Add a batch dimension

        predito = modelo.predict(dado_reshape)

        dados_classe_predita = argmax(predito[0])  # Assuming categorical output #
        
        predicao_atual = list(outputStr2Int.keys())[dados_classe_predita]

        global predicao_modelo
        if predicao_modelo != predicao_atual: 
          f"Predição em tempo real: '{predicao_atual}'" # se 2 valores do dicionário são iguais, mostra o primeiro
          predicao_modelo = predicao_atual

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

      predicao_modelo=None

      while True:
        avisar()

        delay(16)

  with col2:
    sl.markdown('<div style="font-weight: bold; font-size: 20px">Análise do chatbot:<div/>', unsafe_allow_html=True)
    sl.markdown('<div style=" background-color: #82c9ff; color: white; width: 165px; height: 3px;"> <div/>', unsafe_allow_html=True)
    



with tab1:
  sl.markdown("<br>", unsafe_allow_html=True)
  sl.markdown("<br>", unsafe_allow_html=True)
  sl.markdown('<div style="font-weight: bold; font-size: 20px"> Projeto em conjunto com a empresa Reply: <div/>', unsafe_allow_html=True)
  sl.markdown('<div style=" background-color: #82c9ff; color: white; width: 370px; height: 3px;"> <div/>', unsafe_allow_html=True)
  sl.markdown('<div> Sistema de Coleta de dados para evitar prejuízo físico e monetário por manutenções e gerenciamento tardio do maquinário.<div/>', unsafe_allow_html=True)
  sl.markdown("<br>", unsafe_allow_html=True) #espaçamento
  sl.markdown("<br>", unsafe_allow_html=True)
  sl.markdown("<br>", unsafe_allow_html=True)
   
   
  sl.markdown('<div style="font-weight: bold; font-size: 20px"> Funcionamento do sistema: <div/>', unsafe_allow_html=True)
  sl.markdown('<div style=" background-color: #82c9ff; color: white; width: 240px; height: 3px;"> <div/>', unsafe_allow_html=True)
  sl.markdown('<div>Com a interface intuitiva do site PennyPrevent, o usuário pode usufruir dos dados que possui sobre um maquinário<div/>', unsafe_allow_html=True)
  sl.markdown('<div>para o treinamento e teste de um modelo de IA para essa situação específica, assim podendo salvar um modelo para<div/>', unsafe_allow_html=True)
  sl.markdown('<div>o monitoramento, testa-lo com tempo real, e faze-lo trabalhar com o sistema em que ele foi treinado, tornando-o<div/>', unsafe_allow_html=True)
  sl.markdown('<div>responsável por predições e avisos relevantes e ajuda respondendo dúvidas que possam surgir. Além da análise<div/>', unsafe_allow_html=True)
  sl.markdown('<div>gráfica gerada para melhor interpretação.<div/>', unsafe_allow_html=True)
  sl.markdown("<br>", unsafe_allow_html=True) #espaçamento
  sl.markdown("<br>", unsafe_allow_html=True)
  sl.markdown("<br>", unsafe_allow_html=True)


  sl.markdown('<div style="font-weight: bold; font-size: 20px"> Objetivos do Projeto: <div/>', unsafe_allow_html=True)
  sl.markdown('<div style=" background-color: #82c9ff; color: white; width: 185px; height: 3px;"> <div/>', unsafe_allow_html=True)
  sl.markdown('<div>- Monitorar diversos tipos de maquinário<div/>', unsafe_allow_html=True)
  sl.markdown('<div>- Utilizar de uma IA para ter melhores resultados<div/>', unsafe_allow_html=True)
  sl.markdown('<div>- Evitar perda de dinheiro<div/>', unsafe_allow_html=True)
  sl.markdown('<div>- Evitar perda de tempo<div/>', unsafe_allow_html=True)
  sl.markdown('<div>- Eficiência operacional<div/>', unsafe_allow_html=True)
  sl.markdown("<br>", unsafe_allow_html=True) #espaçamento
  sl.markdown("<br>", unsafe_allow_html=True)
  sl.markdown("<br>", unsafe_allow_html=True)

 


with tab3:
  with sl.container():
    col1, col2, col3, col4 = sl.columns(4)
      
    with col1:  
      sl.image(gui, width=300)
      sl.markdown("<br>", unsafe_allow_html=True)
      sl.markdown("<br>", unsafe_allow_html=True)
    with col2:
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.write("Guilherme Renovato")
        sl.markdown("[linkedin](https://www.linkedin.com/in/guilherme-renovato-94389629a/)")
        sl.markdown("<br>", unsafe_allow_html=True) #espaçamento
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
    
    with col1:  
      sl.image(bizon, width=300)
      sl.markdown("<br>", unsafe_allow_html=True)
      sl.markdown("<br>", unsafe_allow_html=True)
    with col2:
        sl.write("Gustavo BIzon Jeronymo")
        sl.markdown("[linkedin](https://www.linkedin.com/in/gustavo-bizon-engenheiro-mecatrônico)")
        sl.markdown("<br>", unsafe_allow_html=True) #espaçamento
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)


    with col3:  
      sl.image(couto, width=300)
      sl.markdown("<br>", unsafe_allow_html=True)
      sl.markdown("<br>", unsafe_allow_html=True)
    with col4:
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.write("Gustavo Couto")
        sl.markdown("[linkedin](https://www.linkedin.com/in/gustavo-couto-9341bb268/?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app)")
        sl.markdown("<br>", unsafe_allow_html=True) #espaçamento
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)


    with col3:  
      sl.image(mat, width=300)
      sl.markdown("<br>", unsafe_allow_html=True)
      sl.markdown("<br>", unsafe_allow_html=True)
    with col4:
        sl.write("Matheus Rodrigues da Silva")
        sl.markdown("[linkedin](https://www.linkedin.com/in/matheus-rodrigues-da-silva-30b568267/)")
        sl.markdown("<br>", unsafe_allow_html=True) #espaçamento
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)