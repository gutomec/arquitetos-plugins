/**
 * Claude Swarm - Main Entry Point
 * CLI e exports para uso como biblioteca.
 */

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';

import { config } from './config';
import { Orchestrator } from './orchestrator';
import { createAgent } from './agents';
import { broker } from './message-broker';
import { ExecutionStrategy } from './types';

// =============================================================================
// EXPORTS
// =============================================================================

export { config } from './config';
export { broker, MessageBroker } from './message-broker';
export { Orchestrator } from './orchestrator';
export {
  BaseAgent,
  AnalystAgent,
  CoderAgent,
  ReviewerAgent,
  TesterAgent,
  ResearcherAgent,
  createAgent,
} from './agents';
export * from './types';

// =============================================================================
// CLI
// =============================================================================

const program = new Command();

program
  .name('swarm')
  .description('Claude Swarm - Multi-agent orchestration system')
  .version('1.0.0');

program
  .command('status')
  .description('Mostra status do swarm')
  .action(async () => {
    const spinner = ora('Verificando status...').start();

    try {
      const orchestrator = new Orchestrator();
      const health = await orchestrator.healthCheck();

      spinner.stop();

      console.log(chalk.bold('\nSwarm Status\n'));
      console.log('─'.repeat(50));

      for (const worker of health.workers) {
        const statusColor = worker.status === 'alive' ? chalk.green : chalk.red;
        console.log(
          `${chalk.cyan(worker.name.padEnd(25))} ${statusColor(worker.status.padEnd(10))} ${chalk.yellow(worker.lastSeenSecondsAgo + 's ago')}`
        );
      }

      console.log('─'.repeat(50));
      console.log(
        `Total: ${health.total} | ${chalk.green('Healthy: ' + health.healthy)} | ${chalk.red('Unhealthy: ' + health.unhealthy)}`
      );

      await broker.disconnect();
    } catch (e) {
      spinner.fail('Erro ao verificar status');
      console.error(e);
      process.exit(1);
    }
  });

program
  .command('execute')
  .description('Executa uma tarefa distribuida')
  .argument('<task>', 'Descricao da tarefa')
  .option('-s, --strategy <strategy>', 'Estrategia: fan-out, pipeline, map-reduce, auto', 'auto')
  .action(async (task: string, options: { strategy: string }) => {
    const spinner = ora('Executando tarefa...').start();

    try {
      const orchestrator = new Orchestrator();
      const strategy = options.strategy as ExecutionStrategy;

      const result = await orchestrator.execute(task, strategy);

      spinner.stop();

      if (result.success) {
        console.log(chalk.green('\n✓ Tarefa executada com sucesso\n'));
        console.log('─'.repeat(50));
        console.log(chalk.bold('Sintese:'));
        console.log(result.synthesis);
        console.log('─'.repeat(50));
        console.log(
          chalk.dim(
            `Workers: ${result.workersSuccessful}/${result.workersConsulted} | Estrategia: ${result.strategy}`
          )
        );
      } else {
        console.log(chalk.red('\n✗ Erro na execucao\n'));
        console.log(result.error);
      }

      await broker.disconnect();
    } catch (e) {
      spinner.fail('Erro na execucao');
      console.error(e);
      process.exit(1);
    }
  });

program
  .command('broadcast')
  .description('Envia broadcast para todos workers')
  .argument('<action>', 'Acao: pause, resume, status, shutdown')
  .option('-m, --message <message>', 'Mensagem adicional', '')
  .action(async (action: string, options: { message: string }) => {
    try {
      const orchestrator = new Orchestrator();
      const msgId = await orchestrator.broadcast(action, options.message);

      console.log(chalk.green(`Broadcast enviado: ${action}`));
      console.log(chalk.dim(`Message ID: ${msgId}`));

      await broker.disconnect();
    } catch (e) {
      console.error(chalk.red('Erro ao enviar broadcast'), e);
      process.exit(1);
    }
  });

program
  .command('shutdown')
  .description('Encerra o swarm graciosamente')
  .action(async () => {
    const spinner = ora('Encerrando swarm...').start();

    try {
      const orchestrator = new Orchestrator();
      await orchestrator.shutdown();

      spinner.succeed('Swarm encerrado com sucesso');
    } catch (e) {
      spinner.fail('Erro ao encerrar swarm');
      console.error(e);
      process.exit(1);
    }
  });

program
  .command('worker')
  .description('Inicia um worker standalone')
  .argument('<type>', 'Tipo: analyst, coder, reviewer, tester, researcher')
  .action(async (type: string) => {
    console.log(chalk.green(`Iniciando worker: ${type}`));

    try {
      const agent = createAgent(type);

      process.on('SIGINT', async () => {
        console.log(chalk.yellow('\nInterrompido pelo usuario'));
        await agent.stop();
        process.exit(0);
      });

      await agent.start();
    } catch (e) {
      console.error(chalk.red('Erro ao iniciar worker'), e);
      process.exit(1);
    }
  });

program
  .command('state')
  .description('Gerencia estado compartilhado')
  .argument('<action>', 'Acao: get, set, list')
  .argument('[key]', 'Chave do estado')
  .option('-v, --value <value>', 'Valor para set')
  .action(async (action: string, key: string | undefined, options: { value?: string }) => {
    try {
      await broker.connect();

      if (action === 'get' && key) {
        const result = await broker.getState(key);
        if (result) {
          console.log(chalk.bold(`State: ${key}`));
          console.log(typeof result === 'object' ? JSON.stringify(result, null, 2) : result);
        } else {
          console.log(chalk.yellow(`Chave nao encontrada: ${key}`));
        }
      } else if (action === 'set' && key && options.value) {
        await broker.setState(key, options.value);
        console.log(chalk.green(`Estado salvo: ${key}`));
      } else if (action === 'list') {
        console.log(chalk.yellow('Use redis-cli para listar chaves: KEYS swarm:state:*'));
      } else {
        console.log(chalk.red('Uso invalido. Veja --help'));
      }

      await broker.disconnect();
    } catch (e) {
      console.error(chalk.red('Erro'), e);
      process.exit(1);
    }
  });

program
  .command('info')
  .description('Mostra informacoes de configuracao')
  .action(() => {
    console.log(chalk.bold('\nConfiguracao do Swarm\n'));
    console.log('─'.repeat(40));
    console.log(`${chalk.cyan('Redis Host:'.padEnd(20))} ${config.redisHost}`);
    console.log(`${chalk.cyan('Redis Port:'.padEnd(20))} ${config.redisPort}`);
    console.log(`${chalk.cyan('Agent ID:'.padEnd(20))} ${config.agentId}`);
    console.log(`${chalk.cyan('Agent Type:'.padEnd(20))} ${config.agentType}`);
    console.log(`${chalk.cyan('Claude Model:'.padEnd(20))} ${config.claudeModel}`);
    console.log(`${chalk.cyan('Task Timeout:'.padEnd(20))} ${config.taskTimeout}ms`);
    console.log(`${chalk.cyan('Max Workers:'.padEnd(20))} ${config.maxWorkers}`);
    console.log('─'.repeat(40));
  });

// Run CLI if this is the main module
if (require.main === module) {
  program.parse();
}
