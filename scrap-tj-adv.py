import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor
import os

# Get the directory of the currently executing script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the CSV and Excel files
csv_path = os.path.join(script_dir, "gfsa_processos.csv")
excel_path = os.path.join(script_dir, "processos_results.xlsx")

## Fetch data to the url based in the num_processo
def fetch_data(num_processo):
    # Constructing URL
    url = f"https://esaj.tjsp.jus.br/cpopg/show.do?processo.codigo=01001OE1B0000&processo.foro=1&processo.numero={num_processo}"
    
    # Extracting data from website
    html = urlopen(url)
    bs = BeautifulSoup(html, 'html.parser')
    
    status_element = bs.find('span', {'class':'unj-tag'})
    status_processo = status_element.get_text(strip=True) if status_element else "Not Found"
    
    valor_element = bs.find('div', {'id':'valorAcaoProcesso'})
    valor_processo = valor_element.get_text(strip=True) if valor_element else "Not Found"
    
    dtmov_element = bs.find('td', {'class':'dataMovimentacao'})
    dtmov_processo = dtmov_element.get_text(strip=True) if dtmov_element else "Not Found"
    
    lastmov_element = bs.find('td', {'class':'descricaoMovimentacao'})
    lastmov_processo = lastmov_element.get_text(strip=True) if lastmov_element else "Not Found"
    
    incidente_element = bs.find('a', {'class':'incidente'})
    incidente_processo = incidente_element.get_text(strip=True) if incidente_element else "Not Found"
    
    return {
        'Numero Processo': num_processo,
        'Status': status_processo,
        'Valor': valor_processo,
        'Data Movimentacao': dtmov_processo,
        'Descricao Movimentacao': lastmov_processo,
        'Incidente': incidente_processo
    }

# Reading CSV into DataFrame
df_processos = pd.read_csv(csv_path)
num_processos = [quote(processo.strip()) for processo in df_processos["Processo"]]

# Counter for completed tasks and total tasks
completed = 0
total = len(num_processos)

# Using ThreadPoolExecutor to parallelize the task ## Usitng 10 
results = []
with ThreadPoolExecutor(max_workers=100) as executor:
    futures = executor.map(fetch_data, num_processos)
    for future in futures:
        results.append(future)
        completed += 1
        percentage = (completed / total) * 100
        print(f"Progress: {percentage:.2f}%")

df_results = pd.DataFrame(results)

# Save the results to an Excel file
df_results.to_excel(excel_path, index=False)
