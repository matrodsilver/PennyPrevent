import streamlit as sl
from io import StringIO
import pandas as pd
import openai
import requests
import numpy as np
import pywhatkit as wp
from time import sleep as delay


etapa = 0  # variável das etapas do processo (se faz necessário no streamlit)

chatbot = False  # variável que define se o chatbot está em uso ou não #! ´False´ quando chatbot não estiver em uso para não consumir creditos


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
                    # **Pegar dados do output para chatbot**
                    dados_debug = ''
                    for coluna in dados:
                        vars = []

                        for var in dados[coluna]:
                            if var not in vars:
                                vars.append(var)

                        dados_debug += f'{coluna}: {len(vars)} variáveis\n'

                        if len(vars) < 11:
                            dados_debug += f'{vars}'

                    openai.api_key = "<key>"

                    lista_mensagens = []
                    texto = f'Analise esses dados:\n{dados_debug}\n'
                    texto += f'valores de teste: {valores_teste}\n'
                    texto += f'Predição do teste: {list(outputStr2Int.keys())[classe_predita]}'

                    sl.markdown('Análise do chatbot:', unsafe_allow_html=True)

                    respostaChatbot = EnviarConversa(texto, lista_mensagens)

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
        return pd.read_csv(r".\Next2024\PennyPrevent.csv")


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
def EnviarConversa(mensagem, lista_msgs=[]):
    lista_msgs.append(
        {"role": "user", "content": mensagem}
    )

    resposta = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=lista_msgs,
    )
    return resposta.choices[0].message.content


# ** Retorna o valor mais atual do banco de dados em formato JSON **
def PegarUltimosDados():
    ultimosDados = f'<url>'
    
    coletado = requests.get(ultimosDados).json()

    #! salvar dados coletados em arquivo de registro
    with open('registro.txt', 'a') as registro:
        registro.write(str(pd.DataFrame(coletado).tail(1)) + '\n')

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
    
    #! salvar predição em arquivo de registro
    with open('registro.txt', 'a') as relatorio:
        relatorio.write(f'Predito: {predicao_atual}\n')

    if predicao_atual in ['Disfuncional', 'Problema encontrado']:
        wp_usuarios = ['+5511996568160']

        titulo, mensagem = '⚠️Aviso⚠️', f'Foi previsto que o sistema 【𝟭】 está {
            predicao_atual}'
            
        for usuario in wp_usuarios:
            # wp.sendwhatmsg_instantly(usuario, titulo+'\n'+mensagem, 15)  #! descomentar caso queira enviar mensagem pelo whatsapp
            pass


if __name__ == '__main__':
    main()
