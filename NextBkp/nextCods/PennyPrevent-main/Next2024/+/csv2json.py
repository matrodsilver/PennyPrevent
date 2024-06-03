import pandas as pd
import os

dados = os.path.join('Next2024', 'poseidonTratado.csv')

csv_data = pd.read_csv(dados)

json_data = csv_data.to_json(orient = 'records')

with open('2json.json', 'w') as json_file:
    json_file.write(json_data)

#! outro
# # enter the json filename to be converted to json
# JSON_FILE = 'json_filename.json'
# # enter the csv filename you wish to save it as
# CSV_FILE = 'csv_filename.csv'

# with open(JSON_FILE, encoding = 'utf-8') as f :
# 	df = pd.read_json(f)