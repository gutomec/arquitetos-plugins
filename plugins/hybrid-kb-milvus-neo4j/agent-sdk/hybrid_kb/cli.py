"""
Hybrid KB CLI - Command Line Interface
=======================================
Interface de linha de comando para o sistema Hybrid KB.
"""

import asyncio
import argparse
import os
import sys
from dotenv import load_dotenv

from .orchestrator import HybridKBOrchestrator
from .skills import Skills


def main():
    """Main CLI entry point."""
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Hybrid Knowledge Base - GraphRAG com Milvus e Neo4j",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  hybrid-kb search "documentos sobre machine learning"
  hybrid-kb ingest documento.txt
  hybrid-kb analyze
  hybrid-kb health
  hybrid-kb interactive
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    # Search command
    search_parser = subparsers.add_parser("search", help="Buscar no knowledge base")
    search_parser.add_argument("query", help="Query de busca")
    search_parser.add_argument("--strategy", choices=["auto", "vector", "graph", "hybrid"],
                               default="auto", help="Estratégia de busca")

    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingerir documento")
    ingest_parser.add_argument("file", help="Arquivo para ingerir")
    ingest_parser.add_argument("--provider", choices=["google", "cohere"],
                               default="google", help="Provider de embeddings")

    # Analyze command
    subparsers.add_parser("analyze", help="Analisar schema do knowledge base")

    # Health command
    subparsers.add_parser("health", help="Verificar saúde do sistema")

    # Interactive command
    subparsers.add_parser("interactive", help="Modo interativo")

    # Skills command
    skills_parser = subparsers.add_parser("skills", help="Listar ou mostrar skills")
    skills_parser.add_argument("--show", help="Mostrar skill específica")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Run async commands
    asyncio.run(run_command(args))


async def run_command(args):
    """Execute the specified command."""
    orchestrator = HybridKBOrchestrator()

    try:
        if args.command == "search":
            result = await orchestrator.search(args.query, args.strategy)
            print(result)

        elif args.command == "ingest":
            if not os.path.exists(args.file):
                print(f"Erro: Arquivo não encontrado: {args.file}")
                return

            with open(args.file, "r", encoding="utf-8") as f:
                content = f.read()

            metadata = {"filename": args.file}
            result = await orchestrator.ingest(content, metadata)
            print(result)

        elif args.command == "analyze":
            result = await orchestrator.analyze()
            print(result)

        elif args.command == "health":
            result = await orchestrator.health()
            print(result)

        elif args.command == "skills":
            if args.show:
                print(Skills.get(args.show))
            else:
                print("Skills disponíveis:")
                for skill_name in Skills.all().keys():
                    print(f"  - {skill_name}")

        elif args.command == "interactive":
            await interactive_mode(orchestrator)

    finally:
        orchestrator.close()


async def interactive_mode(orchestrator: HybridKBOrchestrator):
    """Run in interactive mode."""
    print("=" * 60)
    print("Hybrid Knowledge Base - Modo Interativo")
    print("=" * 60)
    print("Comandos especiais:")
    print("  /health  - Verificar saúde do sistema")
    print("  /analyze - Analisar schema")
    print("  /skills  - Listar skills disponíveis")
    print("  /quit    - Sair")
    print("=" * 60)
    print()

    while True:
        try:
            user_input = input("Você: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["/quit", "/exit", "/q"]:
                print("Até logo!")
                break

            if user_input.lower() == "/health":
                result = await orchestrator.health()
                print(f"\n{result}\n")
                continue

            if user_input.lower() == "/analyze":
                result = await orchestrator.analyze()
                print(f"\n{result}\n")
                continue

            if user_input.lower() == "/skills":
                print("\nSkills disponíveis:")
                for skill_name in Skills.all().keys():
                    print(f"  - {skill_name}")
                print()
                continue

            # Process regular message
            result = await orchestrator.process(user_input)
            print(f"\nAssistant: {result}\n")

        except KeyboardInterrupt:
            print("\n\nAté logo!")
            break
        except Exception as e:
            print(f"\nErro: {e}\n")


if __name__ == "__main__":
    main()
