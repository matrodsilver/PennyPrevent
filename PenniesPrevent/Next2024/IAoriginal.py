'''
link para o colab:
https://colab.research.google.com/drive/1HWflE9BZzIpapgP2--twCMPz0A_geABv#scrollTo=q8z6Kkb36TNA&uniqifier=1
'''

import tensorflow
from tensorflow import keras

## biblioteca para tratar dados

import pandas as pd
import sklearn as skl

dados = pd.read_csv("/content/drive/MyDrive/Arqvs/Cód./Python/Colab/Alura/IA/Deep Learning parte 1: Keras/poseidonTratado.csv")

dados.head(2)

## reduzir variáveis dos dados

dados = dados.drop(['Unnamed: 0', 'created_at'], axis = 1)

dados.head(2)

## verificação de variáveis

dados.info()

for coluna in dados:
  vars = []

  for var in dados[coluna]:
    if var not in vars:
      vars.append(var)

  print(f'{coluna}: {len(vars)} variáveis')

  print(f'{vars}\n')

## tratar variáveis dos dados

input = dados.drop('Estado', axis = 1)
output = dados['Estado']

## normalização
for coluna in input:
  print(f'{coluna}: {min(input[coluna])} ~ {max(input[coluna])}')
print('\n')

for coluna in input:
  input[coluna] = [valor/(max(input[coluna]) - min(input[coluna])) for valor in input[coluna]]

for coluna in input:
  print(f'{coluna}: {min(input[coluna])} ~ {max(input[coluna])}')

outputStr2Int = {'funcional': 0,
              'problema encontrado': 1,
              'disfuncional': 2}

output = output.replace(outputStr2Int)

input.head(2)

output = pd.DataFrame(output)

output

from sklearn.model_selection import train_test_split

treino, teste, respostas_treino, respostas_teste = train_test_split(input, output, stratify = output, test_size = .2, random_state = 5)

## criação, compilação e treino do modelo

camadas = 256 # n de neurônios

modelo = keras.Sequential(
    [
        keras.layers.Input(shape=(4,)),
        keras.layers.Dense(camadas, activation = tensorflow.nn.selu),
        keras.layers.Dropout(.2),
        keras.layers.Dense(3, activation = tensorflow.nn.softmax)
    ]
)

modelo.compile(optimizer = 'adam', loss = 'sparse_categorical_crossentropy', metrics = ['accuracy'])

historico = modelo.fit(treino, respostas_treino, epochs = 7, validation_split = 0.2) # , batch_size = 96)

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

from numpy import argmax

guesses = modelo.predict(teste)

erros = 0
for i, valor in enumerate(guesses):
  estado_predito = argmax(valor)
  estado_real = respostas_teste['Estado'].iloc[i]
  if estado_predito != estado_real:
    erros += 1

print('acertos =', 100 - erros/100,'%')