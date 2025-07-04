from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  # Adicionando CORS para permitir requisições do frontend
import docx
import pandas as pd
import google.generativeai as genai
import os

app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem

API_KEY = 'AIzaSyANoDPbuHvG0uyw0uwvzUALAdjxd77hBhs'
directory = r'C:\Users\marco\OneDrive\Desktop\GPT v2\documents'  # Caminho absoluto
genai.configure(api_key=API_KEY)

def show_documents():
    documents = os.listdir(directory)
    documents = [f for f in documents if os.path.isfile(os.path.join(directory, f))]
    print("Documentos encontrados:", documents)
    return documents

def read_local_file(file_path):
    if file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        content = [paragraph.text for paragraph in doc.paragraphs]
        return '\n'.join(content)
    
    elif file_path.endswith(".xlsx"):
        try:
            df = pd.read_excel(file_path, sheet_name=None)  # Lê todas as planilhas
            content = []
            for sheet_name, data in df.items():
                content.append(f"Planilha: {sheet_name}")
                content.append(data.to_string(index=False))  # Converte para string sem índice
            return '\n'.join(content)
        except Exception as e:
            return f"Erro ao ler {file_path}: {str(e)}"
    
    return ""

def pre_process_documents():
    documents_list = []
    documents = show_documents()
    for document_filename in documents:
        document_path = os.path.join(directory, document_filename)
        document = read_local_file(document_path)
        documents_list.append(document)
    return documents_list

# Carregar todos os documentos na inicialização para reutilizá-los
processed_documents = pre_process_documents()

def gerar_resposta(pergunta, model, chat):
    contexto = ("Você é um analista de dados de uma empresa de formatura (Você precisa falar igual craque Neto, apresentador do Os Donos da Bola da BAND. Use a linguagem que ele usa, até as falas ofensivas, por exemplo: ele chama as pessoas de Oreiudo) e trabalha diariamente com consultas em SQL do postgre. Precisa fazer correlações entre tabelas para gerar relatórios e bases de dados personalizadas para alimentar dashboards. Você sempre tentará construir as consultas de maneira mais otimizada possível e busca fazer analises com os resultados obtidos, gerando analises estratégicas para a diretoria com previsões e projeções")

    prompt = f"{contexto}\n\nBaseado nos documentos, responda à seguinte pergunta:\n{pergunta}\n\nResposta:"
    
    response = chat.send_message(prompt, stream=False)
    
    return response.text  # Retornar o texto da resposta

def initialize_model_and_chat():
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    chat = model.start_chat(history=[])
    return model, chat

def feed_model():
    global model, chat

    prompt = ''
    for i, document in enumerate(processed_documents, start=1):
        prompt += f"\nDocumento {i}: {document}\n\n"

    response = chat.send_message(prompt, stream=False)

model, chat = initialize_model_and_chat()
feed_model() # alimenta o modelo com os documentos inicialmente

@app.route('/ask', methods=['POST'])
def ask():
    global model, chat
    pergunta = request.json.get('pergunta')
    resposta = gerar_resposta(pergunta, model, chat)
    return jsonify({'resposta': resposta})

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
