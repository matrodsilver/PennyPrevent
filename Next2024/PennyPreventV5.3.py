import streamlit as sl
from io import StringIO
import pandas as pd
import openai
import requests
import numpy as np
import pywhatkit as wp
from time import sleep as delay


#caminho das fotos
gui = "E:/PennyPreventV5.1/Fotos/gui.jpg" # mudar caminho
bizon = "E:/PennyPreventV5.1/Fotos/bizon.jpg" # mudar caminho
couto = "E:/PennyPreventV5.1/Fotos/couto.jpg" # mudar caminho
mat = "E:/PennyPreventV5.1/Fotos/mat.jpg" # mudar caminho
pp = "E:/PennyPreventV5.1/Fotos/PennyPreventLogo.png" # mudar caminho

# mudando estilo da página
sl.set_page_config(layout="wide")
tab1, tab2 = sl.tabs(["Penny Prevent", "Dados"])
col1, col2  = sl.columns(2)


sl.markdown('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-4bw+/aepP/YC94hEpVNVgiZdgIC5+VKNBQNGCHeKRQN+PtmoHDEXuppvnDJzQIu9" crossorigin="anonymous">', unsafe_allow_html=True)

etapa = 0  # variável das etapas do processo (se faz necessário no streamlit)

chatbot = False  # variável que define se o chatbot está em uso ou não #! ´False´ quando chatbot não estiver em uso para não consumir creditos

with tab2:
    tab4, tab5, tab3 = sl.tabs(["Dashboard", "IA", "Teste"])
    
    def main():
        # chamando variáveis são alterada em várias funções e etapas do processo globalmente
        global etapa
        global dados

        dados = CarregarDados()

        if dados is not None:
            GraficoDados(dados)

            resposta = sl.text_input('Adicionar colunas a desconsiderar? (s | n)').lower()

            QuestionarDesconsiderarColunas(resposta, dados)

            if etapa == 1:
                ## Usuário pode desconsiderar colunas dos dados ##
                SelecionarColunas()

            if etapa == 2:
                ## Separar variáveis dos dados ##
                resultados = sl.text_input('Defina a coluna de resultados: ')

                try:
                    inputDados = dados.drop(resultados, axis=1)
                    outputDados = dados[resultados]

                    sl.markdown(f'Coluna ´{resultados}´ definida como alvo', unsafe_allow_html=True)

                    etapa = 3  # normalizar dados

                except:
                    sl.markdown('Digite uma Coluna existente na base de dados', unsafe_allow_html=True)

            if etapa == 3:
                ## Normalização dos dados ##
                maximos = []
                minimos = []

                sl.markdown('Normalizando dados...', unsafe_allow_html=True)

                for i, coluna in enumerate(inputDados):
                    #* armazenar máximos e mínimos de cada colunas *
                    maximos.append((max(inputDados[coluna])))
                    minimos.append(min(inputDados[coluna]))

                    #* escalar valores de acordo com máximos e mínimos *
                    inputDados[coluna] = [valor/(maximos[i] - minimos[i]) if maximos[i] - minimos[i] != 0 else maximos[i] for valor in inputDados[coluna]]

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

                sl.markdown('Treinando modelo...', unsafe_allow_html=True)
                
                modelo.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

                historico = modelo.fit(treino, respostas_treino, epochs=16, validation_split=0.15)  # treina modelo e salva histórico do treino

                h = historico.history

                sl.markdown('Resultados do modelo', unsafe_allow_html=True)
                
                sl.line_chart(h['accuracy'])  # exibe dados do treino

                # * teste de acurácia do modelo *
                guesses = modelo.predict(teste)

                Acuracia(guesses, respostas_teste)

                ## Testar modelo manualmente ##
                ExibirColunasAtuais(inputDados, 'Colunas a simular')

                valores_teste = sl.text_input('Testar modelo:').replace(' ', '').split(',')

                if valores_teste != ['']:
                    try:
                        valores_teste = [float(v) for v in valores_teste]  # tentar tornar valores numéricos

                        for i, coluna in enumerate(inputDados):
                            #* escalar valores de acordo com máximos e mínimos *
                            valores_teste[i] = valores_teste[i]/(maximos[i] - minimos[i]) if maximos[i] - minimos[i] != 0 else maximos[i]

                        guess = np.array(valores_teste)

                        guess_reshape = np.expand_dims(guess, axis=0)  # Add a batch dimension

                        estado_predito = modelo.predict(guess_reshape)

                        classe_predita = np.argmax(estado_predito[0])  # Assuming categorical output

                        predito_teste = list(outputStr2Int.keys())[classe_predita]

                        sl.markdown(f"Predição do teste manual: '{predito_teste}'", unsafe_allow_html=True)

                        # * Salvar modelo *
                        modelo.save('modelo.h5')

                    except:
                        sl.markdown('digite valores coerentes de teste para cada coluna, separados por ´,´', unsafe_allow_html=True)

                    if chatbot:
                        respostaChatbot = EnviarConversa(dados, valores_teste, predito_teste)

                        sl.markdown(f'{respostaChatbot}', unsafe_allow_html=True)

                while True:
                    Avisar(inputDados, maximos, minimos, outputStr2Int, modelo)

                    delay(16)


    # ** Exibir dados em gráficos **
    def GraficoDados(dadosExibir):
        sl.markdown('Colunas', unsafe_allow_html=True)
        for dado in dadosExibir.columns:
            sl.markdown(f'{dado}', unsafe_allow_html=True)

            #! se dados são numéricos, exibe todos dentro de um limite gráfico
            #! do contrário, o gráfico não tem limite, e pode ficar muito grande, nesse caso só exibe os 10 primeiros valores
            try:
                dadosGraf = [float(valor) for valor in dadosExibir[dado]]
                sl.line_chart(dadosGraf)
            except:
                sl.markdown('10 primeiros valores', unsafe_allow_html=True)
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
            sl.markdown("Rodando arquivo de exemplo (default)")
            return pd.read_csv(r"E:\PennyPreventV5.1\PennyPrevent.csv")


    # ** Define as colunas a serem desconsideradas por input do usuário **
    def QuestionarDesconsiderarColunas(res, dadosRecebidos):
        global etapa

        #! base de dados precisa pelo menos de uma coluna de input e uma de resultado
        #! (por isso se é menor que 3 ele encerra o processo)
        if (len(dadosRecebidos.columns) < 3 or res not in ['sim', 's']) and res != '':
            etapa = 2  # escolher coluna alvo

        elif len(dadosRecebidos.columns) > 3 and res in ['sim', 's'] and res != '':
            etapa = 1  # escolher colunas a desconsiderar


    # ** Exibe colunas atuais **
    def ExibirColunasAtuais(dadosAtuais, texto):
        cols = ''
        
        sl.markdown(f'_ {texto} _', unsafe_allow_html=True)
        
        for coluna in dadosAtuais:
            cols += f'| {coluna} |'

        sl.markdown(cols, unsafe_allow_html=True)


    # ** Redefine e exibe os dados após a desconsideração das colunas escolhidas **
    def SelecionarColunas():
        global dados
        global etapa

        colunasDel = sl.text_input('Especifique as colunas a serem desconsideradas (separadas por ´,´):').replace(' ', '').split(',')  # tira espaços e separa inputs

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

                sl.markdown('_ Colunas desconsideradas: _', unsafe_allow_html=True)
                for c in desconsideradas:
                    colsDes += f'| {c} |'

                sl.markdown(colsDes, unsafe_allow_html=True)

                etapa = 2

            if len(naoEncontradas) > 0:
                colsNao = ''

                sl.markdown('_ Colunas não encontradas: _', unsafe_allow_html=True)
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
                    <h4 style="color: #00FFFF">{100 - erros/len(predicoes)*100}%</h4>''', unsafe_allow_html=True)
        

    # ** Retorna respostas do chatbot **
    def EnviarConversa(info, teste, predito):
        dados_debug = ''
        maxVars = 10
        lista_mensagens = []

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
        texto += f'valores de teste: {teste}\n'
        texto += f'Predição do teste: {predito}'

        lista_mensagens.append(
            {"role": "user", "content": texto}
        )
        
        openai.api_key = "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"

        resposta = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=lista_mensagens,
        )
        
        sl.markdown('Análise do chatbot:', unsafe_allow_html=True)
        
        return resposta.choices[0].message.content


    # ** Retorna o valor mais atual do banco de dados em formato JSON **
    def PegarUltimosDados():
        ultimosDados = f'https://predito-85975-default-rtdb.firebaseio.com/Dados/.json'
        
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

        sl.markdown(f'Ultimos dados: {dados_isolados}', unsafe_allow_html=True)

        for i, coluna in enumerate(inp):
            dados_isolados[i] = dados_isolados[i] / \
                (max[i] - min[i])

        dados_isolados = np.array(dados_isolados)

        dado_reshape = np.expand_dims(dados_isolados, axis=0)  # Add a batch dimension

        predito = ia.predict(dado_reshape)

        dados_classe_predita = np.argmax(predito[0])  # Assuming categorical output #

        predicao_atual = list(out2tr.keys())[
            dados_classe_predita]

        sl.markdown(f"Predição em tempo real: '{predicao_atual}'", unsafe_allow_html=True)
        
        #? escrever predição para firebase


        if predicao_atual in ['Disfuncional', 'Problema encontrado']:
            wp_usuarios = ['+5511996568160']

            titulo, mensagem = '⚠️Aviso⚠️', f'Foi previsto que o sistema 【𝟭】 está {
                predicao_atual}'
                
            for usuario in wp_usuarios:
                # wp.sendwhatmsg_instantly(usuario, titulo+'\n'+mensagem, 15)  #! descomentar caso queira enviar mensagem pelo whatsapp
                pass


    if __name__ == '__main__':
        main()


#Personalização da Home
with tab1:
  
  tab6, tab7 = sl.tabs(["Sobre", "Equipe"])

with tab6:
    
    col1, col2, col3 = sl.columns(3)

    with col2: 
        sl.image(pp, width=300)
        sl.image(pp2, width=300)
    sl.markdown('</div>', unsafe_allow_html=True)
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



#Personalização da aba equipe
with tab7:
  
  with sl.container():
    col1, col2, col3, col4 = sl.columns(4)
      
    with col1:  
      sl.image(gui, width=300)
      sl.markdown("<br>", unsafe_allow_html=True)
      sl.markdown("<br>", unsafe_allow_html=True)
    with col2:
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.write("Guilherme Renovato")
        sl.markdown("<div>Programador e criação da estrutura </div>", unsafe_allow_html=True)
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
    
    with col1:  
      sl.image(bizon, width=300)
      sl.markdown("<br>", unsafe_allow_html=True)
      sl.markdown("<br>", unsafe_allow_html=True)
    with col2:
        sl.write("Gustavo BIzon Jeronymo")
        sl.markdown("<div>Programador, criação do site e da estrutura </div>", unsafe_allow_html=True)
        sl.markdown("[linkedin](https://www.linkedin.com/in/gustavo-bizon-engenheiro-mecatrônico)")
        sl.markdown("<br>", unsafe_allow_html=True) #espaçamento
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
        sl.markdown("<div>Programador e criação da estrutura </div>", unsafe_allow_html=True)
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


    with col3:  
      sl.image(mat, width=300)
      sl.markdown("<br>", unsafe_allow_html=True)
      sl.markdown("<br>", unsafe_allow_html=True)
    with col4:
        sl.write("Matheus Rodrigues da Silva")
        sl.markdown("<div>Programador, criação do site e da estrutura </div>", unsafe_allow_html=True)
        sl.markdown("[linkedin](https://www.linkedin.com/in/matheus-rodrigues-da-silva-30b568267/)")
        sl.markdown("<br>", unsafe_allow_html=True) #espaçamento
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)
        sl.markdown("<br>", unsafe_allow_html=True)