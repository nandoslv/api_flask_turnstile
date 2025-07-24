from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests

load_dotenv()

SITE_VERIFY_URL = os.getenv('SITE_VERIFY_URL')
SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)

# Configuração COMPLETA do CORS
CORS(app, resources={
    r"/*": {
        "origins": "*",  # Ou liste domínios específicos
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

@app.route('/', methods=['GET'])
def home():
  return jsonify("Bem Vindo!")

@app.route('/valida_token', methods=['POST'])
def validaToken():
    # Obter o token do corpo da requisição
    data = request.get_json()
    
    if not data or 'tokenTurnstile' not in data:
        return jsonify({'success': False, 'error': 'Token não fornecido'}), 400
    
    token = data['tokenTurnstile']
    
    try:
        # Verificar o token com a API da Cloudflare
        response = requests.post(
            SITE_VERIFY_URL,
            data={
                'secret': SECRET_KEY,
                'response': token,
                'remoteip': request.remote_addr  # Opcional: incluir o IP do usuário
            },
            timeout=5  # Timeout de 5 segundos
        )
        
        result = response.json()
        
        if result.get('success'):
            return jsonify({'success': True, 'message': 'Token válido'}), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Token inválido',
                'error-codes': result.get('error-codes', []),
                'messages': result.get('messages', [])
            }), 400
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': 'Erro ao conectar com o serviço de verificação',
            'details': str(e)
        }), 500

app.run(port=8800, host='localhost', debug=True)