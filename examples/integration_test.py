"""Integration test - End to end"""

import tempfile
from pathlib import Path

from src.data.corpus_loader import CorpusLoader, CodeChunker
from src.embeddings.embedding_model import EmbeddingGenerator
from src.embeddings.vector_store import VectorStore
from src.rag.retriever import CodeRetriever
from src.llm.code_generator import CodeGenerator


def test_end_to_end():
    """Test complete RAG pipeline"""
    
    # Create temporary corpus
    with tempfile.TemporaryDirectory() as tmpdir:
        corpus_path = Path(tmpdir)
        
        # Write sample SAS code
        sample_code = """
        data work.demo;
          set input.demographics;
          
          age_group = put(age, agegroup.);
          if sex = 'M' then gender = 'Male';
          else gender = 'Female';
          
          keep subjid age_group gender;
        run;
        """
        
        sample_file = corpus_path / "sample.sas"
        sample_file.write_text(sample_code)
        
        # Load corpus
        loader = CorpusLoader(corpus_path)
        corpus = loader.load_corpus()
        assert len(corpus) > 0, "Should load corpus"
        
        # Chunk code
        chunker = CodeChunker()
        chunks = []
        for doc in corpus:
            doc_chunks = chunker.chunk_code(doc["code"], doc["id"])
            chunks.extend(doc_chunks)
        assert len(chunks) > 0, "Should create chunks"
        
        # Generate embeddings
        embedding_gen = EmbeddingGenerator()
        texts = [chunk["text"] for chunk in chunks]
        embeddings = embedding_gen.encode(texts)
        assert len(embeddings) > 0, "Should generate embeddings"
        
        # Store in vector DB
        with tempfile.TemporaryDirectory() as db_path:
            vector_store = VectorStore(db_path=db_path)
            ids = [chunk["id"] for chunk in chunks]
            vector_store.add_documents(ids=ids, documents=texts)
            
            # Retrieve
            retriever = CodeRetriever(vector_store)
            query = "demographics by age group"
            results = retriever.retrieve(query, top_k=1)
            
            assert len(results) > 0, "Should retrieve results"
            print(f"Retrieved {len(results)} snippets")


if __name__ == "__main__":
    test_end_to_end()
    print("✓ End-to-end test passed!")
