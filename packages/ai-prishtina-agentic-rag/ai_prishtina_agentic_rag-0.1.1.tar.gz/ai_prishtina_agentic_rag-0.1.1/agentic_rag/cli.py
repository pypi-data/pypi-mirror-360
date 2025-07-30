"""Command-line interface for the Agentic RAG library."""

import asyncio
import json
import os
import sys

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from typing import Optional

from .core.agent import AgenticRAG
from .document_processing.loaders import DocumentLoader
from .retrieval.vector_stores import ChromaVectorStore, FAISSVectorStore
from .llm.providers import OpenAIProvider, AnthropicProvider, LocalModelProvider
from .tools import ToolRegistry, WebSearchTool, CalculatorTool, StatisticsTool
from .utils.config import Config
from .utils.logging import setup_logging

console = Console()


@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, config, verbose):
    """Agentic RAG - Professional-grade agentic Retrieval-Augmented Generation library."""
    ctx.ensure_object(dict)
    
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(level=log_level, enable_rich=True)
    
    # Load configuration
    if config:
        ctx.obj['config'] = Config.from_file(config)
    else:
        ctx.obj['config'] = Config.from_env()
    
    ctx.obj['verbose'] = verbose


@cli.command()
@click.argument('documents_path', type=click.Path(exists=True))
@click.option('--vector-store', '-vs', type=click.Choice(['chroma', 'faiss']), default='chroma', help='Vector store to use')
@click.option('--collection-name', '-cn', default='agentic_rag', help='Collection name')
@click.option('--persist-dir', '-pd', type=click.Path(), help='Persistence directory')
@click.option('--recursive', '-r', is_flag=True, help='Process directories recursively')
@click.pass_context
def ingest(ctx, documents_path, vector_store, collection_name, persist_dir, recursive):
    """Ingest documents into the vector store."""
    # config = ctx.obj['config']  # Will be used when full implementation is ready
    
    async def _ingest():
        try:
            # Initialize vector store
            if vector_store == 'chroma':
                vs = ChromaVectorStore(
                    collection_name=collection_name,
                    persist_directory=persist_dir
                )
            else:  # faiss
                persist_path = os.path.join(persist_dir, f"{collection_name}.faiss") if persist_dir else None
                vs = FAISSVectorStore(persist_path=persist_path)
            
            # Load documents
            loader = DocumentLoader()
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Loading documents...", total=None)
                
                if os.path.isfile(documents_path):
                    documents = [loader.load_file(documents_path)]
                else:
                    documents = loader.load_directory(documents_path, recursive=recursive)
                
                progress.update(task, description=f"Loaded {len(documents)} documents")
                
                # Convert to vector store format
                from .retrieval.vector_stores import Document as VectorDocument
                vs_documents = []
                for doc in documents:
                    vs_doc = VectorDocument(
                        id=f"doc_{len(vs_documents)}",
                        content=doc.content,
                        metadata=doc.metadata
                    )
                    vs_documents.append(vs_doc)
                
                progress.update(task, description="Adding to vector store...")
                doc_ids = await vs.add_documents(vs_documents)
                
                progress.update(task, description=f"Successfully ingested {len(doc_ids)} documents")
            
            console.print(f"✅ Successfully ingested {len(doc_ids)} documents into {vector_store} vector store")
            
        except Exception as e:
            console.print(f"❌ Error during ingestion: {e}", style="red")
            sys.exit(1)
    
    asyncio.run(_ingest())


@cli.command()
@click.option('--vector-store', '-vs', type=click.Choice(['chroma', 'faiss']), default='chroma', help='Vector store to use')
@click.option('--collection-name', '-cn', default='agentic_rag', help='Collection name')
@click.option('--persist-dir', '-pd', type=click.Path(), help='Persistence directory')
@click.option('--llm-provider', '-llm', type=click.Choice(['openai', 'anthropic', 'local']), default='openai', help='LLM provider')
@click.option('--model', '-m', help='Model name')
@click.option('--enable-agent', '-a', is_flag=True, default=True, help='Enable agentic capabilities')
@click.option('--enable-tools', '-t', is_flag=True, default=True, help='Enable tools')
@click.pass_context
def chat(ctx, vector_store, collection_name, persist_dir, llm_provider, model, enable_agent, enable_tools):
    """Start an interactive chat session."""
    config = ctx.obj['config']
    
    async def _chat():
        try:
            # Initialize vector store
            if vector_store == 'chroma':
                vs = ChromaVectorStore(
                    collection_name=collection_name,
                    persist_directory=persist_dir
                )
            else:  # faiss
                persist_path = os.path.join(persist_dir, f"{collection_name}.faiss") if persist_dir else None
                vs = FAISSVectorStore(persist_path=persist_path)
            
            # Initialize LLM provider
            if llm_provider == 'openai':
                llm = OpenAIProvider(model=model or "gpt-3.5-turbo")
            elif llm_provider == 'anthropic':
                llm = AnthropicProvider(model=model or "claude-3-sonnet-20240229")
            else:  # local
                llm = LocalModelProvider(model=model or "microsoft/DialoGPT-medium")
            
            # Initialize RAG system
            rag = AgenticRAG(
                config=config,
                vector_store=vs,
                llm_provider=llm,
                enable_agent=enable_agent
            )
            
            # Setup tools if enabled
            if enable_tools:
                tool_registry = ToolRegistry()
                tool_registry.register(WebSearchTool())
                tool_registry.register(CalculatorTool())
                tool_registry.register(StatisticsTool())
                rag.tools = tool_registry
            
            # Check if vector store has documents
            doc_count = await vs.count_documents()
            if doc_count == 0:
                console.print("⚠️  No documents found in vector store. Use 'ingest' command to add documents first.", style="yellow")
            else:
                console.print(f"📚 Found {doc_count} documents in vector store")
            
            # Display welcome message
            welcome_panel = Panel(
                "[bold blue]Welcome to Agentic RAG Chat![/bold blue]\n\n"
                f"Vector Store: {vector_store} ({doc_count} documents)\n"
                f"LLM Provider: {llm_provider}\n"
                f"Agentic Mode: {'Enabled' if enable_agent else 'Disabled'}\n"
                f"Tools: {'Enabled' if enable_tools else 'Disabled'}\n\n"
                "Type 'quit' or 'exit' to end the session.",
                title="Configuration",
                border_style="blue"
            )
            console.print(welcome_panel)
            
            # Chat loop
            while True:
                try:
                    query = console.input("\n[bold green]You:[/bold green] ")
                    
                    if query.lower() in ['quit', 'exit', 'q']:
                        console.print("👋 Goodbye!")
                        break
                    
                    if not query.strip():
                        continue
                    
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console
                    ) as progress:
                        task = progress.add_task("Processing query...", total=None)
                        
                        response = await rag.query(query)
                        
                        progress.update(task, description="Query processed")
                    
                    # Display response
                    console.print(f"\n[bold blue]Assistant:[/bold blue] {response.answer}")
                    
                    if response.sources:
                        console.print(f"\n[dim]📚 Sources ({len(response.sources)}):[/dim]")
                        for i, source in enumerate(response.sources, 1):
                            source_info = source.get('title', source.get('source', 'Unknown'))
                            console.print(f"  {i}. {source_info}")
                    
                    if response.reasoning_steps and enable_agent:
                        console.print(f"\n[dim]🧠 Reasoning Steps:[/dim]")
                        for i, step in enumerate(response.reasoning_steps, 1):
                            console.print(f"  {i}. {step}")
                    
                    console.print(f"\n[dim]🎯 Confidence: {response.confidence:.2f}[/dim]")
                    
                except KeyboardInterrupt:
                    console.print("\n👋 Goodbye!")
                    break
                except Exception as e:
                    console.print(f"❌ Error: {e}", style="red")
                    continue
        
        except Exception as e:
            console.print(f"❌ Failed to initialize chat: {e}", style="red")
            sys.exit(1)
    
    asyncio.run(_chat())


@cli.command()
@click.argument('query')
@click.option('--vector-store', '-vs', type=click.Choice(['chroma', 'faiss']), default='chroma', help='Vector store to use')
@click.option('--collection-name', '-cn', default='agentic_rag', help='Collection name')
@click.option('--persist-dir', '-pd', type=click.Path(), help='Persistence directory')
@click.option('--llm-provider', '-llm', type=click.Choice(['openai', 'anthropic', 'local']), default='openai', help='LLM provider')
@click.option('--model', '-m', help='Model name')
@click.option('--output', '-o', type=click.Choice(['text', 'json']), default='text', help='Output format')
@click.pass_context
def query(ctx, query, vector_store, collection_name, persist_dir, llm_provider, model, output):
    """Execute a single query."""
    config = ctx.obj['config']
    
    async def _query():
        try:
            # Initialize components (similar to chat command)
            if vector_store == 'chroma':
                vs = ChromaVectorStore(
                    collection_name=collection_name,
                    persist_directory=persist_dir
                )
            else:
                persist_path = os.path.join(persist_dir, f"{collection_name}.faiss") if persist_dir else None
                vs = FAISSVectorStore(persist_path=persist_path)
            
            if llm_provider == 'openai':
                llm = OpenAIProvider(model=model or "gpt-3.5-turbo")
            elif llm_provider == 'anthropic':
                llm = AnthropicProvider(model=model or "claude-3-sonnet-20240229")
            else:
                llm = LocalModelProvider(model=model or "microsoft/DialoGPT-medium")
            
            rag = AgenticRAG(
                config=config,
                vector_store=vs,
                llm_provider=llm,
                enable_agent=True
            )
            
            # Execute query
            response = await rag.query(query)
            
            # Output response
            if output == 'json':
                result = {
                    "query": query,
                    "answer": response.answer,
                    "sources": response.sources,
                    "reasoning_steps": response.reasoning_steps,
                    "confidence": response.confidence,
                    "metadata": response.metadata,
                    "timestamp": response.timestamp.isoformat()
                }
                console.print(json.dumps(result, indent=2))
            else:
                console.print(f"[bold blue]Query:[/bold blue] {query}")
                console.print(f"[bold green]Answer:[/bold green] {response.answer}")
                
                if response.sources:
                    console.print(f"\n[bold]Sources:[/bold]")
                    for i, source in enumerate(response.sources, 1):
                        console.print(f"  {i}. {source.get('title', source.get('source', 'Unknown'))}")
                
                console.print(f"\n[dim]Confidence: {response.confidence:.2f}[/dim]")
        
        except Exception as e:
            console.print(f"❌ Error: {e}", style="red")
            sys.exit(1)
    
    asyncio.run(_query())


@cli.command()
@click.option('--vector-store', '-vs', type=click.Choice(['chroma', 'faiss']), default='chroma', help='Vector store to use')
@click.option('--collection-name', '-cn', default='agentic_rag', help='Collection name')
@click.option('--persist-dir', '-pd', type=click.Path(), help='Persistence directory')
@click.pass_context
def status(ctx, vector_store, collection_name, persist_dir):
    """Show system status and statistics."""
    # ctx will be used when full implementation is ready
    
    async def _status():
        try:
            # Initialize vector store
            if vector_store == 'chroma':
                vs = ChromaVectorStore(
                    collection_name=collection_name,
                    persist_directory=persist_dir
                )
            else:
                persist_path = os.path.join(persist_dir, f"{collection_name}.faiss") if persist_dir else None
                vs = FAISSVectorStore(persist_path=persist_path)
            
            # Get statistics
            doc_count = await vs.count_documents()
            
            # Create status table
            table = Table(title="Agentic RAG Status")
            table.add_column("Component", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Details")
            
            table.add_row("Vector Store", vector_store.upper(), f"Collection: {collection_name}")
            table.add_row("Documents", str(doc_count), "Total indexed documents")
            
            if persist_dir:
                table.add_row("Persistence", "Enabled", persist_dir)
            else:
                table.add_row("Persistence", "Disabled", "In-memory only")
            
            # Check API keys
            openai_key = "✅ Set" if os.getenv("OPENAI_API_KEY") else "❌ Not set"
            anthropic_key = "✅ Set" if os.getenv("ANTHROPIC_API_KEY") else "❌ Not set"
            
            table.add_row("OpenAI API Key", openai_key, "")
            table.add_row("Anthropic API Key", anthropic_key, "")
            
            console.print(table)
            
        except Exception as e:
            console.print(f"❌ Error getting status: {e}", style="red")
            sys.exit(1)
    
    asyncio.run(_status())


@cli.command()
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def config_template(output):
    """Generate a configuration template."""
    template = """# Agentic RAG Configuration Template

llm:
  provider: "openai"  # openai, anthropic, local
  model: "gpt-3.5-turbo"
  api_key: null  # Set via environment variable
  temperature: 0.7
  max_tokens: 1000

vector_store:
  provider: "chroma"  # chroma, faiss, pinecone, weaviate
  collection_name: "agentic_rag"
  persist_directory: "./data/vector_store"
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"

document_processing:
  chunk_size: 1000
  chunk_overlap: 200
  chunking_strategy: "recursive"  # fixed, semantic, recursive

retrieval:
  top_k: 5
  similarity_threshold: 0.7
  enable_reranking: true
  enable_hybrid_search: false

agent:
  enable_planning: true
  max_planning_steps: 5
  enable_memory: true
  enable_tools: true
  available_tools: ["web_search", "calculator"]

evaluation:
  enable_evaluation: false
  metrics: ["relevance", "faithfulness"]
  log_level: "INFO"
"""
    
    if output:
        with open(output, 'w') as f:
            f.write(template)
        console.print(f"✅ Configuration template saved to {output}")
    else:
        console.print(template)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
