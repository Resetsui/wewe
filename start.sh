#!/bin/bash

# Script para iniciar o bot Discord e o servidor web
# Desenvolvido por Resetsui para We Profit - 2025

echo "=== Iniciando We Profit Discord Bot ==="

# Função para verificar se o arquivo .env existe
check_env_file() {
  if [ ! -f .env ]; then
    echo "AVISO: Arquivo .env não encontrado."
    echo "Criando arquivo .env básico..."
    
    # Cria um arquivo .env básico
    cat > .env << EOF
# Configurações do Bot Discord
# IMPORTANTE: Substitua com seu token real do Discord
DISCORD_TOKEN=coloque_seu_token_aqui
COMMAND_PREFIX=!
GUILD_ID=123456789012345678  # Substitua pelo ID do seu servidor Discord
EOF
    
    echo "Arquivo .env criado. Por favor, edite-o com suas informações."
  fi
}

# Função para iniciar apenas o servidor web
start_web_only() {
  echo "Iniciando servidor web..."
  python app.py
}

# Função para iniciar o bot completo
start_full() {
  echo "Iniciando bot completo..."
  python main.py --web
}

# Função para iniciar apenas o bot (sem web)
start_bot_only() {
  echo "Iniciando apenas o bot Discord..."
  python main.py
}

# Verifica argumentos
case "$1" in
  --web-only)
    check_env_file
    start_web_only
    ;;
  --bot-only)
    check_env_file
    start_bot_only
    ;;
  *)
    check_env_file
    start_full
    ;;
esac