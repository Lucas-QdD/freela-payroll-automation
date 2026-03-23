import os
import gspread
import pandas as pd
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
from fpdf.enums import XPos, YPos
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

def get_last_week_range():
    # Calculates the start and end dates of the previous week (Mon-Sun).
    today = datetime.now()
    start_date = today - timedelta(days=today.weekday() + 7)
    end_date = start_date + timedelta(days=6)
    return start_date, end_date

def get_sheet_data(spreadsheet_name):
    # Connects to Google Sheets and returns data as a DataFrame.
    # Path logic we discussed
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")
    
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    
    creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=scopes)
    client = gspread.authorize(creds)
    
    sheet = client.open(spreadsheet_name).sheet1
    records = sheet.get_all_records()
    
    df = pd.DataFrame(records)
    # Ensure 'Data' column is in datetime format
    df['Data'] = pd.to_datetime(df['Data'], dayfirst=True) 
    return df

class ReceiptPDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 12)
        self.cell(0, 10, "RECIBO DE PAGAMENTO DE FREELAS", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def generate_weekly_report(payroll_summary, period_range):
    pdf = ReceiptPDF()
    pdf.add_page()
    
    # Título do Relatório
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, f"Resumo de Pagamentos: {period_range}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.ln(5)
    
    # Cabeçalho da Tabela
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(45, 10, "Funcionário", border=1)
    pdf.cell(95, 10, "Serviços Realizados", border=1) # Coluna maior para a descrição
    pdf.cell(45, 10, "Total", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Conteúdo
    pdf.set_font("helvetica", size=9)
    total_geral = 0
    
    for index, row in payroll_summary.iterrows():
        pdf.cell(45, 10, f" {row['Nome']}", border=1)
        pdf.cell(95, 10, f" {row['Servicos']}", border=1)
        pdf.cell(45, 10, f" R$ {row['Total_Valor']:.2f}", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        total_geral += row['Total_Valor']
    
    # Total Geral
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 10, f"Valor Total da Semana: R$ {total_geral:.2f}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")

    # Salvamento
    if not os.path.exists("output"):
        os.makedirs("output")
    
    file_name = f"output/relatorio_semanal_{period_range.replace(' ', '_')}.pdf"
    pdf.output(file_name)
    return file_name

load_dotenv()

def send_email_with_report(file_path, period_range):
    # Sends the generated PDF report via email.
    sender_email = os.getenv("SENDER_EMAIL")
    app_password = os.getenv("APP_PASSWORD")
    receiver_email = os.getenv("RECEIVER_EMAIL")

    msg = EmailMessage()
    msg['Subject'] = f"Relatório de Pagamentos Freelas - {period_range}"
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(f"Olá,\n\nSegue em anexo o relatório consolidado de pagamentos para o período de {period_range}.\n\nAtenciosamente,\nSistema de Automação")

    # Anexando o PDF
    with open(file_path, 'rb') as f:
        file_data = f.read()
        msg.add_attachment(
            file_data,
            maintype='application',
            subtype='pdf',
            filename=os.path.basename(file_path)
        )

    # Enviando
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")


def process_payroll():
    start_date, end_date = get_last_week_range()
    period_str = f"{start_date.date()} to {end_date.date()}"
    
    # Get real data
    try:
        df = get_sheet_data("Planilha_teste")
    except Exception as e:
        print(f"Error: {e}")
        return

    # Filter & Aggregate
    mask = (df['Data'] >= start_date) & (df['Data'] <= end_date)
    weekly_df = df.loc[mask]

    if weekly_df.empty:
        print("No records found.")
        return

    payroll_summary = weekly_df.groupby(['Nome', 'Email']).agg(
    Total_Valor=('Valor', 'sum'),
    Servicos=('Servico', lambda x: ", ".join([f"{s} ({list(x).count(s)}x)" for s in set(x)]))
).reset_index()

    # GENERATE PDFs
    print("\nGenerating Weekly Report...")
    file_path = generate_weekly_report(payroll_summary, period_str)
    print(f"Report saved: {file_path}")

    print("📧 Sending email...")
    send_email_with_report(file_path, period_str)

if __name__ == "__main__":
    process_payroll()

