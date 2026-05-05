"""CLI tool for SAS RAG Assistant"""

import click

from src.core.logger import get_logger
from src.embeddings.vector_store import VectorStore
from src.embeddings.embedding_model import EmbeddingGenerator
from src.rag.retriever import CodeRetriever
from src.llm.code_generator import CodeGenerator
from src.data.corpus_loader import CorpusLoader, CodeChunker
from src.core.config import get_config

logger = get_logger(__name__)


def _format_score(value):
    """Format optional numeric scores for CLI output."""
    return f"{value:.4f}" if isinstance(value, (int, float)) else "n/a"


@click.group()
def cli():
    """SAS RAG Assistant CLI"""
    pass


@cli.command()
@click.option("--corpus-path", default=None, help="Path to SAS code corpus")
@click.option("--reset", is_flag=True, help="Clear the vector database before ingesting")
def ingest(corpus_path, reset):
    """Ingest SAS code corpus into vector database"""
    click.echo("Ingesting SAS code corpus...")

    config = get_config()
    corpus_path = corpus_path or config.corpus_path

    try:
        # Load corpus
        loader = CorpusLoader(corpus_path)
        corpus = loader.load_corpus()
        click.echo(f"Loaded {len(corpus)} SAS files")

        # Chunk code
        chunker = CodeChunker(chunk_size=config.chunk_size)
        chunks = []
        for doc in corpus:
            doc_chunks = chunker.chunk_code(doc["code"], doc["id"])
            chunks.extend(doc_chunks)
        click.echo(f"Created {len(chunks)} code chunks")

        # Generate embeddings
        embedding_gen = EmbeddingGenerator()
        texts = [chunk["text"] for chunk in chunks]
        embeddings = embedding_gen.encode(texts)
        click.echo(f"Generated {len(embeddings)} embeddings")

        # Store in vector DB
        vector_store = VectorStore()
        if reset:
            vector_store.clear_collection()

        ids = [chunk["id"] for chunk in chunks]
        metadatas = [
            {
                "code_id": chunk["code_id"],
                "start_line": chunk["start_line"],
                "end_line": chunk["end_line"],
                "chunk_type": chunk.get("chunk_type", "sas_block"),
            }
            for chunk in chunks
        ]
        vector_store.add_documents(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        click.echo("Ingestion complete.")

    except Exception as e:
        click.echo(f"Ingestion failed: {e}", err=True)
        raise


@cli.command()
@click.option("--requirement", prompt="Enter code requirement", help="Code requirement")
@click.option("--top-k", default=3, help="Number of similar snippets to retrieve")
def generate(requirement, top_k):
    """Generate SAS code for a requirement"""
    click.echo(f"Generating code for: {requirement}\n")

    try:
        # Initialize components
        vector_store = VectorStore()
        retriever = CodeRetriever(vector_store)
        code_gen = CodeGenerator()

        # Retrieve snippets
        retrieved = retriever.retrieve(requirement, top_k=top_k)

        if retrieved:
            click.echo("Retrieved similar code snippets:\n")
            for i, snippet in enumerate(retrieved, 1):
                similarity = snippet.get("similarity", 0)
                sources = ", ".join(snippet.get("retrieval_sources", [])) or "unknown"
                metadata = snippet.get("metadata", {})
                location = (
                    f"{metadata.get('code_id', 'unknown')}:"
                    f"{metadata.get('start_line', '?')}-{metadata.get('end_line', '?')}"
                )
                click.echo(f"--- Snippet {i} | ID: {snippet['id']} ---")
                click.echo(
                    "Scores: "
                    f"similarity={similarity:.2%}, "
                    f"hybrid={_format_score(snippet.get('hybrid_score'))}, "
                    f"rerank={_format_score(snippet.get('rerank_score'))}, "
                    f"final={_format_score(snippet.get('final_score'))}"
                )
                click.echo(f"Sources: {sources} | Location: {location}")
                click.echo(snippet["code"][:300] + "...\n")

            # Adapt code
            context = retriever.format_context(retrieved)
            adapted_code = code_gen.adapt_code(context, requirement)
        else:
            click.echo("No similar snippets found. Generating from scratch.\n")
            adapted_code = code_gen.generate_code(requirement)

        click.echo("\n=== GENERATED CODE ===\n")
        click.echo(adapted_code)

    except Exception as e:
        click.echo(f"Generation failed: {e}", err=True)
        raise


@cli.command()
@click.option("--query", prompt="Enter search query", help="Search query")
@click.option("--top-k", default=3, help="Number of results")
def search(query, top_k):
    """Search for similar code snippets"""
    click.echo(f"Searching for: {query}\n")

    try:
        vector_store = VectorStore()
        retriever = CodeRetriever(vector_store)

        retrieved = retriever.retrieve(query, top_k=top_k)

        if retrieved:
            for i, snippet in enumerate(retrieved, 1):
                similarity = snippet.get("similarity", 0)
                sources = ", ".join(snippet.get("retrieval_sources", [])) or "unknown"
                metadata = snippet.get("metadata", {})
                location = (
                    f"{metadata.get('code_id', 'unknown')}:"
                    f"{metadata.get('start_line', '?')}-{metadata.get('end_line', '?')}"
                )
                click.echo(f"[{i}] ID: {snippet['id']} | Location: {location}")
                click.echo(
                    "    Scores: "
                    f"similarity={similarity:.2%}, "
                    f"hybrid={_format_score(snippet.get('hybrid_score'))}, "
                    f"rerank={_format_score(snippet.get('rerank_score'))}, "
                    f"final={_format_score(snippet.get('final_score'))}"
                )
                click.echo(f"    Sources: {sources}")
                click.echo(snippet["code"][:200] + "...\n")
        else:
            click.echo("No results found.")

    except Exception as e:
        click.echo(f"Search failed: {e}", err=True)
        raise


@cli.command()
def stats():
    """Show database statistics"""
    try:
        vector_store = VectorStore()
        count = vector_store.get_collection_size()
        click.echo(f"Vector DB Documents: {count}")
    except Exception as e:
        click.echo(f"Failed to get stats: {e}", err=True)
        raise


if __name__ == "__main__":
    cli()
