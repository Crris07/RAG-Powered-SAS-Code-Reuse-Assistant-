# Data Preparation Guide

## Adding New SAS Code to Corpus

### Directory Structure
Place all SAS files in: `data/corpus/raw/`

### File Format
- Files must have `.sas` extension
- UTF-8 encoding
- Follow SAS syntax standards
- Include comments documenting purpose

### Example File: `my_analysis.sas`
```sas
/* Purpose: Generate primary efficacy analysis dataset
   Study: XYZ-001
   Date: 2024-05-03
*/

proc sort data=adam.adeff;
  by subjid avisit;
run;

... rest of code ...
```

### Metadata (Optional)
Create `data/corpus/metadata.json` for additional context:

```json
{
  "my_analysis.sas": {
    "study": "XYZ-001",
    "type": "efficacy",
    "procedures": ["PROC SORT", "PROC GLM", "PROC MEANS"],
    "keywords": ["efficacy", "endpoint", "ADAS-cog11"],
    "date_created": "2024-05-03"
  }
}
```

## Ingestion Process

### Step 1: Add Files
Copy your `.sas` files to `data/corpus/raw/`

### Step 2: Run Ingestion
```bash
# Via CLI
python -m src.cli.cli ingest

# Or programmatically
from src.data.corpus_loader import CorpusLoader, CodeChunker
from src.embeddings.embedding_model import EmbeddingGenerator
from src.embeddings.vector_store import VectorStore

loader = CorpusLoader("./data/corpus/raw")
corpus = loader.load_corpus()

chunker = CodeChunker(chunk_size=500)
chunks = []
for doc in corpus:
    chunks.extend(chunker.chunk_code(doc["code"], doc["id"]))

embedding_gen = EmbeddingGenerator()
embeddings = embedding_gen.encode([c["text"] for c in chunks])

store = VectorStore()
store.add_documents(
    ids=[c["id"] for c in chunks],
    documents=[c["text"] for c in chunks],
    metadatas=[{"source": c["code_id"]} for c in chunks]
)
```

### Step 3: Verify Ingestion
```bash
# Check vector DB size
python -m src.cli.cli stats

# Test search
python -m src.cli.cli search --query "demographics table"
```

## Corpus Guidelines

### Good SAS Code
✅ Well-commented
✅ Clear variable names
✅ Modular (discrete tasks)
✅ Documented procedures
✅ Best practices followed

### Not Recommended
❌ Hard to understand
❌ Cryptic variable names
❌ Mixed purposes
❌ Non-standard syntax
❌ Very short snippets (<50 lines)

## Code Organization Tips

### By Analysis Type
- `01_adsl_*.sas` - Subject-level datasets
- `02_ae_*.sas` - Adverse events
- `03_demographics_*.sas` - Demographics tables
- `04_efficacy_*.sas` - Efficacy analysis
- `05_safety_*.sas` - Safety analysis
- `06_pk_*.sas` - Pharmacokinetic analysis

### By Procedure Type
- `demographic_*.sas` - PROC FREQ, PROC MEANS
- `analysis_*.sas` - PROC GLM, PROC LOGISTIC
- `output_*.sas` - PROC REPORT, PROC PRINT
- `data_step_*.sas` - DATA step transformations

## Performance Considerations

### Optimal Chunk Size
- **Current**: 500 tokens
- **For larger files**: Increase to 800-1000
- **For smaller functions**: Decrease to 200-300

### Optimal Overlap
- **Current**: 100 tokens (20% of chunk size)
- Increases retrieval quality at cost of storage

### Corpus Size
- **Tested**: 20-50 files (142 chunks)
- **Recommended minimum**: 10-15 representative examples
- **Maximum**: Limited by disk space (ChromaDB)

## Updating Corpus

### Re-ingest After Updates
```bash
# Clear existing data
python -m src.cli.cli clear-db

# Re-ingest corpus
python -m src.cli.cli ingest
```

### Incremental Updates
For large corpora, add new files without clearing:
```python
# New files in data/corpus/raw/
# Load and chunk new files only
# Add to existing vector DB
```

## Data Privacy & Security

- **Local Storage**: ChromaDB stores data locally in `./data/vector_db/`
- **No Uploads**: Code never sent to external services (except LLM for generation)
- **LLM Privacy**: Configure .env with your own API keys
- **Sensitive Data**: Avoid embedding proprietary/confidential code
