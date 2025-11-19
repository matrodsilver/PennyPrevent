import streamlit as sl
from io import StringIO
import pandas as pd
import openai
import requests
import numpy as np
# import pywhatkit as wp #? retirar na versão online
from time import sleep as delay
import os
import base64
import plotly.graph_objects as go

# caminho das fotos
gui = r"./PennyPrevent/Fotos/gui.jpg"
bizon = r"./PennyPrevent/Fotos/bizon.jpg"
couto = r"./PennyPrevent/Fotos/couto.jpg"
mat = r"./PennyPrevent/Fotos/mat.jpg"
pp = r"./PennyPrevent/Fotos/PennyPreventLogo.png"

sl.set_page_config(layout="wide", page_title="Penny Prevent", page_icon=pp)

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image:
        encoded_string = base64.b64encode(image.read()).decode()
    page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
    background: linear-gradient(rgba(0, 11, 44, 0.8), rgba(0, 11, 44, 0.8)), 
                url('data:image/jpg;base64,{encoded_string}');
    background-size: cover;
    }}
    [data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
}}
    </style>
    """
    sl.markdown(page_bg_img, unsafe_allow_html=True)

# Chamando a função para adicionar o fundo
add_bg_from_local('./PennyPrevent/bg.jpg')

# mudando estilo da página

# criando abas e colunas
tab_penny_prevent, tab_dados = sl.tabs(["Penny Prevent", "Dados"])
col1, col2  = sl.columns(2)

sl.markdown('''<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-4bw+/aepP/YC94hEpVNVgiZdgIC5+VKNBQNGCHeKRQN+PtmoHDEXuppvnDJzQIu9" crossorigin="anonymous">''', unsafe_allow_html=True)

flag_etapa = None  # variável das etapas do processo (se faz necessário no streamlit)

# variáveis de sessão
if 'flag_analise' not in sl.session_state:
    sl.session_state['flag_analise'] = True

if 'chat_log' not in sl.session_state:
    sl.session_state['chat_log'] = []

with tab_dados:
    tab_gerar, tab_chat, tab_teste, tab_download = sl.tabs(["Gerar Modelo", "ChatBot", "Teste Manual", "Baixar Modelo"])


def main():
    # chamando variáveis são alterada em várias funções e etapas do processo globalmente
    global flag_etapa
    global dados
    
    openai.api_key = Cp(['0x73',
                        '0x6b', '0x2d', '0x70', '0x72', '0x6f', '0x6a', '0x2d', '0x77', '0x6c', '0x44', '0x63', '0x39', '0x50', '0x6f', '0x4b', '0x51', '0x66', '0x71', '0x43', '0x6a', '0x64', '0x49', '0x48', '0x4a', '0x52', '0x57', '0x49', '0x41', '0x4c', '0x61', '0x54', '0x58', '0x38', '0x38', '0x43', '0x41', '0x64', '0x49', '0x41', '0x73', '0x52', '0x35', '0x6f', '0x67', '0x53', '0x39', '0x75', '0x4b', '0x63', '0x59', '0x78', '0x61', '0x45', '0x32', '0x69', '0x64', '0x50', '0x78', '0x6e', '0x35', '0x79', '0x41', '0x53', '0x4c', '0x6c', '0x78', '0x4e', '0x56', '0x56', '0x5f', '0x7a', '0x6e', '0x4f', '0x70', '0x6e', '0x57', '0x58', '0x43', '0x35', '0x49', '0x79', '0x54', '0x33', '0x42', '0x6c', '0x62', '0x6b', '0x46', '0x4a', '0x45', '0x46', '0x68', '0x55', '0x6b', '0x32', '0x6c', '0x6e', '0x45', '0x37', '0x75', '0x56', '0x67', '0x4a', '0x68', '0x51', '0x4c', '0x35', '0x6e', '0x5a', '0x74', '0x59', '0x76', '0x35', '0x4b', '0x63', '0x4e', '0x37', '0x48', '0x47', '0x7a', '0x34', '0x69', '0x68', '0x64', '0x36', '0x6c', '0x4a', '0x75', '0x75', '0x77', '0x67', '0x72', '0x34', '0x66', '0x74', '0x66', '0x41', '0x73', '0x36', '0x72', '0x4e', '0x4e', '0x38', '0x78', '0x67', '0x50', '0x45', '0x36', '0x62', '0x46', '0x56', '0x46', '0x4a', '0x52', '0x66', '0x4b', '0x6a', '0x4e', '0x57', '0x34', '0x38', '0x4d', '0x41'])


    with tab_gerar:
        dados = CarregarDados()

        GraficoDados(dados)

        resposta = sl.text_input('Adicionar colunas a desconsiderar? (s | n)', help='exemplo padrão: s').lower()

        QuestionarDesconsiderarColunas(resposta, dados)

        if flag_etapa == 1:
            ## Usuário pode desconsiderar colunas dos dados ##
            SelecionarColunas()

        if flag_etapa == 2:
            ## Separar variáveis dos dados ##
            resultados = sl.text_input('Defina a coluna de resultados: ', help="exemplo padrão: Estado")

            try:
                inputDados = dados.drop(resultados, axis=1)
                outputDados = dados[resultados]

                sl.markdown(f'''Coluna ´{resultados}´ definida como alvo''', unsafe_allow_html=True)

                flag_etapa = 3  # normalizar dados

            except:
                sl.markdown('''Digite uma Coluna existente na base de dados''', unsafe_allow_html=True)

        if flag_etapa == 3:
            ## Normalização dos dados ##
            maximos = []
            minimos = []

            sl.markdown('''Normalizando dados...''', unsafe_allow_html=True)

            for i, coluna in enumerate(inputDados):
                #* armazenar máximos e mínimos de cada colunas *
                maximos.append((max(inputDados[coluna])))
                minimos.append(min(inputDados[coluna]))

                #* escalar valores de acordo com máximos e mínimos *
                inputDados[coluna] = [valor/(maximos[i] - minimos[i]) if maximos[i] - minimos[i] != 0 else maximos[i] for valor in inputDados[coluna]]

            if 'maximos' not in sl.session_state and 'minimos' not in sl.session_state:
                sl.session_state['maximos'] = maximos
                sl.session_state['minimos'] = minimos

            #* criar dicionário dos nomes dos resultados *
            outputStr2Int = {}  # definindo dicionário de resultados

            n = 0
            for key in outputDados:
                if key not in outputStr2Int:
                    outputStr2Int[key] = n
                    n += 1

            outputDados = outputDados.replace(outputStr2Int)  # substituir str para valores numéricos, melhores para a ia

            outputDados = pd.DataFrame(outputDados)

            #* formatar dados para o modelo *
            from sklearn.model_selection import train_test_split

            treino, teste, respostas_treino, respostas_teste = train_test_split(inputDados, outputDados, stratify=outputDados, test_size=.15, random_state=5)

            ## Criação, treino e teste do modelo ##
            neuronios = 256  # n de neurônios

            import tensorflow
            import keras

            #* configurações do modelo *
            modelo = keras.Sequential(
                [
                    keras.layers.Input(shape=(len(inputDados.columns),)),         # camada de input
                    keras.layers.Dense(neuronios, activation=tensorflow.nn.selu), # camada oculta, em que os neurônios adquirem pesos
                    keras.layers.Dropout(.15),                                    # camada de dropout, para evitar overfitting (ajustes demasiados aos dados)
                    keras.layers.Dense(3, activation=tensorflow.nn.softmax)       # camada de output
                ]
            )

            sl.markdown('''Treinando modelo...''', unsafe_allow_html=True)
            
            modelo.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

            historico = modelo.fit(treino, respostas_treino, epochs=16, validation_split=0.15)  # treina modelo e salva histórico do treino

            h = historico.history

            sl.markdown('''Resultados do modelo''', unsafe_allow_html=True)
            
            sl.line_chart(h['accuracy'])  # exibe dados do treino

            # * teste de acurácia do modelo *
            guesses = modelo.predict(teste)

            Acuracia(guesses, respostas_teste)

            # * Salvar modelo *
            modelo.save('modeloIA.h5')

            with tab_download:
                if 'modeloIA.h5' in os.listdir('.'):
                    if sl.download_button(
                    label='Baixar o modelo gerado',
                    data='modelo.h5',
                    file_name='modeloDeIA.h5',
                    mime='text/pdf',):
                        sl.text('Download executado com sucesso!')

            ## Testar modelo manualmente ##
            with tab_teste:
                ExibirColunasAtuais(inputDados, 'Colunas a simular')

                valores_teste = sl.text_input('Testar modelo:', help='exemplo padrão: 3, 1, 20, 0  →retorna→ funcional').replace(' ', '').split(',')

                if valores_teste != ['']:
                    predito_teste = None

                    try:
                        valores_teste = [float(v) for v in valores_teste]  # tentar tornar valores numéricos

                        for i, coluna in enumerate(inputDados):
                            #* escalar valores de acordo com máximos e mínimos *
                            valores_teste[i] = valores_teste[i]/(sl.session_state['maximos'][i] - sl.session_state['minimos'][i]) if sl.session_state['maximos'][i] - sl.session_state['minimos'][i] != 0 else sl.session_state['maximos'][i]

                        guess = np.array(valores_teste)

                        guess_reshape = np.expand_dims(guess, axis=0)  # Add a batch dimension

                        estado_predito = modelo.predict(guess_reshape)

                        classe_predita = np.argmax(estado_predito[0])  # Assuming categorical output

                        predito_teste = list(outputStr2Int.keys())[classe_predita]

                        sl.markdown(f"""Predição do teste manual: '{predito_teste}'""", unsafe_allow_html=True)

                    except:
                        sl.markdown('''digite valores coerentes de teste para cada coluna, separados por ´,´''', unsafe_allow_html=True)
                        
                    with tab_chat:
                        respostaChatbot = EnviarAnalise(dados, valores_teste, predito_teste)

                        print(respostaChatbot) #? debug
                        sl.markdown(f'''{respostaChatbot}''', unsafe_allow_html=True)

                        input_usuario = sl.text_input('conversar com o assistente', max_chars=500)

                        if input_usuario != '':
                            ## CHATBOT.LOG ##
                            sl.session_state['chat_log'].append({"role": "user", "content": input_usuario})

                            resposta = openai.chat.completions.create(
                                model="gpt-3.5-turbo",
                                messages=sl.session_state['chat_log'],
                            ).choices[0].message.content

                            sl.session_state['chat_log'].append({"role": "assistant", "content": resposta})

                            sl.markdown(f'''{resposta}''', unsafe_allow_html=True)

                        print(input_usuario) #? debug

            sl.markdown(f"""Predição em tempo real:""")
            while True:
                Avisar(inputDados, sl.session_state['maximos'], sl.session_state['minimos'], outputStr2Int, modelo)

                delay(120)


# ** Exibir dados em gráficos **
import plotly.graph_objects as go

def GraficoDados(dadosExibir):
    sl.markdown('''Colunas''', unsafe_allow_html=True)
    for dado in dadosExibir.columns:
        sl.markdown(f'''<h3 style="color: #41b5e6">{dado}</h3>''', unsafe_allow_html=True)

        # Verifica se a coluna contém dados numéricos
        if dadosExibir[dado].dtype in ['int64', 'float64']:
            # Seleciona os últimos 40 valores dos dados
            dadosReduzidos = dadosExibir[dado].tail(500)

            # Configura o gráfico usando Plotly com mais personalizações
            fig = go.Figure()

            # Adiciona os dados como uma linha com marcadores nos pontos
            fig.add_trace(go.Scatter(
                x=dadosReduzidos.index,
                y=dadosReduzidos,
                mode='lines+markers',  # Mostra a linha e os pontos
                line=dict(color='#41b5e6', width=2),  # Cor e espessura da linha
                marker=dict(size=6, color='#FF7F0E')  # Tamanho e cor dos pontos
            ))

            # Personaliza o layout do gráfico
            fig.update_layout(
                xaxis_title='Id',  # Rótulo do eixo X
                yaxis_title=dado,  # Rótulo do eixo Y (nome da coluna)
                plot_bgcolor='#000000',  # Cor de fundo do gráfico
                hovermode="x",  # Exibe o valor ao passar o mouse
            )

            # Exibe o gráfico
            sl.plotly_chart(fig)
        else:
            # Para dados não numéricos, exibe os 10 primeiros valores
            sl.markdown('''10 primeiros valores''', unsafe_allow_html=True)
            sl.line_chart(dadosExibir[dado].head(10))


# ** Retorna dados CSV e JSON em formato pandas dataframe **
def CarregarDados():
    uploaded_file = sl.file_uploader("Escolher arquivo", type=['csv', 'json'])

    if uploaded_file is not None:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))  # To convert to a string based IO:

        # turn csv or json file into pandas dataframe
        if uploaded_file.name.split('.')[-1] == 'json':   #! json
            return pd.read_json(stringio)

        elif uploaded_file.name.split('.')[-1] == 'csv':  #! csv
            return pd.read_csv(stringio)

    else:
        sl.markdown("""Rodando arquivo de exemplo (default)""")
        return pd.read_csv(r"./PennyPrevent/PennyPrevent.csv")


# ** Define as colunas a serem desconsideradas por input do usuário **
def QuestionarDesconsiderarColunas(res, dadosRecebidos):
    global flag_etapa

    #! base de dados precisa pelo menos de uma coluna de input e uma de resultado
    #! (por isso se é menor que 3 ele encerra o processo)
    if (len(dadosRecebidos.columns) < 3 or res not in ['sim', 's']) and res != '':
        flag_etapa = 2  # escolher coluna alvo

    elif len(dadosRecebidos.columns) > 3 and res in ['sim', 's'] and res != '':
        flag_etapa = 1  # escolher colunas a desconsiderar


# ** Exibe colunas atuais **
def ExibirColunasAtuais(dadosAtuais, texto):
    cols = ''
    
    sl.markdown(f'''<div style="font-weight: bold">{texto} </div>''', unsafe_allow_html=True)
    
    for coluna in dadosAtuais:
        cols += f'| {coluna} |'

    sl.markdown(f'''<div style="color: #77DD77"> {cols} </div>''', unsafe_allow_html=True)


# ** Redefine e exibe os dados após a desconsideração das colunas escolhidas **
def SelecionarColunas():
    global dados
    global flag_etapa

    colunasDel = sl.text_input('Especifique as colunas a serem desconsideradas (separadas por ´,´):', help='exemplo padrão: id').replace(' ', '').split(',')  # tira espaços e separa inputs

    desconsideradas = []
    naoEncontradas = []

    if colunasDel != '' and type(dados) == pd.DataFrame:
        for coluna in colunasDel:
            if coluna in dados:
                desconsideradas.append(coluna)
                dados = dados.drop(coluna, axis=1)

            else:
                naoEncontradas.append(coluna)

        if len(desconsideradas) > 0:
            colsDes = ''

            sl.markdown('''_ Colunas desconsideradas: _''', unsafe_allow_html=True)
            for c in desconsideradas:
                colsDes += f'| {c} |'

            sl.markdown(f'''<div style="color: #FF6961"> {colsDes} </div>''', unsafe_allow_html=True)

            flag_etapa = 2

        if len(naoEncontradas) > 0:
            colsNao = ''

            sl.markdown('''_ Colunas não encontradas: _''', unsafe_allow_html=True)
            for c in naoEncontradas:
                colsNao += f'| {c} |'

            sl.markdown(colsNao, unsafe_allow_html=True)

        ExibirColunasAtuais(dados, 'Colunas Atuais')


# ** Checar acurácia do modelo **
def Acuracia(predicoes, resp_teste):
    erros = 0
    
    for i, valor in enumerate(predicoes):
        estado_predito = np.argmax(valor)
        estado_real = resp_teste['Estado'].iloc[i]  # get value's index
        if estado_predito != estado_real:
            erros += 1

    sl.markdown(f'''<h3>Acertos do modelo:</h3>
                <h4 style="color: #77DD77">{format(100 - erros / len(predicoes) * 100, ".2f")}%</h4>''', unsafe_allow_html=True)

    

# ** Retorna respostas do chatbot **
def EnviarAnalise(info, teste, predito):
    if sl.session_state['flag_analise']:
        dados_debug = ''
        maxVars = 10

        for coluna in info:
            vars = []

            for var in info[coluna]:
                if var not in vars:
                    vars.append(var)

            dados_debug += f'{coluna}: {len(vars)} variáveis\n'

            if len(vars) <= maxVars:
                dados_debug += f'{vars}'
            else:
                dados_debug += f'{vars[:maxVars]} ...'

        texto = f'Analise esses dados:\n{dados_debug}\n'
        texto += f'valores de teste normalizados: {teste}\n'
        texto += f'Predição do teste: {predito}'

        sl.session_state['chat_log'].append(
            {"role": "user", "content": texto}
        )


        resposta = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=sl.session_state['chat_log'],
        ).choices[0].message.content

        sl.markdown('''Análise do chatbot:''', unsafe_allow_html=True)
        
        sl.session_state['chat_log'].append({"role": "assistant", "content": resposta})
        
        sl.session_state['flag_analise'] = False

    return sl.session_state['chat_log'][1]['content']


# ** Retorna o valor mais atual do banco de dados em formato JSON **
def PegarUltimosDados():
    ultimosDados = '''https://console.firebase.google.com/u/0/project/gs-iot-5484a/database/gs-iot-5484a-default-rtdb/Dados/.json'''
    
    coletado = requests.get(ultimosDados).json()

    return coletado


# ** Notificar usuários em tempo real em caso de problema **
def Avisar(inp, max, min, out2tr, ia):
    prever = pd.DataFrame(PegarUltimosDados()).tail(1)  # pegar somente ultimo valor e tornar pandas dataframe

    for atributo in prever:
        prever[atributo] = [
            float(v) for v in prever[atributo]]

    dados_isolados = []

    for valor in prever:
        #! firebase manda mais informações como lista, por isso é necessário iterar
        for valor_real in prever[valor]:
            dados_isolados.append(valor_real)

    ultimos_dados = dados_isolados.copy()

    for i, coluna in enumerate(inp):
        dados_isolados[i] = dados_isolados[i] / \
            (max[i] - min[i])

    dados_isolados = np.array(dados_isolados)

    dado_reshape = np.expand_dims(dados_isolados, axis=0)  # Add a batch dimension

    predito = ia.predict(dado_reshape)

    dados_classe_predita = np.argmax(predito[0])  # Assuming categorical output #

    predicao_atual = list(out2tr.keys())[
        dados_classe_predita]

    with tab_gerar:
        sl.markdown(f'''Ultimos dados: {ultimos_dados} → {predicao_atual}''', unsafe_allow_html=True)

    if predicao_atual in ['Disfuncional', 'Problema encontrado']:
        wp_usuarios = [Cp(['0x2b',
                           '0x35', '0x35', '0x31', '0x31', '0x39', '0x39', '0x36', '0x35', '0x36', '0x38', '0x31', '0x36', '0x30'])]

        titulo, mensagem = '⚠️Aviso⚠️', f'Foi previsto que o sistema 【𝟭】 está {
            predicao_atual}'
            
        for usuario in wp_usuarios:
            # wp.sendwhatmsg_instantly(usuario, titulo+'\n'+mensagem, 15)  #! descomentar caso queira enviar mensagem pelo whatsapp
            pass


def Cp(l):
    k = ''
    for c in l:
        k += chr(int(c, 16))
    # print('cp:', k)
    return k

main()

if flag_etapa != 3:
    with tab_download:
        sl.markdown('''Execute os passos da tab "Dashboard" para poder baixar o modelo gerado''', unsafe_allow_html=True)

    with tab_teste:
        sl.markdown('''Execute os passos da tab "Dashboard" para ser possível fazer o teste manual''', unsafe_allow_html=True)

    with tab_chat:
        sl.markdown('''Execute os passos da tab "Teste manual" para poder usar o chatbot gerado''', unsafe_allow_html=True)


#Personalização da aba Penny Prevent
with tab_penny_prevent:
  
  tab_sobre, tab_equipe = sl.tabs(["Sobre", "Equipe"])

with tab_sobre:
    
    col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12, col13, col14, col15, col16, col17, col18 = sl.columns(18)

    with col9: 
        sl.image(pp, width=150)
    
    sl.markdown('''
        <br><br>
        <center>
                <div style="font-weight: bold; font-size: 50px; color: #41B5E6">Projeto em conjunto com a empresa Reply:</div>
                <div style="background-color: #41B5E6; color: white; width: 940px; height: 3px;"></div>
                <br>
                <div style="font-size:20px">Sistema de Coleta de dados para evitar prejuízo físico e monetário por manutenções e gerenciamento tardio do maquinário.</div>
        </center>
        <br><br><br>
        
        <center>
                <div style="font-weight: bold; font-size: 50px; color: #41B5E6">Funcionamento do sistema:</div>
                <div style="background-color: #41B5E6; color: white; width: 610px; height: 3px;"></div>
        </center>
                <br>
                <div style="font-size: 20px">Com a interface intuitiva do site PennyPrevent, o usuário pode usufruir dos dados que possui sobre um maquinário para o treinamento e teste de um modelo de IA para essa situação específica, assim podendo salvar um modelo para o monitoramento, testá-lo em tempo real, e fazê-lo trabalhar com o sistema em que ele foi treinado, tornando-o responsável por predições e avisos relevantes e ajudando a responder dúvidas que possam surgir. Além da análise gráfica gerada para melhor interpretação.</div>
                <br><br><br>
        
        <center>        
            <div style="font-weight: bold; font-size: 50px; color: #41B5E6">Objetivos do Projeto:</div>
            <div style="background-color:#41B5E6; color: white; width: 460px; height: 3px;"></div>
            <br>
            <li style="font-size: 20px"> Monitorar diversos tipos de maquinário </li>
            <li style="font-size: 20px"> Utilizar IA para ter melhores resultados </li>
            <li style="font-size: 20px"> Evitar perda de dinheiro </li>
            <li style="font-size: 20px"> Evitar perda de tempo </li>
            <li style="font-size: 20px"> Eficiência operacional </li>
        </center>
        <br><br><br>
    ''', unsafe_allow_html=True)




#Personalização da aba Equipe
with tab_equipe:
  
    with sl.container():
        col1, col2, col3, col4 = sl.columns(4)
        
        with col1:  
            sl.image(gui, use_column_width=True)
            sl.markdown("<br>", unsafe_allow_html=True)
        
        with col1:
            sl.markdown('''
                <div style="font-weight: bold; font-size: 20px">Guilherme Renovato</div>
                <div style="background-color: #82c9ff; color: white; width: 180px; height: 3px;"></div>
                <div>Programador e criação da estrutura</div> <br>
                <style>
                .link-button {
                    font-weight: bold;
                    font-size: 20px;
                    color: #00BBBB;
                    text-decoration: none;
                    transition: text-shadow 0.3s ease-in-out;
                }
                </style> <style>
                .link-button:hover {
                    text-shadow: 0 0 10px #00FFFF;
                }
                </style>
                <a href="https://www.linkedin.com/in/guilherme-renovato-94389629a/" class="link-button">Linkedin</a> <br>
                <a href="https://github.com/RENOVATINHO" class="link-button">Github</a> <br>
                <a href="mailto:guilhermerenovs@gmail.com" class="link-button">guilhermerenovs@gmail.com</a> <br>           
                <br><br><br><br><br><br><br>''', unsafe_allow_html=True)
                        

        with col2:  
            sl.image(bizon, use_column_width=True)
            sl.markdown('''<br>''', unsafe_allow_html=True)

        with col2:
            sl.markdown('''
                <div style="font-weight: bold; font-size: 20px">Gustavo Bizon</div>
                <div style="background-color: #82c9ff; color: white; width: 124px; height: 3px;"></div>
                <div>Programador, criação do site e da estrutura</div> <br>
                <a href="https://www.linkedin.com/in/gustavo-bizon-engenheiro-mecatrônico" class="link-button">Linkedin</a> <br>
                <a href="https://github.com/gustavobizon" class="link-button">Github</a> <br>
                <a href="mailto:gustavobizonj@gmail.com" class="link-button">gustavobizonj@gmail.com</a> <br>
                <br><br><br><br><br><br><br>''', unsafe_allow_html=True)
            

        with col3:  
            sl.image(couto, use_column_width=True)
            sl.markdown('''<br>''', unsafe_allow_html=True)

        with col3:
            sl.markdown('''
                <div style="font-weight: bold; font-size: 20px">Gustavo Couto</div>
                <div style="background-color: #82c9ff; color: white; width: 125px; height: 3px;"></div>
                <div>Programador e criação da estrutura</div> <br>
                <a href="https://www.linkedin.com/in/gustavo-couto-9341bb268/" class="link-button">Linkedin</a> <br>
                <a href="https://github.com/GustavoCouto14" class="link-button">Github</a> <br>
                <a href="mailto:gucouto14@gmail.com" class="link-button">gucouto14@gmail.com</a> <br>
                <br><br><br><br><br><br><br>''', unsafe_allow_html=True)
            

        with col4:  
            sl.image(mat, use_column_width=True)
            sl.markdown('''<br>''', unsafe_allow_html=True)

        with col4:
            sl.markdown('''
                <div style="font-weight: bold; font-size: 20px">Matheus Rodrigues</div>
                <div style="background-color: #82c9ff; color: white; width: 168px; height: 3px;"></div>
                <div>Programador, criação do site e da estrutura</div> <br>
                <a href="https://www.linkedin.com/in/matheus-rodrigues-da-silva-30b568267/" class="link-button">Linkedin</a> <br>
                <a href="https://github.com/matrodsilver" class="link-button">Github</a> <br>
                <a href="https://matrodsilver.github.io/WebPortfolioMatheusS/" class="link-button">Portifolio</a> <br>
                <a href="mailto:matrodsilva@gmail.com" class="link-button">Matrodsilva@gmail.com</a>
                <br><br><br><br><br><br><br>''', unsafe_allow_html=True)

