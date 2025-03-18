#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Serviço web para prevenir suspensão do projeto no Replit
Fornece endpoints simples para manter o bot online
"""

import os
import time
import threading
import datetime
import logging
import socket
import psutil

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ping_service')

try:
    from flask import Flask, jsonify, render_template_string
except ImportError:
    logger.error("Flask não está instalado. Instale usando: pip install flask")
    raise

# Registra a hora de início do serviço
start_time = time.time()

# Cria a aplicação Flask
app = Flask(__name__)

def format_uptime(seconds):
    """Formata o tempo de atividade em formato legível"""
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    
    if days > 0:
        return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif hours > 0:
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif minutes > 0:
        return f"{int(minutes)}m {int(seconds)}s"
    else:
        return f"{int(seconds)}s"

@app.route('/')
def home():
    """Página inicial"""
    uptime = time.time() - start_time
    formatted_uptime = format_uptime(uptime)
    
    # Obter uso de memória e CPU
    process = psutil.Process(os.getpid())
    memory_usage = process.memory_info().rss / 1024 / 1024  # em MB
    cpu_percent = process.cpu_percent(interval=0.1)
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>We Profit - Bot Discord</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 20px; 
                text-align: center;
                background-color: #f5f5f5;
                color: #333;
            }
            .container {
                max-width: 800px;
                margin: 20px auto;
                padding: 20px;
                background: white;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #3498db; margin-bottom: 30px; }
            h2 { color: #555; font-size: 1.5em; }
            .status { margin: 20px 0; }
            .online { color: #2ecc71; font-weight: bold; }
            .metric {
                background: #f9f9f9;
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
                box-shadow: inset 0 0 5px rgba(0,0,0,0.05);
            }
            .value {
                font-size: 1.2em;
                font-weight: bold;
                color: #3498db;
            }
            .footer {
                margin-top: 30px;
                font-size: 0.9em;
                color: #7f8c8d;
            }
            .links {
                margin-top: 20px;
            }
            .links a {
                display: inline-block;
                margin: 0 10px;
                color: #3498db;
                text-decoration: none;
            }
            .links a:hover {
                text-decoration: underline;
            }
            @media (max-width: 600px) {
                .container {
                    padding: 15px;
                }
                h1 {
                    font-size: 1.5em;
                }
            }
        </style>
        <script>
            // Atualiza o tempo de atividade a cada segundo
            window.onload = function() {
                setInterval(function() {
                    fetch('/ping')
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('uptime').innerText = data.uptime;
                        });
                }, 1000);
            };
        </script>
    </head>
    <body>
        <div class="container">
            <h1>We Profit Discord Bot</h1>
            
            <div class="status">
                <h2>Status: <span class="online">Online</span></h2>
            </div>
            
            <div class="metric">
                <div>Tempo de Atividade</div>
                <div class="value" id="uptime">{{ uptime }}</div>
            </div>
            
            <div class="metric">
                <div>Uso de Memória</div>
                <div class="value">{{ memory_usage }} MB</div>
            </div>
            
            <div class="metric">
                <div>Uso de CPU</div>
                <div class="value">{{ cpu_percent }}%</div>
            </div>
            
            <div class="links">
                <a href="/ping">Ping API</a>
                <a href="/status">Status API</a>
            </div>
            
            <div class="footer">
                <p>Esta página serve para manter o bot ativo no Replit 24/7.</p>
                <p>Desenvolvido por Resetsui para We Profit - 2025</p>
            </div>
        </div>
    </body>
    </html>
    """, uptime=formatted_uptime, memory_usage=round(memory_usage, 2), cpu_percent=round(cpu_percent, 2))

@app.route('/ping')
def ping():
    """Endpoint para serviço de ping - mantém o bot online"""
    uptime = time.time() - start_time
    formatted_uptime = format_uptime(uptime)
    
    return jsonify({
        "status": "online",
        "timestamp": datetime.datetime.now().isoformat(),
        "uptime": formatted_uptime
    })

@app.route('/status')
def status():
    """Endpoint para verificar o status do bot"""
    uptime = time.time() - start_time
    
    # Obter informações de sistema
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    # Obter endereço IP
    hostname = socket.gethostname()
    try:
        ip_address = socket.gethostbyname(hostname)
    except:
        ip_address = "Desconhecido"
    
    return jsonify({
        "status": "online",
        "uptime_seconds": int(uptime),
        "uptime_formatted": format_uptime(uptime),
        "started_at": datetime.datetime.fromtimestamp(start_time).isoformat(),
        "current_time": datetime.datetime.now().isoformat(),
        "hostname": hostname,
        "ip_address": ip_address,
        "memory_usage_mb": round(memory_info.rss / 1024 / 1024, 2),
        "cpu_percent": round(process.cpu_percent(interval=0.1), 2)
    })

def start_ping_service():
    """Inicia o serviço web para anti-suspensão"""
    logger.info("Iniciando serviço de ping...")
    
    port = int(os.environ.get('PORT', 5000))
    
    # Inicia o servidor em uma thread separada
    def run_server():
        app.run(host='0.0.0.0', port=port)
    
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    logger.info(f"Serviço de ping iniciado na porta {port}")
    
    return server_thread

if __name__ == "__main__":
    # Se executado diretamente, inicia o servidor
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)