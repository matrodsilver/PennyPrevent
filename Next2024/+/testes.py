import pandas as pd # **Biblioteca para tratar dados**


# **Verificar dados**
caminho_do_arquivo = r".\Next2024\poseidonTratado.csv" # mudar caminho do arquivo
dados = pd.read_csv(caminho_do_arquivo)

print(dados)

print(dados.keys())

print(dados.keys()[len(dados.keys())-1])