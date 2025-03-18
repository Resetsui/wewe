#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema Anti-Suspensão para o bot Discord
Este módulo implementa estratégias avançadas para evitar que o Replit suspenda o projeto

Desenvolvido por Resetsui para a Guild We Profit - 2025
Otimizado para eficiência e menor consumo de recursos
"""

import os
import time
import random
import logging
import threading
import requests
import psutil
from datetime import datetime

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('anti_suspend')

# Intervalo de verificação (em segundos)
CHECK_INTERVAL = 300  # 5 minutos

# URLs para fazer ping e manter o sistema ativo
PING_TARGETS = [
    "https://www.google.com",
    "https://discord.com",
    "https://replit.com"
]

def make_external_requests():
    """Faz requisições a serviços externos para manter a conectividade"""
    # Seleciona um alvo aleatório para o ping
    target = random.choice(PING_TARGETS)
    
    try:
        # Faz a requisição
        start_time = time.time()
        response = requests.get(target, timeout=10)
        elapsed_time = time.time() - start_time
        
        # Verifica se o ping foi bem-sucedido
        if response.status_code == 200:
            logger.debug(f"Ping bem-sucedido para {target} ({elapsed_time:.2f}s)")
            return True
        else:
            logger.warning(f"Ping para {target} retornou código {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Erro ao fazer ping para {target}: {str(e)}")
        return False

def get_process_uptime():
    """Retorna o tempo de atividade do processo atual"""
    # Obtém informações sobre o processo atual
    process = psutil.Process(os.getpid())
    
    # Calcula o tempo de atividade em segundos
    uptime_seconds = time.time() - process.create_time()
    
    # Formata o tempo de atividade
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"{int(days)}d {int(hours)}h {int(minutes)}m"
    elif hours > 0:
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif minutes > 0:
        return f"{int(minutes)}m {int(seconds)}s"
    else:
        return f"{int(seconds)}s"

def monitor_uptime():
    """Monitora o tempo de atividade e previne suspensão"""
    logger.info("Sistema anti-suspensão iniciado")
    
    while True:
        try:
            # Registra informações de atividade
            uptime = get_process_uptime()
            logger.info(f"Anti-Suspensão: Ativo ({uptime})")
            
            # Faz requisições externas para manter o sistema ativo
            success = make_external_requests()
            
            # Se a requisição falhar, tenta novamente em breve
            if not success:
                time.sleep(60)  # Tenta novamente em 1 minuto
                continue
            
            # Aguarda até a próxima verificação
            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            logger.error(f"Erro no sistema anti-suspensão: {str(e)}")
            # Aguarda um período antes de tentar novamente
            time.sleep(60)
            continue

def start_anti_suspend_monitor():
    """Inicia o monitor anti-suspensão em uma thread separada"""
    logger.info("Iniciando sistema anti-suspensão...")
    
    anti_suspend_thread = threading.Thread(target=monitor_uptime)
    anti_suspend_thread.daemon = True
    anti_suspend_thread.start()
    
    logger.info("Sistema anti-suspensão iniciado em segundo plano.")
    return anti_suspend_thread

# Para testes como módulo individual
if __name__ == "__main__":
    thread = start_anti_suspend_monitor()
    print("Pressione Ctrl+C para encerrar...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Encerrando...")