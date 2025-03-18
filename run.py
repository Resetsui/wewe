#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para iniciar o Bot Discord com servidor web para anti-suspensão
"""

import os
import argparse
import threading
import time
import sys

def run_bot():
    """Inicia o bot Discord"""
    print("Iniciando o bot Discord...")
    try:
        # Tenta importar e executar o bot
        from bot import run_bot
        run_bot()
    except ImportError:
        print("Erro ao importar o bot.py")
        print("Certifique-se de que o arquivo existe e que todas as dependências estão instaladas.")
        sys.exit(1)

def run_webserver():
    """Inicia o servidor web separadamente"""
    print("Iniciando o servidor web...")
    os.system("python app.py")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Inicia o Bot Discord com servidor web')
    parser.add_argument('--web-only', action='store_true', help='Inicia apenas o servidor web')
    parser.add_argument('--bot-only', action='store_true', help='Inicia apenas o bot Discord')
    args = parser.parse_args()

    # Verifica se há um token do Discord configurado
    if not os.environ.get('DISCORD_TOKEN') and not args.web_only:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            if not os.environ.get('DISCORD_TOKEN'):
                print("AVISO: Token do Discord não encontrado nas variáveis de ambiente ou arquivo .env")
                print("O bot não conseguirá conectar ao Discord sem um token válido.")
                print("Execute novamente com a flag --web-only para iniciar apenas o servidor web.")
                
                if not args.bot_only:
                    print("Iniciando apenas o servidor web...")
                    run_webserver()
                    return
        except ImportError:
            print("AVISO: python-dotenv não está instalado. Não é possível carregar variáveis do arquivo .env")
    
    if args.web_only:
        run_webserver()
    elif args.bot_only:
        run_bot()
    else:
        # Inicia o bot e o servidor web em threads separadas
        bot_thread = threading.Thread(target=run_bot)
        web_thread = threading.Thread(target=run_webserver)
        
        bot_thread.daemon = True
        web_thread.daemon = True
        
        web_thread.start()
        time.sleep(1)  # Espera o servidor web iniciar
        bot_thread.start()
        
        try:
            # Mantém o programa principal em execução
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nEncerrando o bot e o servidor web...")
            sys.exit(0)

if __name__ == "__main__":
    main()