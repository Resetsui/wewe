#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Discord Bot para We Profit
Arquivo principal que inicializa o bot e configura sistemas de suporte

Desenvolvido por Resetsui para a Guild We Profit - 2025
Otimizado para Replit
"""

import os
import sys
import time
import threading
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('main')

def start_bot():
    """Inicia o bot em uma thread separada"""
    try:
        # Importar apenas quando necessário para evitar problemas de inicialização
        from bot import run_bot
        
        logger.info("Iniciando o Bot Discord...")
        
        # Criar uma thread para o bot
        bot_thread = threading.Thread(target=run_bot)
        bot_thread.daemon = True
        bot_thread.start()
        
        return bot_thread
    except ImportError as e:
        logger.error(f"Erro ao importar o módulo do bot: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro ao iniciar o bot: {e}")
        return None

def start_web_server():
    """Inicia o servidor web para anti-suspensão"""
    try:
        # Importar apenas quando necessário
        from ping_service import start_ping_service
        
        logger.info("Iniciando o servidor web para anti-suspensão...")
        web_thread = start_ping_service()
        
        return web_thread
    except ImportError as e:
        logger.error(f"Erro ao importar o módulo do servidor web: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro ao iniciar o servidor web: {e}")
        return None

def main():
    """Função principal que coordena o início de todos os sistemas"""
    logger.info("Iniciando sistemas We Profit")
    
    # Iniciar servidor web para anti-suspensão
    web_thread = start_web_server()
    
    # Verificar token do Discord
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        logger.warning("Token do Discord não encontrado nas variáveis de ambiente")
        logger.warning("O servidor web será iniciado, mas o bot não conseguirá conectar ao Discord")
        
        # Solicitar o token ao usuário
        print("\n==== CONFIGURAÇÃO NECESSÁRIA ====")
        print("Para usar o bot Discord, você precisa configurar um token válido.")
        print("1. Acesse https://discord.com/developers/applications")
        print("2. Crie uma aplicação ou selecione uma existente")
        print("3. Vá para a seção 'Bot' e copie o token")
        print("4. Configure a variável de ambiente DISCORD_TOKEN no Replit")
        print("===================================\n")
    else:
        # Iniciar o bot Discord
        bot_thread = start_bot()
        if bot_thread:
            logger.info("Bot Discord iniciado com sucesso")
        else:
            logger.error("Falha ao iniciar o bot Discord")
    
    # Manter o programa principal em execução
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Encerrando sistemas...")
        sys.exit(0)

if __name__ == "__main__":
    main()