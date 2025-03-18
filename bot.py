#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bot Discord para We Profit
Foco em convocação de jogadores com sistema de mensagens auto-destrutivas
Desenvolvido por Resetsui para We Profit - 2025
"""

import os
import sys
import time
import asyncio
import random
import logging
from typing import Optional, List, Dict
from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks
from discord import app_commands

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('bot')

# Carregar variáveis de ambiente
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("python-dotenv não está instalado. Não será possível carregar variáveis de ambiente do arquivo .env")

# Importar configurações
from config import Config

class WeProfit(commands.Bot):
    def __init__(self):
        """Initialize Discord bot with necessary settings"""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.reactions = True
        
        super().__init__(
            command_prefix=Config.COMMAND_PREFIX,
            intents=intents,
            help_command=None  # Usaremos nosso próprio comando de ajuda personalizado
        )
        
        # Armazenamento de mensagens de alerta para auto-destruição
        self.alert_messages = []
        
        # Rastreamento de mensagens por membro
        self.members_messaged = {}
        
        # Adicionar comandos diretamente ao bot
        self.add_commands()
        
    async def setup_cogs(self):
        """Carrega os cogs (módulos) do bot"""
        logger.info("Carregando cogs...")
        
        # Lista de cogs para carregar
        cogs = [
            'cogs_new.commands',  # Comandos básicos
            'cogs_new.events',    # Eventos do bot
        ]
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"Cog carregado: {cog}")
            except Exception as e:
                logger.error(f"Erro ao carregar cog {cog}: {e}")
                
    def add_commands(self):
        """Adiciona comandos essenciais diretamente ao bot"""
        # Os comandos foram movidos para cogs_new/commands.py
    
    async def setup_hook(self):
        """Hook executado na inicialização"""
        logger.info("Configurando hooks e tarefas...")
        
        # Carregar cogs
        await self.setup_cogs()
        
        # Inicia tarefa para verificar mensagens que devem ser auto-destruídas
        self.check_scheduled_deletions.start()
        
        # Registra comandos slash
        @self.tree.command(name="convocar", description="Convoca membros do grupo via mensagem direta")
        @app_commands.describe(
            urgencia="Nível de urgência da convocação",
            detalhes="Detalhes adicionais sobre a convocação"
        )
        @app_commands.choices(urgencia=[
            app_commands.Choice(name="Baixa - Informativo apenas", value="baixa"),
            app_commands.Choice(name="Média - Recomendado comparecer", value="média"),
            app_commands.Choice(name="Alta - Presença obrigatória", value="alta")
        ])
        async def convocar_slash(interaction, urgencia: str, detalhes: Optional[str] = None):
            await self.convocar_comando(interaction, urgencia, detalhes)
        
        try:
            # Sincronizar os comandos slash
            await self.tree.sync()
            logger.info("Comandos slash sincronizados com sucesso")
        except Exception as e:
            logger.error(f"Erro ao sincronizar comandos slash: {e}")
    
    async def on_ready(self):
        """Evento chamado quando o bot estiver pronto"""
        logger.info(f"Bot conectado como {self.user} (ID: {self.user.id})")
        
        # Configurar status/atividade
        activity_type = Config.ACTIVITY_TYPE.lower()
        activity_name = Config.ACTIVITY_NAME
        
        if activity_type == "playing":
            activity = discord.Game(name=activity_name)
        elif activity_type == "watching":
            activity = discord.Activity(type=discord.ActivityType.watching, name=activity_name)
        elif activity_type == "listening":
            activity = discord.Activity(type=discord.ActivityType.listening, name=activity_name)
        else:
            activity = None
            
        await self.change_presence(activity=activity)
        
        # Mostrar informações sobre os servidores conectados
        if len(self.guilds) > 0:
            logger.info(f"Bot conectado a {len(self.guilds)} servidor(es):")
            for guild in self.guilds:
                logger.info(f"  • {guild.name} (ID: {guild.id}) - {len(guild.members)} membros")
        else:
            logger.warning("Bot não está conectado a nenhum servidor")
        
        # Verificar comandos carregados
        logger.info(f"Comandos carregados: {len(self.commands)}")
    
    async def convocar_comando_texto(self, ctx, urgencia: str, *, detalhes: Optional[str] = None):
        """Versão de texto do comando convocar"""
        # Normaliza a entrada removendo acentos
        urgencia = urgencia.lower().strip()
        
        # Verifica se a urgência é válida
        opcoes_validas = ["baixa", "media", "média", "alta"]
        if urgencia not in opcoes_validas:
            await ctx.send(f"❌ Urgência inválida. Use: {', '.join(opcoes_validas)}")
            return
            
        # Converte 'media' para 'média' para padronizar
        if urgencia == "media":
            urgencia = "média"
            
        # Cria resposta temporária
        response = await ctx.send("⏳ Enviando convocação para todos os membros...")
        
        # Chama a função principal de convocação
        resultado = await self._enviar_convocacao(ctx.guild, urgencia, detalhes, ctx.author)
        
        # Atualiza a mensagem com o resultado
        await response.edit(content=resultado)
    
    async def convocar_comando(self, interaction: discord.Interaction, urgencia: str, detalhes: Optional[str] = None):
        """Envia um alerta de combate em mensagem privada para todos os membros do servidor"""
        await interaction.response.defer()
        
        # Obter o servidor e o autor
        guild = interaction.guild
        autor = interaction.user
        
        # Chama a função principal de convocação
        resultado = await self._enviar_convocacao(guild, urgencia, detalhes, autor)
        
        # Responde com o resultado
        await interaction.followup.send(resultado)
    
    async def _enviar_convocacao(self, guild, urgencia: str, detalhes: Optional[str], autor):
        """Função interna para enviar convocações para todos os membros"""
        if not guild:
            return "❌ Este comando deve ser usado em um servidor."
            
        # Mapear urgência para cores
        cores = {
            "baixa": Config.COLORS["info"],     # Azul
            "média": Config.COLORS["warning"],  # Amarelo
            "alta": Config.COLORS["error"]      # Vermelho
        }
        
        # Tempo de auto-destruição baseado na urgência
        tempos_destruicao = {
            "baixa": 24,    # 24 horas
            "média": 6,     # 6 horas
            "alta": 2       # 2 horas
        }
        
        # Verificar se é urgência média ou alta (formato original)
        if urgencia.lower() in ["media", "média"]:
            alert_level = "🟠 MÉDIA"
        elif urgencia.lower() == "alta":
            alert_level = "🔴 ALTA"
        else:
            alert_level = "🟢 BAIXA"
        
        # Criar embed para a mensagem - mantendo o formato original
        embed = discord.Embed(
            title=f"🚨 ALERTA DE URGÊNCIA {alert_level} - We Profit",
            description=f"Você está sendo convocado para uma atividade do grupo!",
            color=cores[urgencia]
        )
        
        # Adicionar detalhes se fornecidos
        if detalhes:
            embed.add_field(
                name="Detalhes",
                value=detalhes,
                inline=False
            )
            
        # Adicionar informação sobre auto-destruição
        tempo_destruicao = tempos_destruicao[urgencia]
        embed.add_field(
            name="Auto-Destruição",
            value=f"⏱️ Esta mensagem se auto-destruirá em **{tempo_destruicao} horas**",
            inline=False
        )
        
        # Adicionar rodapé com informações do autor
        embed.set_footer(text=f"Enviado por {autor.name} • {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Enviar para todos os membros
        enviadas = 0
        falhas = 0
        
        for membro in guild.members:
            # Pular bots e o próprio autor
            if membro.bot or membro == autor:
                continue
                
            try:
                # Enviar mensagem para o membro
                dm_channel = await membro.create_dm()
                mensagem = await dm_channel.send(embed=embed)
                
                # Salvar a mensagem para auto-destruição
                self.alert_messages.append({
                    'message_id': mensagem.id,
                    'channel_id': dm_channel.id,
                    'delete_at': datetime.now() + timedelta(hours=tempo_destruicao)
                })
                
                # Registrar nos membros contatados
                if str(membro) not in self.members_messaged:
                    self.members_messaged[str(membro)] = []
                
                self.members_messaged[str(membro)].append({
                    'message_id': mensagem.id,
                    'urgencia': urgencia,
                    'timestamp': time.time()
                })
                
                enviadas += 1
                await asyncio.sleep(0.5)  # Pequena pausa para evitar rate limits
                
            except discord.Forbidden:
                # Não tem permissão para enviar DM para este membro
                falhas += 1
                continue
                
            except Exception as e:
                logger.error(f"Erro ao enviar mensagem para {membro}: {e}")
                falhas += 1
                continue
                
        # Resultado final
        if enviadas > 0:
            return f"✅ Convocação enviada para **{enviadas}** membros! ({falhas} falhas)"
        else:
            return f"❌ Não foi possível enviar mensagens para nenhum membro. Certifique-se de que o bot tem permissões adequadas."
    
    @tasks.loop(minutes=5)
    async def check_scheduled_deletions(self):
        """Verifica periodicamente mensagens para auto-destruição"""
        now = datetime.now()
        mensagens_para_deletar = []
        
        # Identifica mensagens que devem ser deletadas
        for msg in self.alert_messages:
            if now >= msg['delete_at']:
                mensagens_para_deletar.append(msg)
                
        # Remove mensagens
        for msg in mensagens_para_deletar:
            try:
                channel = self.get_channel(msg['channel_id'])
                if not channel:
                    # Tenta obter o canal como canal de DM
                    channel = await self.fetch_channel(msg['channel_id'])
                    
                if channel:
                    # Tenta excluir a mensagem
                    try:
                        message = await channel.fetch_message(msg['message_id'])
                        await message.delete()
                        logger.info(f"Mensagem {msg['message_id']} auto-destruída com sucesso")
                    except Exception as e:
                        logger.warning(f"Não foi possível excluir mensagem {msg['message_id']}: {e}")
                        
            except Exception as e:
                logger.error(f"Erro ao processar auto-destruição: {e}")
                
            # Remove da lista de mensagens pendentes
            self.alert_messages.remove(msg)
    
    @check_scheduled_deletions.before_loop
    async def before_scheduled_deletions(self):
        """Aguarda o bot estar pronto antes de iniciar a tarefa de verificação"""
        await self.wait_until_ready()

async def run_bot_async():
    """Função principal assíncrona para iniciar o bot"""
    # Verificar token
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("Token do Discord não encontrado. Configure a variável de ambiente DISCORD_TOKEN.")
        logger.error("Você pode criar um arquivo .env com DISCORD_TOKEN=seu_token_aqui")
        return
    
    # Criar e iniciar o bot
    bot = WeProfit()
    
    try:
        logger.info("Iniciando bot...")
        await bot.start(token)
    except discord.LoginFailure:
        logger.error("Falha ao fazer login no Discord. Verifique se o token está correto.")
    except Exception as e:
        logger.error(f"Erro ao iniciar o bot: {e}")
    finally:
        # Garantir que o bot seja fechado corretamente
        if not bot.is_closed():
            await bot.close()

def run_bot():
    """Função principal para iniciar o bot usando asyncio.run"""
    try:
        asyncio.run(run_bot_async())
    except KeyboardInterrupt:
        logger.info("Bot encerrado pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")

if __name__ == "__main__":
    run_bot()