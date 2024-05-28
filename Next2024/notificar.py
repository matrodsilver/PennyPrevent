
# ** Notificar usuários em tempo real em caso de problema **
from pushbullet import Pushbullet
import pywhatkit as wp
from time import sleep as delay
import requests
import numpy as np
'todos os imports feitos'

from tkinter import Tk, filedialog

root = Tk()
root.title('Escolha o arquivo')

filepath = filedialog.askopenfilename(initialdir='/', title='Selecione o arquivo', filetypes=(('todos os arquivos', '*.*'),))

from tensorflow.keras.models import load_model #type: ignore #? informa erro mas é funcional (?)
# modelo_salvo = load_model(r'.\Next2024\modelo (1).h5')
modelo_salvo = load_model(filepath)

# from PennyPreventV2 import inputDados, outputStr2Int, minimos, maximos


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

    predito = modelo_salvo.predict(dado_reshape)

    dados_classe_predita = np.argmax(predito[0])  # Assuming categorical output #
    
    predicao_atual = list(outputStr2Int.keys())[dados_classe_predita]

    f"Predição em tempo real: '{predicao_atual}'" # se 2 valores do dicionário são iguais, mostra o primeiro


    # if volume < 30: # 30000:
    if predicao_atual in ['disfuncional', 'problema encontrado', 'funcional']:
      pb_usuarios = ['o.9CYuBlpove3ErChfkLDjcmkNcjquJ1oz']
      wp_usuarios = ['+5511996568160']
      
      # titulo, mensagem = '⚠️Aviso⚠️', f'⚠ O sistema【𝟭】atingiu o limite de volume ⚠\nAtualmente em: {57- volume} cm'
      titulo, mensagem = '⚠️Aviso⚠️', f'Foi previsto que o sistema 【𝟭】 está {predicao_atual}'

      for usuario in pb_usuarios:
        pbt = Pushbullet(usuario)
        pbt.push_note(titulo, mensagem)
      
      for usuario in wp_usuarios:
        wp.sendwhatmsg_instantly(usuario, titulo+'\n'+mensagem, 15) #True, 15) #type: ignore


while True:
  avisar()

  delay(16)