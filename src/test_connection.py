import os
import gspread
from google.oauth2.service_account import Credentials

# Descobrindo o caminho para credentials
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")

# Definir o escopo (o que o robô pode fazer)
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Carregar as credenciais

creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=scopes)
client = gspread.authorize(creds)

# Abrir a planilha
try:
    sheet = client.open("Planilha_teste").sheet1
    data = sheet.get_all_records()
    print("✅ Conexão estabelecida com sucesso!")
    print(f"Encontradas {len(data)} linhas na planilha.")
    if data:
        print("Primeira linha encontrada:", data[0])
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")