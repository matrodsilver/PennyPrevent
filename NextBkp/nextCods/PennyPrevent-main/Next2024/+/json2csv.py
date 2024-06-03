# não funcionando

import pandas as pd
import os


dados = os.path.join('./', 'csv2json.json')

json_data = pd.read_json(dados)
csv_data = json_data.to_csv()

with open('2csv.csv', encoding = 'utf-8') as csv_file :
    df = pd.read_json(csv_file)
 
    csv_file.write(json_data)
 
 
csv_data = pd.read_csv(dados)