#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration settings for the Discord bot
"""
import os

# Tentar carregar variáveis de ambiente do arquivo .env, se existir
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Continuar sem o python-dotenv se não estiver instalado
    pass

class Config:
    """Configuration class for the bot"""
    
    # Configurações do Discord
    TOKEN = os.getenv("DISCORD_TOKEN")
    
    # Prefixo para comandos
    COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")
    
    # ID do servidor Discord principal (opcional)
    # Se não for especificado, o bot usará todos os servidores onde está presente
    GUILD_ID = int(os.getenv("GUILD_ID", "0")) if os.getenv("GUILD_ID") else None
    
    # Presença do bot
    ACTIVITY_TYPE = "playing"  # playing, listening, watching
    ACTIVITY_NAME = "help"  # Sem prefixo para mostrar como 'Hashz' ao invés de '!Hashz'
    
    # Cooldown entre comandos (em segundos)
    DEFAULT_COMMAND_COOLDOWN = 3
    
    # Cores para embeds
    COLORS = {
        "primary": 0x3498db,   # Blue
        "success": 0x2ecc71,   # Green
        "warning": 0xf1c40f,   # Yellow
        "error": 0xe74c3c,     # Red
        "info": 0x9b59b6       # Purple
    }
    
    # Intervalo para o serviço de ping (em segundos)
    PING_INTERVAL = 5 * 60  # 5 minutos
    
    # Configuração de reinicialização automática
    AUTO_RESTART_INTERVAL = 12 * 60 * 60  # 12 horas
    MEMORY_THRESHOLD_MB = 500  # Limiar de uso de memória para reiniciar