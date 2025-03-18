#!/bin/bash

# Script para iniciar o bot Discord e o servidor web
# Desenvolvido para corrigir problemas de inicialização no Replit

echo "=== Iniciando We Profit Discord Bot ==="

# Verificar se o arquivo .env existe
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

# Iniciar o bot completo
echo "Iniciando bot completo com servidor web..."
python main.py --web