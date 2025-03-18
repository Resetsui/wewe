/**
 * Inicializador para o Bot Discord We Profit
 * Este arquivo serve como ponto de entrada para compatibilidade com o workflow do Replit
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

console.log('=== We Profit Discord Bot - Iniciador ===');
console.log('Verificando permissões do script...');

// Garantir que o script shell tenha permissões de execução
try {
  fs.chmodSync('run.sh', 0o755);
  console.log('Permissões do script atualizadas com sucesso');
} catch (error) {
  console.error('Erro ao atualizar permissões:', error);
}

console.log('Iniciando a aplicação Python via script...');

// Comando para iniciar o bot Python usando o script shell
const pythonProcess = spawn('./run.sh', [], {
  stdio: 'inherit',
  shell: true
});

// Capturar eventos de saída do processo Python
pythonProcess.on('error', (err) => {
  console.error('Erro ao iniciar o processo Python:', err);
});

pythonProcess.on('close', (code) => {
  if (code !== 0) {
    console.log(`O processo Python encerrou com código ${code}`);
  }
});

// Lidar com sinais para encerramento limpo
process.on('SIGINT', () => {
  console.log('Recebido SIGINT. Encerrando o processo Python...');
  pythonProcess.kill('SIGINT');
});

process.on('SIGTERM', () => {
  console.log('Recebido SIGTERM. Encerrando o processo Python...');
  pythonProcess.kill('SIGTERM');
});