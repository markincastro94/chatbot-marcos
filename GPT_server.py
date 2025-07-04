from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  # Adicionando CORS para permitir requisições do frontend
import docx
import google.generativeai as genai
import os

app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem

API_KEY = 'AIzaSyAKo9yDg76rzHpzQTnnaJZNtG-B8-rKtOE'
directory = './documents/'
genai.configure(api_key=API_KEY)

def show_documents():
    documents = os.listdir(directory)
    documents = [f for f in documents if os.path.isfile(os.path.join(directory, f))]
    print("Documentos encontrados:", documents)
    return documents

def read_local_file(file_path):
    doc = docx.Document(file_path)
    content = []
    for paragraph in doc.paragraphs:
        content.append(paragraph.text)
    return '\n'.join(content)

def pre_process_documents():
    documents_list = []
    documents = show_documents()
    for document_filename in documents:
        document = read_local_file(directory + document_filename)
        documents_list.append(document)
    return documents_list

# Carregar todos os documentos na inicialização para reutilizá-los
processed_documents = pre_process_documents()

def gerar_resposta(pergunta, model, chat):
    prompt = ''
    
    prompt += f"Baseado nos documentos, responda à seguinte pergunta:\n{pergunta}\n\nResposta:"

    response = chat.send_message(prompt, stream=False)
    
    return response

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
    return jsonify({'resposta': resposta.text})

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
