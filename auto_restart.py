#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de Reinicialização Automática para o Bot Discord
Reinicia o bot periodicamente para garantir estabilidade
Desenvolvido por Resetsui para We Profit - 2025
Otimizado para melhor desempenho com menor impacto
"""

import os
import gc
import sys
import time
import psutil
import logging
import threading
import subprocess
from datetime import datetime, timedelta

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('auto_restart')

# Importa configurações, se disponível
try:
    from config import Config
    MEMORY_THRESHOLD_MB = Config.MEMORY_THRESHOLD_MB
    CHECK_INTERVAL = 30 * 60  # 30 minutos
    MAX_UPTIME = Config.AUTO_RESTART_INTERVAL
except ImportError:
    # Usa configurações padrão se não puder importar
    MEMORY_THRESHOLD_MB = 500  # 500MB
    CHECK_INTERVAL = 30 * 60  # 30 minutos
    MAX_UPTIME = 12 * 60 * 60  # 12 horas

# Último reinício - inicializado com o timestamp atual
LAST_RESTART = time.time()

def get_memory_usage():
    """Retorna o uso de memória do processo atual em MB"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    # Convertendo para MB
    memory_mb = memory_info.rss / 1024 / 1024
    return memory_mb

def optimize_memory_usage(bot=None):
    """
    Otimiza o uso de memória limpando caches e estruturas de dados temporárias
    Chamada periodicamente para garantir uso eficiente de recursos
    
    Args:
        bot: Instância do bot (opcional, pode ser None)
    
    Returns:
        dict: Estatísticas sobre o que foi limpo
    """
    stats = {"objects_collected": 0, "memory_before": 0, "memory_after": 0}
    
    # Registra uso de memória antes da otimização
    stats["memory_before"] = get_memory_usage()
    
    # Força coleta de lixo para liberar memória não utilizada
    gc.collect()
    stats["objects_collected"] = gc.get_count()[0]
    
    # Libera cache do Discord se possível
    if bot and hasattr(bot, "_connection"):
        if hasattr(bot._connection, "_discord_parsers"):
            bot._connection._discord_parsers.clear()
        
        # Limpa cache de mensagens para canais não recentes
        if hasattr(bot._connection, "_messages"):
            bot._connection._messages.clear()
    
    # Registra uso de memória após a otimização
    stats["memory_after"] = get_memory_usage()
    
    # Calcula quanto foi economizado
    memory_saved = stats["memory_before"] - stats["memory_after"]
    if memory_saved > 0:
        logger.info(f"Otimização de memória: {memory_saved:.2f}MB liberados")
    
    return stats

def needs_restart():
    """Verifica se o bot precisa ser reiniciado com base em várias condições"""
    current_time = time.time()
    uptime = current_time - LAST_RESTART
    
    # Verifica tempo de atividade
    if uptime > MAX_UPTIME:
        logger.info(f"Reinício programado: Tempo máximo de atividade atingido ({uptime/3600:.1f}h)")
        return True
    
    # Verifica uso de memória
    memory_usage = get_memory_usage()
    if memory_usage > MEMORY_THRESHOLD_MB:
        logger.warning(f"Uso de memória elevado: {memory_usage:.2f}MB > {MEMORY_THRESHOLD_MB}MB")
        
        # Tenta otimizar antes de reiniciar
        optimize_memory_usage()
        
        # Verifica novamente após otimização
        new_memory_usage = get_memory_usage()
        if new_memory_usage > MEMORY_THRESHOLD_MB:
            logger.warning(f"Memória continua alta após otimização: {new_memory_usage:.2f}MB")
            return True
    
    return False

def graceful_shutdown():
    """Realiza um desligamento suave antes da reinicialização"""
    logger.info("Realizando desligamento suave antes da reinicialização...")
    
    # Limpa recursos antes de reiniciar
    gc.collect()
    
    # Outras operações de limpeza podem ser adicionadas aqui
    logger.info("Desligamento suave concluído.")

def restart_bot():
    """Reinicia o bot"""
    logger.info("Reiniciando o bot...")
    
    try:
        # Realiza desligamento suave
        graceful_shutdown()
        
        # Atualiza o timestamp do último reinício
        global LAST_RESTART
        LAST_RESTART = time.time()
        
        # Reinicia o processo Python atual 
        # Usa o mesmo interpretador Python e argumentos do processo atual
        python = sys.executable
        os.execl(python, python, *sys.argv)
    except Exception as e:
        logger.error(f"Erro ao reiniciar o bot: {e}")
        # Se falhar, tenta fechar o processo e permitir que um watcher externo o reinicie
        sys.exit(1)

def monitor_and_restart():
    """Thread que monitora condições e reinicia quando necessário"""
    logger.info("Monitor de reinicialização automática iniciado")
    
    while True:
        try:
            # Verifica se é necessário reiniciar
            if needs_restart():
                restart_bot()
                # Código abaixo não deve ser executado após restart_bot()
                # mas mantemos como salvaguarda
                time.sleep(60)
            
            # Otimiza ocasionalmente mesmo sem necessidade de reinício
            if time.time() - LAST_RESTART > 3600:  # A cada hora
                optimize_memory_usage()
            
            # Aguarda até a próxima verificação
            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            logger.error(f"Erro no monitor de reinicialização: {e}")
            time.sleep(60)  # Espera um minuto antes de tentar novamente
            continue

def start_auto_restart_monitor():
    """Inicia o monitor de reinicialização automática"""
    logger.info("Iniciando sistema de reinicialização automática...")
    
    auto_restart_thread = threading.Thread(target=monitor_and_restart)
    auto_restart_thread.daemon = True
    auto_restart_thread.start()
    
    logger.info("Sistema de reinicialização automática iniciado em segundo plano.")
    return auto_restart_thread

# Para testes como módulo individual
if __name__ == "__main__":
    thread = start_auto_restart_monitor()
    print("Pressione Ctrl+C para encerrar...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Encerrando...")