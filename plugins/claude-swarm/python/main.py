#!/usr/bin/env python3
"""
Claude Swarm - Main Entry Point
CLI para gerenciamento do swarm de agentes.
"""

import asyncio
import json
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import config
from orchestrator import Orchestrator, ExecutionStrategy
from agents import create_agent
from message_broker import broker

app = typer.Typer(
    name="swarm",
    help="Claude Swarm - Multi-agent orchestration system"
)
console = Console()


@app.command()
def status():
    """Mostra status do swarm."""
    async def _status():
        orchestrator = Orchestrator()
        health = await orchestrator.health_check()

        table = Table(title="Swarm Status")
        table.add_column("Worker", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Last Seen", style="yellow")

        for worker in health["workers"]:
            status_style = "green" if worker["status"] == "alive" else "red"
            table.add_row(
                worker["name"],
                f"[{status_style}]{worker['status']}[/{status_style}]",
                f"{worker['last_seen_seconds_ago']}s ago"
            )

        console.print(table)
        console.print(f"\nTotal: {health['total']} | Healthy: {health['healthy']} | Unhealthy: {health['unhealthy']}")

    asyncio.run(_status())


@app.command()
def execute(
    task: str = typer.Argument(..., help="Descricao da tarefa"),
    strategy: str = typer.Option("auto", "--strategy", "-s", help="Estrategia: fan-out, pipeline, map-reduce, auto"),
):
    """Executa uma tarefa distribuida."""
    async def _execute():
        orchestrator = Orchestrator()

        strategy_enum = ExecutionStrategy(strategy)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task("Executando tarefa...", total=None)
            result = await orchestrator.execute(task, strategy_enum)

        if result.get("success"):
            console.print(Panel(
                result.get("synthesis", json.dumps(result, indent=2)),
                title="Resultado",
                border_style="green"
            ))
            console.print(f"\n[dim]Workers: {result.get('workers_successful', 0)}/{result.get('workers_consulted', 0)} | Estrategia: {result.get('strategy')}[/dim]")
        else:
            console.print(Panel(
                json.dumps(result, indent=2),
                title="Erro",
                border_style="red"
            ))

    asyncio.run(_execute())


@app.command()
def broadcast(
    action: str = typer.Argument(..., help="Acao: pause, resume, status, shutdown"),
    message: str = typer.Option("", "--message", "-m", help="Mensagem adicional"),
):
    """Envia broadcast para todos workers."""
    async def _broadcast():
        orchestrator = Orchestrator()
        msg_id = await orchestrator.broadcast(action, message)
        console.print(f"[green]Broadcast enviado: {action}[/green]")
        console.print(f"[dim]Message ID: {msg_id}[/dim]")

    asyncio.run(_broadcast())


@app.command()
def shutdown():
    """Encerra o swarm graciosamente."""
    async def _shutdown():
        orchestrator = Orchestrator()
        await orchestrator.shutdown()
        console.print("[green]Swarm encerrado com sucesso[/green]")

    asyncio.run(_shutdown())


@app.command()
def worker(
    agent_type: str = typer.Argument(..., help="Tipo: analyst, coder, reviewer, tester, researcher"),
):
    """Inicia um worker standalone."""
    async def _worker():
        agent = create_agent(agent_type)
        console.print(f"[green]Iniciando worker: {agent_type}[/green]")

        try:
            await agent.start()
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrompido pelo usuario[/yellow]")
        finally:
            await agent.stop()

    asyncio.run(_worker())


@app.command()
def state(
    action: str = typer.Argument(..., help="Acao: get, set, list"),
    key: Optional[str] = typer.Argument(None, help="Chave do estado"),
    value: Optional[str] = typer.Option(None, "--value", "-v", help="Valor para set"),
):
    """Gerencia estado compartilhado."""
    async def _state():
        await broker.connect()

        if action == "get" and key:
            result = await broker.get_state(key)
            if result:
                console.print(Panel(
                    json.dumps(result, indent=2) if isinstance(result, dict) else str(result),
                    title=f"State: {key}"
                ))
            else:
                console.print(f"[yellow]Chave nao encontrada: {key}[/yellow]")

        elif action == "set" and key and value:
            await broker.set_state(key, value)
            console.print(f"[green]Estado salvo: {key}[/green]")

        elif action == "list":
            # Listar todas as chaves de estado
            import redis.asyncio as redis
            client = redis.Redis(
                host=config.redis_host,
                port=config.redis_port,
                decode_responses=True
            )
            keys = await client.keys("swarm:state:*")
            await client.close()

            table = Table(title="Estado Compartilhado")
            table.add_column("Chave", style="cyan")

            for k in keys:
                table.add_row(k.replace("swarm:state:", ""))

            console.print(table)
            console.print(f"\nTotal: {len(keys)} chaves")

        else:
            console.print("[red]Uso invalido. Veja --help[/red]")

        await broker.disconnect()

    asyncio.run(_state())


@app.command()
def info():
    """Mostra informacoes de configuracao."""
    table = Table(title="Configuracao do Swarm")
    table.add_column("Parametro", style="cyan")
    table.add_column("Valor", style="green")

    table.add_row("Redis Host", config.redis_host)
    table.add_row("Redis Port", str(config.redis_port))
    table.add_row("Agent ID", config.agent_id)
    table.add_row("Agent Type", config.agent_type)
    table.add_row("Claude Model", config.claude_model)
    table.add_row("Task Timeout", f"{config.task_timeout}ms")
    table.add_row("Max Workers", str(config.max_workers))

    console.print(table)


if __name__ == "__main__":
    app()
