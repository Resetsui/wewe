#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Arquivo de compatibilidade para o Replit
Este arquivo existe apenas para suportar a execução web
"""

from flask import Flask, jsonify, render_template_string
import os

# Importa o servidor ping existente, se possível
try:
    from ping_service import app
except ImportError:
    # Se não conseguir importar, cria um servidor simples
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        """Rota alternativa para a página principal"""
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>We Profit - Bot Discord</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 20px; 
                    text-align: center;
                    background-color: #f5f5f5;
                }
                .container {
                    max-width: 800px;
                    margin: 20px auto;
                    padding: 20px;
                    background: white;
                    border-radius: 5px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 { color: #3498db; }
                .status { margin: 20px 0; }
                .online { color: #2ecc71; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>We Profit Discord Bot</h1>
                <div class="status">
                    <h2>Status: <span class="online">Online</span></h2>
                </div>
                <p>O servidor web está funcionando corretamente.</p>
                <p>Para iniciar o bot Discord completo, execute <code>python main.py</code></p>
                <hr>
                <p><small>Desenvolvido por Resetsui para We Profit - 2025</small></p>
            </div>
        </body>
        </html>
        """)
    
    @app.route('/ping')
    def ping():
        """Endpoint para serviço de ping - mantém o bot online"""
        return jsonify({
            "status": "online",
            "message": "Pong!"
        })
    
    @app.route('/status')
    def status():
        """Endpoint para verificar o status do bot"""
        return jsonify({
            "status": "online",
            "message": "Servidor web funcionando corretamente"
        })

# Executar servidor diretamente se este arquivo for executado
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)